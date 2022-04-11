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

At some point, I'd like to do a web interface.
