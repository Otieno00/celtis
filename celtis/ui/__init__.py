"""Reusable tkinter building blocks: widgets, styles, BaseTab."""

from .widgets import (
    entry, calc_entry, hdr, lbl, section, section_pack,
    set_val, get_float, scrolled_frame,
    validate_positive, validate_non_empty, validate_range,
)
from .styles import install_styles
from .base_tab import BaseTab

__all__ = [
    "entry", "calc_entry", "hdr", "lbl", "section", "section_pack",
    "set_val", "get_float", "scrolled_frame",
    "validate_positive", "validate_non_empty", "validate_range",
    "install_styles", "BaseTab",
]