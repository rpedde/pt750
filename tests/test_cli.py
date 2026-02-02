"""Test each label type, and ensure expected images."""

import shlex
from pathlib import Path

import pytest
from PIL import Image

import pt750.main as main_module
from pt750.main import get_parser

# given the paths to two images, compare them and determine the
# similarty score between them by the sum of squared differences


def compare_images(path1: str, path2: str) -> float:
    """Compare two images and return a similarity score."""
    img1 = Image.open(path1).convert("RGB")
    img2 = Image.open(path2).convert("RGB")

    if img1.size != img2.size:
        raise ValueError("Images must be the same size for comparison.")

    width, height = img1.size
    ssd = 0  # sum of squared differences

    for x in range(width):
        for y in range(height):
            r1, g1, b1 = img1.getpixel((x, y))
            r2, g2, b2 = img2.getpixel((x, y))
            ssd += (r1 - r2) ** 2 + (g1 - g2) ** 2 + (b1 - b2) ** 2

    if ssd > 0:
        ssd /= width * height * 3  # normalize by number of pixels and channels

    return ssd


# test parameters to test each label type against reference image
test_cases = [
    # label kind, cli args
    (
        "text",
        "--font mono --tape 24mm text --size large --align left 'hello' 'world'",
    ),
    (
        "qr",
        "--tape 9mm --font sans qr --size large --align center https://example.com 'Line 1' 'Line 2'",
    ),
    (
        "wifi",
        "wifi --size small ssid password",
    ),
    (
        "wrap",
        "wrap --length 100 --min-count 5 UPLINK",
    ),
    (
        "flag",
        "--tape 12mm flag --size large UPLINK",
    ),
    (
        "aruco",
        "--tape 6mm --font serif aruco --size large --align center --dictionary DICT_4X4_50 10 'Aruco Marker'",
    ),
]


@pytest.mark.parametrize("kind, args", test_cases, ids=[tc[0] for tc in test_cases])
def test_cli_outputs(tmp_path, kind: str, args: str):
    """Test CLI outputs against reference images."""

    parser = get_parser()

    reference_image = Path(__file__).parent / "reference_images" / f"{kind}_label.png"
    outfile = str(tmp_path / "out.png")

    full_args = ["--outfile", outfile] + shlex.split(args)
    parsed_args = parser.parse_args(full_args)

    # Call the main function with parsed arguments
    main_module.main(parsed_args)

    # Compare generated image with reference image
    score = compare_images(outfile, str(reference_image))

    # Assert that the similarity score is below a threshold
    assert score < 0.001, f"Images for {kind} label differ too much (score: {score})"
