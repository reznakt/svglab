import keyword
import typing
from typing import Final, Literal, TypeAlias

import bidict

__all__ = [
    "ATTRIBUTE_NAMES",
    "ATTR_TO_NORMALIZED",
    "AttributeName",
    "normalize_attr_name",
]


AttributeName: TypeAlias = Literal[
    "alignment-baseline",
    "attributeName",
    "attributeType",
    "baseline-shift",
    "begin",
    "by",
    "calcMode",
    "class",
    "clip-path",
    "clip-rule",
    "clip",
    "color-interpolation-filters",
    "color-interpolation",
    "color-profile",
    "color-rendering",
    "color",
    "cursor",
    "cx",
    "cy",
    "d",
    "direction",
    "display",
    "dominant-baseline",
    "dur",
    "dx",
    "dy",
    "enable-background",
    "end",
    "externalResourcesRequired",
    "fill-opacity",
    "fill-rule",
    "fill",
    "filter",
    "filterUnits",
    "flood-color",
    "flood-opacity",
    "font-family",
    "font-size-adjust",
    "font-size",
    "font-stretch",
    "font-style",
    "font-variant",
    "font-weight",
    "from",
    "glyph-orientation-horizontal",
    "glyph-orientation-vertical",
    "gradientTransform",
    "gradientUnits",
    "height",
    "href",
    "id",
    "image-rendering",
    "in",
    "in2",
    "kerning",
    "keySplines",
    "keyTimes",
    "lengthAdjust",
    "letter-spacing",
    "lighting-color",
    "marker-end",
    "marker-mid",
    "marker-start",
    "mask",
    "onactivate",
    "onclick",
    "onfocusin",
    "onfocusout",
    "onload",
    "onmousedown",
    "onmousemove",
    "onmouseout",
    "onmouseover",
    "onmouseup",
    "onresize",
    "onscroll",
    "onunload",
    "onzoom",
    "opacity",
    "overflow",
    "pathLength",
    "patternContentUnits",
    "patternTransform",
    "patternUnits",
    "pointer-events",
    "points",
    "preserveAspectRatio",
    "primitiveUnits",
    "r",
    "repeatCount",
    "repeatDur",
    "requiredExtensions",
    "result",
    "role",
    "rotate",
    "rx",
    "ry",
    "shape-rendering",
    "spreadMethod",
    "stop-color",
    "stop-opacity",
    "stroke-dasharray",
    "stroke-dashoffset",
    "stroke-linecap",
    "stroke-linejoin",
    "stroke-miterlimit",
    "stroke-opacity",
    "stroke-width",
    "stroke",
    "style",
    "systemLanguage",
    "tabindex",
    "text-anchor",
    "text-decoration",
    "text-rendering",
    "textLength",
    "to",
    "transform",
    "unicode-bidi",
    "values",
    "viewBox",
    "visibility",
    "width",
    "word-spacing",
    "writing-mode",
    "x",
    "x1",
    "x2",
    "xmlns",
    "y",
    "y1",
    "y2",
    "zoomAndPan",
]
""" Type for all SVG attribute names. """


def is_valid_identifier(name: str) -> bool:
    """Check if a string is a valid Python identifier and not a reserved keyword.

    Args:
        name: The string to check.

    Returns:
        `True` if the string is a valid Python identifier, `False` otherwise.

    Examples:
        >>> is_valid_identifier("foo")
        True
        >>> is_valid_identifier("class")
        False
        >>> is_valid_identifier("123")
        False
        >>> is_valid_identifier("for")
        False

    """
    return name.isidentifier() and not keyword.iskeyword(name)


def normalize_attr_name(name: AttributeName) -> str:
    """Convert an SVG attribute name to a valid Python identifier.

    Args:
        name: The attribute name to normalize.

    Returns:
        The normalized attribute name.

    Raises:
        ValueError: If the attribute name cannot be normalized.

    Examples:
        >>> normalize_attr_name("width")
        'width'
        >>> normalize_attr_name("stroke-width")
        'stroke_width'
        >>> normalize_attr_name("xlink:href")
        'xlink_href'
        >>> normalize_attr_name("class")
        'class_'

    """
    normalized: str = name

    substitutions = {
        "-": "_",
        ":": "_",
    }

    for old, new in substitutions.items():
        normalized = normalized.replace(old, new)

    if not is_valid_identifier(normalized):
        normalized = f"{normalized}_"

    if not is_valid_identifier(normalized):
        msg = f"Cannot normalize attribute name: {name!r}"
        raise ValueError(msg)

    return normalized


ATTRIBUTE_NAMES: Final[frozenset[AttributeName]] = frozenset(
    typing.get_args(AttributeName)
)
"""A set of all valid SVG attribute names."""


ATTR_TO_NORMALIZED: Final = bidict.frozenbidict(
    {attr: normalize_attr_name(attr) for attr in ATTRIBUTE_NAMES}
)
"""A bidirectional mapping of SVG attribute names to normalized Python identifiers."""
