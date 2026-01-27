try:
    from ._version import __version__
except ImportError:
    # local dev install without editable install (i.e. not uv synced)
    __version__ = "local"

__all__ = ["__version__"]
