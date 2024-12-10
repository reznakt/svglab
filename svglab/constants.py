from typing import Final

from svglab import types

DEFAULT_PARSER: Final[types.Parser] = "lxml-xml"
"""The default parser to use when parsing SVG documents."""


DEFAULT_XMLNS: Final = "http://www.w3.org/2000/svg"
"""The default XML namespace for SVG documents."""
