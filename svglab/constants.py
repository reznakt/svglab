import typing
from typing import Final

from svglab import types

DEFAULT_PARSER: Final[types.Parser] = "lxml-xml"
"""The default parser to use when parsing SVG documents."""

DEFAULT_INDENT: Final = 2
"""The default number of spaces to use for indentation. """

DEFAULT_XMLNS: Final = "http://www.w3.org/2000/svg"
"""The default XML namespace for SVG documents."""

ATTRIBUTE_NAMES: Final[frozenset[types.AttributeName]] = frozenset(
    typing.get_args(types.AttributeName)
)
"""A set of all valid SVG attribute names."""
