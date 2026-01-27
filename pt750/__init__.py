__version__ = "local"
try:
    from ._version import __version__  # noqa: F401
except ImportError:
    pass

all = ["__version__"]
