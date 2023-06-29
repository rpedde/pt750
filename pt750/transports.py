import base64
import logging
import socket
from urllib.parse import urlparse, urlunparse

import requests
from easysnmp import Session
from PIL import Image

from pt750.models import PrinterStatus, tapes


class LabelPrinter:
    def __init__(self, uri):
        self.uri = uri
        parts = urlparse(self.uri)
        if parts.scheme == "tcp":
            self.transport = TCPTransport(self.uri)
        elif parts.scheme == "file":
            self.transport = USBTransport(self.uri)
        elif parts.scheme in ["http", "https"]:
            self.transport = HTTPTransport(self.uri)
        else:
            raise RuntimeError("cannot find transport")

    def print(self, img: Image):
        raise NotImplementedError

    def status(self):
        raise NotImplementedError


class PT750W(LabelPrinter):
    def print(self, img: Image):
        img = img.transpose(Image.Transpose.ROTATE_90)
        img = img.transpose(Image.Transpose.FLIP_TOP_BOTTOM)

        image_data = bytearray(img.tobytes())

        for idx in range(len(image_data)):
            image_data[idx] = image_data[idx] ^ 0xFF

        bytes = b"\x00" * 100  # reset stream
        bytes += b"\x1B\x40"  # initialize
        bytes += b"\x1B\x69\x4D\x40"  # auto tape cut
        bytes += b"\x1B\x69\x4B\x08"  # no chain printing, low res (128?)
        bytes += b"\x4d\x02"  # compression

        label_width = img.width
        label_height = img.height

        assert label_width == 128

        for line in range(label_height):
            bytes_per_line = label_width // 8
            byte_ofs = bytes_per_line * line
            row_bytes = image_data[byte_ofs : byte_ofs + bytes_per_line]  # noqa: E203

            # raster graphics transfer
            bytes += b"\x47\x11\x00\x0F"  # "compressed" 16 literal bytes
            bytes += row_bytes

        bytes += b"\x1a"  # print and feed

        self.transport.send_bytes(bytes)

    def status(self) -> PrinterStatus:
        return self.transport.get_status()


class Transport:
    def __init__(self, uri):
        self.uri = uri

    def send_bytes(self, bytes: bytes):
        raise NotImplementedError

    def get_status(self) -> PrinterStatus:
        raise NotImplementedError


class USBTransport(Transport):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        parts = urlparse(self.uri)
        self.path = parts.path

    def send_bytes(self, bytes):
        with open(self.path, "wb") as f:
            f.write(bytes)

    def get_status(self) -> PrinterStatus:
        max_attempts = 3

        while max_attempts:
            with open(self.path, "w+b") as f:
                f.write(b"\x00" * 100)  # Invalidate
                f.write(b"\x1B\x69\x53")
                raw_status = f.read(32)

                if len(raw_status) < 32:
                    max_attempts -= 1
                else:
                    break

        if not max_attempts:
            return None

        media = None
        media_mm = int(raw_status[10])
        if media_mm:
            media = f"{media_mm}mm"

        # we need media and ready status
        return PrinterStatus(media=media, ready=True)


class TCPTransport(Transport):
    MEDIA_OID = ".1.3.6.1.2.1.43.8.2.1.12.1.1"
    STATUS_OID = ".1.3.6.1.2.1.43.8.2.1.11.1.1"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        parts = urlparse(self.uri)
        self.host = parts.hostname
        self.port = parts.port if parts.port else 9100

        # I don't believe this is configurable for the printer... I believe it's
        # just plain always on with v2c/public read-only
        self.snmp = Session(hostname=self.host, community="public", version=2)

    def send_bytes(self, bytes):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.host, self.port))
        s.sendall(bytes)
        s.close()

    def get_status(self) -> PrinterStatus:
        media_descriptor = self.snmp.get(self.MEDIA_OID)
        status = self.snmp.get(self.STATUS_OID)

        ready = int(status.value) in [0, 2, 4, 6]

        media = None
        for tape in tapes:
            if media_descriptor.value.startswith(tape):
                media = tape

        return PrinterStatus(media=media, ready=ready)


class HTTPTransport(Transport):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        parts = urlparse(self.uri)
        self.printer = parts.path.rsplit("/", 1)[-1]
        parts = parts._replace(path=parts.path.rsplit("/", 1)[0])
        self.base_uri = urlunparse(parts)

    def get_status(self) -> PrinterStatus:
        rv = requests.get(f"{self.base_uri}/status")
        if not rv.ok:
            logging.error(f"Error getting status for {self.printer}: {rv.status_code}")
            return PrinterStatus(media="24mm", ready=False)

        body = rv.json()
        if self.printer not in body:
            logging.error(f"Remote does not have printer {self.printer}")
            return PrinterStatus(media="24mm", ready=False)

        return PrinterStatus(**body[self.printer])

    def send_bytes(self, bytes):
        request = {
            "count": 1,
            "label": {
                "label_type": "raw",
                "b64_bytes": base64.b64encode(bytes).decode(),
                "printer": self.printer,
                # these are no-op
                "tape": "6mm",
                "fontname": "mono",
            },
        }

        rv = requests.put(f"{self.base_uri}/print", json=request)
        rv.raise_for_status()
