"""Names of all elements.

This module contains the names of all elements in the SVG specification.
It also provides functions to normalize these names to Python identifiers.
"""

import bidict
import typing_extensions
from typing_extensions import Final, Literal, TypeAlias


ElementName: TypeAlias = Literal[
    "a",
    "altGlyph",
    "altGlyphDef",
    "altGlyphItem",
    "animate",
    "animateColor",
    "animateMotion",
    "animateTransform",
    "circle",
    "clipPath",
    "color-profile",
    "cursor",
    "defs",
    "desc",
    "ellipse",
    "feBlend",
    "feColorMatrix",
    "feComponentTransfer",
    "feComposite",
    "feConvolveMatrix",
    "feDiffuseLighting",
    "feDisplacementMap",
    "feDistantLight",
    "feFlood",
    "feFuncA",
    "feFuncB",
    "feFuncG",
    "feFuncR",
    "feGaussianBlur",
    "feImage",
    "feMerge",
    "feMergeNode",
    "feMorphology",
    "feOffset",
    "fePointLight",
    "feSpecularLighting",
    "feSpotLight",
    "feTile",
    "feTurbulence",
    "filter",
    "font-face-format",
    "font-face-name",
    "font-face-src",
    "font-face-uri",
    "font-face",
    "font",
    "foreignObject",
    "g",
    "glyph",
    "glyphRef",
    "hkern",
    "image",
    "line",
    "linearGradient",
    "marker",
    "mask",
    "metadata",
    "missing-glyph",
    "mpath",
    "path",
    "pattern",
    "polygon",
    "polyline",
    "radialGradient",
    "rect",
    "script",
    "set",
    "stop",
    "style",
    "svg",
    "switch",
    "symbol",
    "text",
    "textPath",
    "title",
    "tref",
    "tspan",
    "use",
    "view",
    "vkern",
]
"""Type for all SVG element names."""


ELEMENT_NAMES: Final[frozenset[ElementName]] = frozenset(
    typing_extensions.get_args(ElementName)
)
"""A set of all SVG element names."""


def _normalize_element_name(name: ElementName, /) -> str:
    """Convert an SVG element name to an appropriate class name.

    Args:
        name: The element name to normalize.

    Returns:
        The normalized element name in `PascalCase`.

    Raises:
        ValueError: If the element name cannot be normalized.

    Examples:
    >>> _normalize_element_name("circle")
    'Circle'
    >>> _normalize_element_name("feGaussianBlur")
    'FeGaussianBlur'
    >>> _normalize_element_name("font-face-name")
    'FontFaceName'

    """
    return "".join(part[0].upper() + part[1:] for part in name.split("-"))


ELEMENT_NAME_TO_NORMALIZED: Final = bidict.frozenbidict[ElementName, str](
    {
        element: _normalize_element_name(element)
        for element in ELEMENT_NAMES
    }
)
"""
A bidirectional mapping from SVG element names to normalized Python
identifiers.
"""
