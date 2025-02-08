"""testing web previews actually exercises most of the stack"""

import json
import random
import string

import pytest
from fastapi.testclient import TestClient
from jsf import JSF
from pt750 import models, web


@pytest.fixture
def client():
    client = TestClient(web.app)
    yield client


def a_random_integer(min=-2147483648, max=2147483647, nullable=False):
    if nullable and random.randint(0, 100) < 50:
        return None

    return random.randint(min, max)


def a_random_string(min_len=None, max_len=None, nullable=False):
    if nullable and random.randint(0, 100) < 50:
        return None

    if min_len is None:
        min_len = 20

    if max_len is None:
        max_len = min_len

    str_len = a_random_integer(min=min_len, max=max_len, nullable=False)

    return "".join(random.choice(string.ascii_letters) for _ in range(str_len))


def a_random_model(model, **kwargs):
    faker = JSF(model.model_json_schema())
    proposed = faker.generate()

    if "fontname" in proposed:
        proposed["fontname"] = random.choice(["mono", "sans", "serif"])

    if "size" in proposed:
        proposed["size"] = random.choice(["small", "medium", "large"])

    if "lines" in proposed:
        line_count = random.randint(1, 4)
        proposed["lines"] = [a_random_string() for _ in range(line_count)]

    if "min_count" in proposed:
        proposed["min_count"] = random.randint(4, 8)

    if "padding" in proposed:
        proposed["padding"] = random.randint(0, 10)

    if "label" in proposed and not proposed["label"]:
        proposed["label"] = a_random_string()

    if "qrtext" in proposed and not proposed["qrtext"]:
        proposed["qrtext"] = a_random_string()

    for k, v in kwargs.items():
        if v is not None:
            proposed[k] = v
        else:
            del proposed[k]

    return proposed


label_types = [
    (models.TextLabelRequest,),
    (models.QRLabelRequest,),
    (models.WrapLabelRequest,),
    (models.FlagLabelRequest,),
]

tape_types = [(x, y.printable_height) for x, y in models.tapes.items()]


@pytest.mark.parametrize("tape, height", tape_types)
@pytest.mark.parametrize("label_type", label_types)
def test_label_requests(client, tape, height, label_type):
    lr = a_random_model(label_type[0], tape=tape)

    request = {"label": lr, "count": 1}
    print(json.dumps(request, indent=2))

    rv = client.put("/preview", json=request)
    assert rv.status_code == 200

    res = rv.json()

    assert "height" in res
    assert "width" in res
    assert "preview" in res

    # should load the preview and make sure height is right.
