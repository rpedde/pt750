# pt750

Some simple utilities around printer to a Brother P-Touch PT-P750W.

This works for both the PT750, as well as the PT710B (USB
connected). It may work for other similar Brother printers as
well, although these two printers are the only ones tested.

This project consists of both a command line tool for printing
to network or attached printers, and a web interface for printing
labels as well.

It can print a variety of label types, including:

- text: plain text label with one or more lines of text
- wrap: vertical lines of text suitable for cat5 wrap using flex tape
- qr: qr code with optional text line
- aruco: aruco graphical codes (suitable for Bambu build plates!)
- wifi: qr code for wifi setup (ssid/password)
- flag: suitable for a cable flag

## Docker

A docker container is available to serve the web interface, and is
available at `ghcr.io/rpedde/pt750`. It is tagged based on release
version, as well as a `master` tag that is built on every commit.

The docker container accepts multiple environment variables.

### L_PORT

Change the port the web UI listens on. It listens on port 5000 by default.

### L_PRINTERS

This specifies the printers that are available to the application. Available
printers are specified by friendly name (which is populated in the printer
drop-down in the web UI) and the URI for the associated printer.

There are two styles of printers, TCP/IP connected printers or USB connected
printers, and the associated URIs look like this:

- tcp://192.168.X.X:9100 (for network printers)
- file:///dev/usb/lp0 (for USB connected printers)

This environment setting is required, as otherwise there is no printer
to print to.

As an example, given two available printers, one connected by usb,
and another remote printer (say, in the workshop) at 192.168.1.10,
the appropriate config might be:

```
L_PRINTERS=workshop=tcp://192.168.1.10,local=file:///dev/usb/lp0
```

This would offer two printers ("workshop" and "local") in the web
ui.

### L_FONT_DIRS

This is a comma-separated list of directories that contain
TrueType fonts. Any TrueType font in one of the specified directories
can be set up as a custom font to extend the built-in list of available
fonts.

### L_FONT_MAP

This is a comma-separated list of friendly name/file names of
TrueType fonts to make available in the web UI. These files
must be in one of the font directories specified by the
L_FONT_DIRS environment variable.

The web UI provides some fonts already (mono, sans, and serif
corresponding to DejaVuSansMono, DejaVuSans, and DejaVuSerif).
While these are perfectly functional fonts, there are other
fonts that scale better to lower resolutions.

Of the free fonts I've tested with, I have found Inconsolata
Condensed Bold to be very legible even when printing as small as
two-line on a 3/8" tape.

I have also found PragmataPro to be excellent, but it is not a
free font.

An example of L_FONT_MAP might look like:

```
L_FONT_MAP=mono=Inconsolata_Condensed-Bold.ttf,fira=FiraCode-Regular.ttf
```

This will replace the built-in DejaVuSansMono font (named "mono"
in the web ui drop-down) with Inconsolata, and make FiraCode available
with the "fira" drop-down.

### Running with docker

An example of running the docker container using docker run:

```
docker run --name=labels --rm \
  -p 5000:5000 \
  -e L_PRINTERS=default=tcp://192.168.1.10:9100 \
  ghcr.io/rpedde/pt750:master
```

### Running with docker compose

An example docker-compose file (also in the repo):

```
services:
    pt750:
        container_name: pt750
        image: ghcr.io/rpedde/pt750:master
        environment:
            - L_PRINTERS=default=tcp://192.168.1.10:9100
        ports:
            - 5000:5000
        restart: always
```

## Web Interface

The web interface is served on port 5000 (configurable via the `L_PORT` environment variable). Access it at `http://localhost:5000` when running locally or on the appropriate host when using Docker.

The web UI allows you to:

- Select from available printers
- Choose tape size and font
- Generate and preview labels before printing
- Support all label types: text, wrap, QR codes, WiFi codes, flags, and ArUco markers

## Command Line Tool

The `makelabel` command provides a CLI for generating labels. Basic usage:

```
usage: makelabel [-h] [--outfile OUTFILE | --printer PRINTER] [--version] [--tape {24mm,12mm,9mm,6mm}] [--font {mono,sans,serif}] {text,qr,wifi,wrap,flag,aruco} ...

make a label

positional arguments:
  {text,qr,wifi,wrap,flag,aruco}
                        kind of label

options:
  -h, --help            show this help message and exit
  --outfile OUTFILE     file to write output image to
  --printer PRINTER     printer URI to print to
  --version             show program's version number and exit
  --tape {24mm,12mm,9mm,6mm}
                        tape size
  --font {mono,sans,serif}
                        font type

```

Each label type has its own options. Use `makelabel <type> --help` to see the options for a specific type.

### Examples

Text label:

```
makelabel --tape 24mm text --align left --size large "Hello" "World"
```

QR code:

```
makelabel qr "https://example.com" --size large
```

WiFi code:

```
makelabel wifi "MyNetwork" "SecurePass123"
```

Cable wrap:

```
makelabel wrap "Uplink"
```

Cable flag:

```
makelabel flag --padding 96 "Flag Label"
```

ArUco marker:

```
makelabel aruco 0 'Cool plate supertack'
```

To send directly to a printer instead of saving to a file, use the `--printer` option with the printer URI.

## Changes

- **0.3.0** Add ArUco markers
- **0.2.1** Fix qr code label types in docker container
- **0.2.0** Add web interface
- **0.1.0** Initial release

## Notes

Raster Documentation: https://download.brother.com/welcome/docp100064/cv_pte550wp750wp710bt_eng_raster_102.pdf
