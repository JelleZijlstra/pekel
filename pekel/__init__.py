"""Python Pekel implementation."""

__version__ = '0.0'

from . import pypekel
# TODO implement a C-accelerated version
from .pypekel import dump, dumps, load, loads
