#!/usr/bin/env python3

import argparse

from PIL import Image

from pt750 import labels, models, transports


def get_parser():
    parser = argparse.ArgumentParser(description="make a label")

    parser.add_argument("--outfile", default="out.png")
    parser.add_argument("--printer")
    parser.add_argument("--tape", default="24mm")
    parser.add_argument("--font", default="mono")

    subparsers = parser.add_subparsers(help="kind of label", dest="kind")
    subparsers.required = True

    text_parser = subparsers.add_parser("text")
    text_parser.add_argument("--align", default="left")
    text_parser.add_argument("--size", default="large")
    text_parser.add_argument("line", nargs="+")

    qr_parser = subparsers.add_parser("qr")
    qr_parser.add_argument("qrtext")
    qr_parser.add_argument("--align", default="left")
    qr_parser.add_argument("--padding", type=int, default=10)
    qr_parser.add_argument("--size", default="large")
    qr_parser.add_argument("line", nargs="*")

    wifi_parser = subparsers.add_parser("wifi")
    wifi_parser.set_defaults(align="left")
    wifi_parser.set_defaults(padding=10)
    wifi_parser.add_argument("--size", default="large")
    wifi_parser.add_argument("ssid")
    wifi_parser.add_argument("password")

    wrap_parser = subparsers.add_parser("wrap")
    wrap_parser.add_argument("--length", type=int, default=128)
    wrap_parser.add_argument("--min-count", type=int, default=7)
    wrap_parser.add_argument("label")

    flag_parser = subparsers.add_parser("flag")
    flag_parser.add_argument("--padding", type=int, default=96)
    flag_parser.add_argument("--size", default="large")
    flag_parser.add_argument("label")

    return parser


def main():
    args = get_parser().parse_args()
    height = models.tapes[args.tape]["printable_height"]
    final_ofs = models.tapes[args.tape]["offset"]

    img = None

    if args.kind == "text":
        align = models.HAlignment(args.align)
        label = labels.TextLabel(
            height, args.font, args.line, align=align, size=args.size
        )

        img = label.image

    elif args.kind == "qr":
        align = models.HAlignment(args.align)

        label = labels.QRLabel(
            height,
            args.font,
            args.qrtext,
            size=args.size,
            padding=args.padding,
            align=align,
            lines=args.line,
        )
        img = label.image
    elif args.kind == "ssid":
        qrtext = f"WIFI:T:WPA;S:{args.ssid};P:{args.password};;"
        lines = [f"SSID: {args.ssid}", f"PASS: {args.password}"]

        label = labels.QRLabel(
            height, args.font, qrtext, size=args.size, padding=args.padding, lines=lines
        )
        img = label.image
    elif args.kind == "wrap":
        label = labels.WrapLabel(
            height, args.font, args.label, length=args.length, min_count=args.min_count
        )
        img = label.image

    elif args.kind == "flag":
        label = labels.FlagLabel(
            height, args.font, args.label, size=args.size, padding=args.padding
        )
        img = label.image
    else:
        raise RuntimeError("invalid label kind")

    final_width = img.width
    out_img = Image.new(mode="1", size=(final_width, 128), color=1)
    out_img.paste(img, (0, final_ofs))

    if args.printer:
        print("sending to printer")
        printer = transports.PT750W(args.printer)
        printer.print(out_img)
    else:
        print(f"saving to {args.outfile}")
        out_img.save(args.outfile)


if __name__ == "__main__":
    main()
