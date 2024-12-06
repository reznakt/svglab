from typing import Literal, Protocol, TypeAlias, TypeVar, runtime_checkable

_AnyStr_contra = TypeVar("_AnyStr_contra", str, bytes, contravariant=True)
_AnyStr_co = TypeVar("_AnyStr_co", str, bytes, covariant=True)


@runtime_checkable
class SupportsRead(Protocol[_AnyStr_co]):
    """Protocol for objects that support reading.

    This exists because using `SupportsRead` from `typeshed` causes problems.

    Example:
    >>> from io import StringIO
    >>> buf = StringIO()
    >>> isinstance(buf, SupportsRead)
    True

    """

    def read(self, size: int | None = None, /) -> _AnyStr_co: ...


@runtime_checkable
class SupportsWrite(Protocol[_AnyStr_contra]):
    """Protocol for objects that support writing.

    This exists because using `SupportsWrite` from `typeshed` causes problems.

    Example:
    >>> from io import StringIO
    >>> buf = StringIO()
    >>> isinstance(buf, SupportsWrite)
    True

    """

    def write(self, data: _AnyStr_contra, /) -> int: ...


Parser: TypeAlias = Literal["html.parser", "lxml", "lxml-xml", "html5lib"]
""" Type for parsers supported by BeautifulSoup. """


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
