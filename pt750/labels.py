import cv2
from typing import Optional

from PIL import Image, ImageDraw

from pt750 import draw, models


class Label:
    def __init__(self):
        self.img = None

    @property
    def image(self):
        return self.img

    @property
    def bytes(self):
        assert self.img
        return self.img.to_bytes()

    def save(self, filename: str):
        assert self.img
        self.img.save(filename)


class TextLabel(Label):
    def __init__(
        self,
        height: int,
        fontname: str,
        lines: list[str],
        align: models.HAlignment = models.HAlignment.left,
        size: str = "large",
    ):
        self.height = height
        self.fontname = fontname
        self.lines = lines
        self.align = align
        self.size = size

        if not all(x for x in lines):
            raise models.ParameterError("Empty lines not allowed")

        self.generate()

    def generate(self):
        img = draw.horiz_text_block(
            self.height, self.fontname, self.size, self.lines, alignment=self.align
        )
        self.img = img


class QRLabel(Label):
    def __init__(
        self,
        height: int,
        fontname: str,
        qrtext: str,
        size: str = "large",
        padding: int = 10,
        align: models.HAlignment = models.HAlignment.left,
        lines: Optional[list[str]] = None,
    ):
        self.height = height
        self.fontname = fontname
        self.qrtext = qrtext
        self.size = size
        self.padding = padding
        self.align = align
        self.lines = lines
        if self.lines is None:
            self.lines = []

        if lines and not all(x for x in lines):
            raise models.ParameterError("Empty lines not allowed")

        self.generate()

    def generate(self):
        qr_img = draw.qr_code(self.height, self.qrtext)
        if self.lines and all(x for x in self.lines):
            text_img = draw.horiz_text_block(
                self.height, self.fontname, self.size, self.lines, self.align
            )
            width = qr_img.width + text_img.width + self.padding
            img = Image.new(mode="1", size=(width, self.height), color=1)
            img.paste(qr_img)
            img.paste(text_img, (qr_img.width + self.padding, 0))
        else:
            img = qr_img

        self.img = img


class ArucoLabel(Label):
    def __init__(
        self,
        height: int,
        fontname: str,
        dictionary: str = "DICT_4X4_100",
        id: int = 0,
        size: str = "large",
        padding: int = 10,
        align: models.HAlignment = models.HAlignment.left,
        lines: Optional[list[str]] = None,
    ):
        self.height = height
        self.fontname = fontname
        self.dictionary = dictionary
        self.id = id
        self.size = size
        self.padding = padding
        self.align = align
        self.lines = lines
        if self.lines is None:
            self.lines = []

        if lines and not all(x for x in lines):
            raise models.ParameterError("Empty lines not allowed")

        self.generate()

    def generate(self):
        dictionary_idx = getattr(models.ArucoDictionary, self.dictionary, 0)
        aruco_dict = cv2.aruco.getPredefinedDictionary(dictionary_idx)
        aruco_cv_img = cv2.aruco.generateImageMarker(aruco_dict, self.id, self.height)

        color_coverted = cv2.cvtColor(aruco_cv_img, cv2.COLOR_BGR2RGB)
        aruco_img = Image.fromarray(color_coverted)

        if self.lines and all(x for x in self.lines):
            text_img = draw.horiz_text_block(
                self.height, self.fontname, self.size, self.lines, self.align
            )
            width = aruco_img.width + text_img.width + self.padding
            img = Image.new(mode="1", size=(width, self.height), color=1)
            img.paste(aruco_img)
            img.paste(text_img, (aruco_img.width + self.padding, 0))
        else:
            img = aruco_img

        self.img = img


class WrapLabel(Label):
    def __init__(
        self,
        height: int,
        fontname: str,
        label: str,
        length: int = 128,
        min_count: int = 7,
    ):
        self.height = height
        self.fontname = fontname
        self.label = label
        self.length = length
        self.min_count = min_count

        if not label:
            raise models.ParameterError("label is required")

        self.generate()

    def generate(self):
        img = draw.vertical_text_block(
            self.height,
            self.length,
            self.fontname,
            self.label,
            min_count=self.min_count,
        )
        self.img = img


class FlagLabel(Label):
    def __init__(self, height, fontname, label, size="large", padding=96):
        self.height = height
        self.fontname = fontname
        self.label = label
        self.size = size
        self.padding = padding

        if not label:
            raise models.ParameterError("label is required")

        self.generate()

    def generate(self):
        text_img = draw.horiz_text_block(
            self.height, self.fontname, self.size, lines=[self.label]
        )

        width = (text_img.width * 2) + self.padding
        img = Image.new(mode="1", size=(width, self.height), color=1)
        img.paste(text_img)
        img.paste(text_img, (text_img.width + self.padding, 0))
        img_draw = ImageDraw.Draw(img)
        middle = text_img.width + (self.padding // 2)
        img_draw.line(((middle, 0), (middle, self.height)), width=1)

        self.img = img
