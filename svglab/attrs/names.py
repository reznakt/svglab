import keyword

import bidict
import typing_extensions
from typing_extensions import Final, Literal, TypeAlias


AttributeName: TypeAlias = Literal[
    "accent-height",
    "accumulate",
    "additive",
    "alignment-baseline",
    "alphabetic",
    "amplitude",
    "arabic-form",
    "ascent",
    "attributeName",
    "attributeType",
    "azimuth",
    "baseFrequency",
    "baseline-shift",
    "baseProfile",
    "bbox",
    "begin",
    "bias",
    "by",
    "calcMode",
    "cap-height",
    "class",
    "clip-path",
    "clip-rule",
    "clip",
    "clipPathUnits",
    "color-interpolation-filters",
    "color-interpolation",
    "color-profile",
    "color-rendering",
    "color",
    "contentScriptType",
    "contentStyleType",
    "cursor",
    "cx",
    "cy",
    "d",
    "descent",
    "diffuseConstant",
    "direction",
    "display",
    "divisor",
    "dominant-baseline",
    "dur",
    "dx",
    "dy",
    "edgeMode",
    "elevation",
    "enable-background",
    "end",
    "exponent",
    "externalResourcesRequired",
    "fill-opacity",
    "fill-rule",
    "fill",
    "filter",
    "filterRes",
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
    "format",
    "fr",
    "from",
    "fx",
    "fy",
    "g1",
    "g2",
    "glyph-name",
    "glyph-orientation-horizontal",
    "glyph-orientation-vertical",
    "glyphRef",
    "gradientTransform",
    "gradientUnits",
    "hanging",
    "height",
    "horiz-adv-x",
    "horiz-origin-x",
    "horiz-origin-y",
    "href",
    "id",
    "ideographic",
    "image-rendering",
    "in",
    "in2",
    "intercept",
    "k",
    "k1",
    "k2",
    "k3",
    "k4",
    "kernelMatrix",
    "kernelUnitLength",
    "kerning",
    "keyPoints",
    "keySplines",
    "keyTimes",
    "lang",
    "lengthAdjust",
    "letter-spacing",
    "lighting-color",
    "limitingConeAngle",
    "local",
    "marker-end",
    "marker-mid",
    "marker-start",
    "markerHeight",
    "markerUnits",
    "markerWidth",
    "mask",
    "maskContentUnits",
    "maskUnits",
    "mathematical",
    "max",
    "media",
    "method",
    "min",
    "mode",
    "name",
    "numOctaves",
    "offset",
    "opacity",
    "operator",
    "order",
    "orient",
    "orientation",
    "origin",
    "overflow",
    "overline-position",
    "overline-thickness",
    "paint-order",
    "panose-1",
    "path",
    "pathLength",
    "patternContentUnits",
    "patternTransform",
    "patternUnits",
    "pointer-events",
    "points",
    "pointsAtX",
    "pointsAtY",
    "pointsAtZ",
    "preserveAlpha",
    "preserveAspectRatio",
    "primitiveUnits",
    "r",
    "radius",
    "refX",
    "refY",
    "rendering-intent",
    "repeatCount",
    "repeatDur",
    "requiredExtensions",
    "requiredFeatures",
    "restart",
    "result",
    "rotate",
    "rx",
    "ry",
    "scale",
    "seed",
    "shape-rendering",
    "slope",
    "spacing",
    "specularConstant",
    "specularExponent",
    "spreadMethod",
    "startOffset",
    "stdDeviation",
    "stemh",
    "stemv",
    "stitchTiles",
    "stop-color",
    "stop-opacity",
    "strikethrough-position",
    "strikethrough-thickness",
    "string",
    "stroke-dasharray",
    "stroke-dashoffset",
    "stroke-linecap",
    "stroke-linejoin",
    "stroke-miterlimit",
    "stroke-opacity",
    "stroke-width",
    "stroke",
    "style",
    "surfaceScale",
    "systemLanguage",
    "tableValues",
    "target",
    "targetX",
    "targetY",
    "text-align-all",
    "text-align-last",
    "text-align",
    "text-anchor",
    "text-decoration",
    "text-indent",
    "text-rendering",
    "textLength",
    "title",
    "to",
    "transform-box",
    "transform-origin",
    "transform",
    "type",
    "u1",
    "u2",
    "underline-position",
    "underline-thickness",
    "unicode-bidi",
    "unicode-range",
    "unicode",
    "units-per-em",
    "v-alphabetic",
    "v-hanging",
    "v-ideographic",
    "v-mathematical",
    "values",
    "vector-offset",
    "version",
    "vert-adv-y",
    "vert-origin-x",
    "vert-origin-y",
    "viewBox",
    "viewTarget",
    "visibility",
    "white-space",
    "width",
    "widths",
    "word-spacing",
    "writing-mode",
    "x-height",
    "x",
    "x1",
    "x2",
    "xChannelSelector",
    "xlink:actuate",
    "xlink:arcrole",
    "xlink:href",
    "xlink:role",
    "xlink:show",
    "xlink:title",
    "xlink:type",
    "xml:base",
    "xml:lang",
    "xml:space",
    "xmlns",
    "y",
    "y1",
    "y2",
    "yChannelSelector",
    "z-index",
    "z",
    "zoomAndPan",
]
""" Type for all SVG attribute names. """


def _is_valid_identifier(name: str) -> bool:
    """Check if a string is a valid identifier and not a reserved keyword.

    Args:
        name: The string to check.

    Returns:
        `True` if the string is a valid Python identifier, `False` otherwise.

    Examples:
        >>> _is_valid_identifier("foo")
        True
        >>> _is_valid_identifier("class")
        False
        >>> _is_valid_identifier("123")
        False
        >>> _is_valid_identifier("for")
        False

    """
    return name.isidentifier() and not keyword.iskeyword(name)


def _normalize_attr_name(name: AttributeName) -> str:
    """Convert an SVG attribute name to a valid Python identifier.

    Args:
        name: The attribute name to normalize.

    Returns:
        The normalized attribute name.

    Raises:
        ValueError: If the attribute name cannot be normalized.

    Examples:
        >>> _normalize_attr_name("width")
        'width'
        >>> _normalize_attr_name("stroke-width")
        'stroke_width'
        >>> _normalize_attr_name("xlink:href")
        'xlink_href'
        >>> _normalize_attr_name("class")
        'class_'

    """
    normalized: str = name

    substitutions = {"-": "_", ":": "_"}

    for old, new in substitutions.items():
        normalized = normalized.replace(old, new)

    if not _is_valid_identifier(normalized):
        normalized = f"{normalized}_"

    if not _is_valid_identifier(normalized):
        msg = f"Cannot normalize attribute name: {name!r}"
        raise ValueError(msg)

    return normalized


_ATTRIBUTE_NAMES: Final[frozenset[AttributeName]] = frozenset(
    typing_extensions.get_args(AttributeName)
)
"""A set of all valid SVG attribute names."""


ATTR_NAME_TO_NORMALIZED: Final = bidict.frozenbidict(
    {attr: _normalize_attr_name(attr) for attr in _ATTRIBUTE_NAMES}
)
"""
A bidirectional mapping of SVG attribute names to normalized
Python identifiers.
"""
