import typing_extensions
from typing_extensions import Final

from svglab import utiltypes


SVG_XMLNS: Final[utiltypes.Xmlns] = typing_extensions.get_args(
    utiltypes.Xmlns
)[0]
"""The value of the `xmlns` attribute."""

FLOAT_RELATIVE_TOLERANCE: Final = 1e-9
"""The relative tolerance used for floating-point comparisons."""

FLOAT_ABSOLUTE_TOLERANCE: Final = 1e-12
"""The absolute tolerance used for floating-point comparisons."""
