"""Useful constants that should be available globally."""

import typing_extensions
from typing_extensions import Final

from svglab.utiltypes import Xmlns


SVG_XMLNS: Final[Xmlns] = typing_extensions.get_args(Xmlns)[0]
"""The value of the `xmlns` attribute."""

FLOAT_RELATIVE_TOLERANCE: Final = 1e-9
"""The relative tolerance used for floating-point comparisons."""

FLOAT_ABSOLUTE_TOLERANCE: Final = 1e-9
"""The absolute tolerance used for floating-point comparisons."""
