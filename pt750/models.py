from enum import Enum, IntEnum
from typing import Any, Literal, Union

import cv2
from pydantic import BaseModel, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


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


class ArucoDictionary(IntEnum):
    DICT_4X4_50 = cv2.aruco.DICT_4X4_50
    DICT_4X4_100 = cv2.aruco.DICT_4X4_100
    DICT_4X4_250 = cv2.aruco.DICT_4X4_250
    DICT_4X4_1000 = cv2.aruco.DICT_4X4_1000
    DICT_5X5_50 = cv2.aruco.DICT_5X5_50
    DICT_5X5_100 = cv2.aruco.DICT_5X5_100
    DICT_5X5_250 = cv2.aruco.DICT_5X5_250
    DICT_5X5_1000 = cv2.aruco.DICT_5X5_1000
    DICT_6X6_50 = cv2.aruco.DICT_6X6_50
    DICT_6X6_100 = cv2.aruco.DICT_6X6_100
    DICT_6X6_250 = cv2.aruco.DICT_6X6_250
    DICT_6X6_1000 = cv2.aruco.DICT_6X6_1000
    DICT_7X7_50 = cv2.aruco.DICT_7X7_50
    DICT_7X7_100 = cv2.aruco.DICT_7X7_100
    DICT_7X7_250 = cv2.aruco.DICT_7X7_250
    DICT_7X7_1000 = cv2.aruco.DICT_7X7_1000
    DICT_ARUCO_ORIGINAL = cv2.aruco.DICT_ARUCO_ORIGINAL
    DICT_APRILTAG_16h5 = cv2.aruco.DICT_APRILTAG_16h5
    DICT_APRILTAG_25h9 = cv2.aruco.DICT_APRILTAG_25h9
    DICT_APRILTAG_36h10 = cv2.aruco.DICT_APRILTAG_36h10
    DICT_APRILTAG_36h11 = cv2.aruco.DICT_APRILTAG_36h11


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


class ArucoLabelRequest(BaseLabel):
    label_type: Literal["aruco"]

    align: HAlignment
    padding: int = 10
    size: str = "large"
    dictionary: str
    id: int
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
        ArucoLabelRequest,
        RawLabelRequest,
        TextLabelRequest,
        WrapLabelRequest,
    ] = Field(discriminator="label_type")
    count: int = 1


class PrinterStatus(BaseModel):
    media: Tapes | None = None
    ready: bool


class Settings(BaseSettings):
    printers: Union[str, dict[str, str]] = "default=file:///dev/null"
    font_dirs: Union[None, str, list[str]] = None
    font_map: Union[str, dict[str, str]] = ""
    port: int = 5000

    model_config = SettingsConfigDict(env_prefix="l_")

    @field_validator("font_dirs", mode="before")
    @classmethod
    def comma_separated(cls, value: Any) -> Any:
        if value is None:
            return None

        return list(map(str.strip, value.split(",")))

    @field_validator("printers", "font_map", mode="before")
    @classmethod
    def kvpairs(cls, value: Any) -> Any:
        if value:
            return dict([x.split("=") for x in value.split(",")])
        return {}


settings = Settings()
