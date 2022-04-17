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
is L_PRINTERS, a comma-separated list of printer uris, like:

`tcp://some.printer:9100,tcp://someother.printer:9100`

## Changes

0.2.0: Add web interface

0.1.0: Initial release
