"""Defines package version.  Parsed by setup.py and imported by __init__.py."""

import importlib.metadata

try:
    __version__ = importlib.metadata.version("imgcorrect")
except importlib.metadata.PackageNotFoundError:
    __version__ = "unknown"
