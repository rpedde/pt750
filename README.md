# pt750

Some simple utilities around printer to a Brother P-Touch PT-P750W.

Currently, this only works over tcp, but with small effort could work
against usb connected devices as well.

This includes a command line for printing some pre-formatted label
types, including:

- text: plain text label with one or more lines of text
- wrap: vertical lines of text suitable for cat5 wrap using flex tape
- qr: qr code with optional text line
- wifi: qr code for wifi setup (ssid/password)
- flag: suitable for a cable flag

This also includes a web interface for printing labels, as well as
a docker container set up for label printing.

The only necessary environment variable to set on the docker container
is L_PRINTERS, a comma-separated list of key=value pairs that map from
friendly name to printer uri:

`L_PRINTERS=office=tcp://some.printer:9100,kitchen=tcp://someother.printer:9100`

which will set up two printers, "office" and "kitchen", pointed to
two different ip printers.

Additionally, the default fonts (mono, sans, and serif) are set
to DejaVuSansMono, DejaVuSans and DejaVuSerif. While these are
perfectly functional fonts, there are fonts that scale better
to lower resolutions.

You can override or add fonts by putting the ttf fonts in a
directory and adding that directory to the font path (a
comma separated list of directories):

`L_FONT_DIRS=/fonts,/otherfonts`

and then mapping friendly names to individual font files,
as such:

`L_FONT_MAP=pragmata=PragmataPro_Mono_R_0828.ttf,consolas=consola.ttf`

## Changes

0.2.0: Add web interface

0.1.0: Initial release
