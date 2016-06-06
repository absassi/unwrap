# -*- coding: utf-8 -*-
import pkg_resources

from .core import Paragraph, Joiner

try:
    __version__ = pkg_resources.get_distribution(__name__).version
except:
    __version__ = 'unknown'

__author__ = "André Berti Sassi"
__copyright__ = "André Berti Sassi"
__license__ = "MIT"
__description__ = "A tool for unwrapping paragraph lines."

__all__ = ["Paragraph", "Joiner"]
