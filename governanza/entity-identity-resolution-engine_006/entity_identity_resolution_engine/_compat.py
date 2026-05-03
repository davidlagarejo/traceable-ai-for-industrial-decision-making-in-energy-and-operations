from __future__ import annotations

from dataclasses import dataclass as _dataclass
import sys


def dataclass(*args, **kwargs):
    if sys.version_info < (3, 10):
        kwargs.pop("slots", None)
    return _dataclass(*args, **kwargs)
