import socket
from urllib.parse import urlparse

from PIL import Image


class LabelPrinter:
    def __init__(self, uri):
        self.uri = uri
        parts = urlparse(self.uri)
        if parts.scheme == 'tcp':
            self.transport = TCPTransport(self.uri)
        else:
            raise RuntimeError('cannot find transport')


class PT750W(LabelPrinter):
    def print(self, img: Image):
        img = img.transpose(Image.Transpose.ROTATE_90)
        img = img.transpose(Image.Transpose.FLIP_TOP_BOTTOM)

        image_data = bytearray(img.tobytes())

        for idx in range(len(image_data)):
            image_data[idx] = image_data[idx] ^ 0xff

        bytes = b'\x00' * 100  # reset stream
        bytes += b'\x1B\x40'  # inittialize
        bytes += b'\x1B\x69\x4D\x40'  # auto tape cut
        bytes += b'\x1B\x69\x4B\x08'  # no chain printing, low res (128?)
        bytes += b'\x4d\x02'  # compression

        label_width = img.width
        label_height = img.height

        assert label_width == 128

        for line in range(label_height):
            bytes_per_line = label_width // 8
            byte_ofs = bytes_per_line * line
            row_bytes = image_data[byte_ofs:byte_ofs + bytes_per_line]

            # raster graphics transfer
            bytes += b'\x47\x11\x00\x0F'  # "compressed" 16 literal bytes
            bytes += row_bytes

        bytes += b'\x1a'  # print and feed

        self.transport.send_bytes(bytes)


class Transport:
    def __init__(self, uri):
        self.uri = uri


class TCPTransport(Transport):
    def send_bytes(self, bytes):
        parts = urlparse(self.uri)

        hostname = parts.hostname
        port = parts.port if parts.port else 9100

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((hostname, port))
        s.sendall(bytes)
        s.close()
