from enum import Enum
from typing import Literal, Union

from pydantic import BaseModel, BaseSettings, validator


class ParameterError(Exception):
    pass


class Tape(BaseModel):
    size: str
    printable_height: int
    offset: int


class Tapes(Enum):
    size_24mm = "24mm"
    size_12mm = "12mm"
    size_9mm = "9mm"
    size_6mm = "6mm"


tapes = {
    "24mm": Tape(size="24mm", printable_height=128, offset=0),
    "12mm": Tape(size="12mm", printable_height=64, offset=32),
    "9mm": Tape(size="9mm", printable_height=48, offset=40),
    "6mm": Tape(size="6mm", printable_height=32, offset=48),
}


class HAlignment(Enum):
    left = "left"
    right = "right"
    center = "center"


class VAlignment(Enum):
    center = "center"
    even = "even"


class BaseLabel(BaseModel):
    printer: str
    tape: Tapes
    fontname: str = "mono"


# request models
class TextLabelRequest(BaseLabel):
    label_type: Literal["text"]

    align: HAlignment
    size: str = "large"
    lines: list[str]


class RawLabelRequest(BaseLabel):
    label_type: Literal["raw"]
    b64_bytes: str


class QRLabelRequest(BaseLabel):
    label_type: Literal["qr"]

    align: HAlignment
    padding: int = 10
    size: str = "large"
    qrtext: str
    lines: list[str] = []


class WrapLabelRequest(BaseLabel):
    label_type: Literal["wrap"]

    length: int = 128
    min_count: int = 7
    label: str


class FlagLabelRequest(BaseLabel):
    label_type: Literal["flag"]

    padding: int = 96
    size: str = "large"
    label: str


class LabelRequest(BaseModel):
    label: Union[
        FlagLabelRequest,
        QRLabelRequest,
        RawLabelRequest,
        TextLabelRequest,
        WrapLabelRequest,
    ]
    count: int = 1


class PrinterStatus(BaseModel):
    media: Tapes = None
    ready: bool


class Settings(BaseSettings):
    printers: Union[str, dict[str, str]] = "default=file:///dev/null"
    font_dirs: Union[None, str, list[str]] = None
    font_map: Union[str, dict[str, str]] = ""
    port: int = 5000

    @validator("font_dirs")
    def comma_separated(cls, v):
        if v is None:
            return None

        return list(map(str.strip, v.split(",")))

    @validator("printers", "font_map")
    def kvpairs(cls, v):
        if v:
            return dict([x.split("=") for x in v.split(",")])
        return {}

    class Config:
        env_prefix = "l_"


settings = Settings()
