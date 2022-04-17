#!/usr/bin/env python

import base64
import io
import os

import uvicorn
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import PlainTextResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from PIL import Image

from pt750 import draw, labels, models, transports

app = FastAPI()
static_dir = os.path.join(os.path.dirname(__file__), "static")
template_dir = os.path.join(os.path.dirname(__file__), "templates")

app.mount("/static", StaticFiles(directory=static_dir), name="static")
templates = Jinja2Templates(directory=template_dir)

settings = models.Settings()


def _image_for_request(request: models.LabelRequest):
    label_info = request.dict()["label"]

    label_type = label_info.pop("label_type")

    _ = label_info.pop("printer")
    tape = label_info.pop("tape").value

    height = models.tapes[tape].printable_height

    if label_type == "text":
        img = labels.TextLabel(height=height, **label_info).image
    elif label_type == "qr":
        img = labels.QRLabel(height=height, **label_info).image
    elif label_type == "wrap":
        img = labels.WrapLabel(height=height, **label_info).image
    elif label_type == "flag":
        img = labels.FlagLabel(height=height, **label_info).image

    return img


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return PlainTextResponse(str(exc), status_code=400)


@app.exception_handler(models.ParameterError)
async def parameter_exception_handler(request: Request, exc: models.ParameterError):
    return PlainTextResponse(str(exc), status_code=400)


@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/config")
async def config():
    print(settings)

    response = {
        "tapes": list(models.tapes.keys()),
        "printers": list(settings.printers),
        "fonts": list(draw.font_map.keys()),
    }

    return response


@app.put("/print")
async def print(label_request: models.LabelRequest):
    img = _image_for_request(label_request)

    final_width = img.width

    tape = label_request.label.tape.value
    final_ofs = models.tapes[tape].offset

    out_img = Image.new(mode="1", size=(final_width, 128), color=1)
    out_img.paste(img, (0, final_ofs))

    printer = transports.PT750W(label_request.label.printer)
    printer.print(out_img)


@app.put("/preview")
async def preview(label_request: models.LabelRequest, max_width: int = 0):
    img = _image_for_request(label_request)

    label_height = f"{(img.height / 128):0.1f}"
    label_width = f"{(img.width / 128):0.1f}"

    if max_width != 0 and max_width < img.width:
        resize_ratio = max_width / img.width
        new_height = img.height * resize_ratio
        img = img.resize((max_width, int(new_height)))

    bytes = io.BytesIO()
    img.save(bytes, format="PNG")

    bytes.seek(0)
    return {
        "preview": base64.b64encode(bytes.read()),
        "width": label_width,
        "height": label_height,
    }


if __name__ == "__main__":
    uvicorn.run("pt750.web:app", host="0.0.0.0", port=5000, reload=True)
