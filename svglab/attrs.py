from keyword import iskeyword
from typing import Final, Literal, TypeGuard

from bidict import frozenbidict

type AttributeName = Literal[
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

ATTRIBUTE_NAMES: Final = frozenset[AttributeName](
    (
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
    )
)


def is_valid_identifier(name: str) -> bool:
    return name.isidentifier() and not iskeyword(name)


def normalize_attr_name(name: AttributeName) -> str:
    normalized = name.replace("-", "_")

    if not is_valid_identifier(normalized):
        normalized = f"{normalized}_"

    if not is_valid_identifier(normalized):
        msg = f"Cannot normalize attribute name: {name!r}"
        raise ValueError(msg)

    return normalized


ATTR_TO_NORMALIZED: Final = frozenbidict(
    (attr, normalize_attr_name(attr)) for attr in ATTRIBUTE_NAMES
)


def attr_to_normalized(attr: AttributeName) -> str:
    return ATTR_TO_NORMALIZED[attr]


def normalized_to_attr(normalized: str) -> AttributeName:
    return ATTR_TO_NORMALIZED.inverse[normalized]


def is_attr_name(name: str) -> TypeGuard[AttributeName]:
    return name in ATTRIBUTE_NAMES


def is_normalized_name(name: str) -> bool:
    return name in ATTR_TO_NORMALIZED.values()


def attr_from_str(key: AttributeName, value: str) -> object:
    match key:
        case "x" | "y" | "width" | "height":
            return float(value)
        case "viewBox":
            return tuple(map(float, value.split()))
        case "xmlns" | "class":
            return value
        case _:
            msg = f"Unknown attribute: {key!r}"
            raise ValueError(msg)


def attr_to_str(key: str, value: object) -> str:
    match key, value:
        case "viewBox", tuple():
            return " ".join(map(str, value))
        case _:
            return str(value)
