from typing import Literal, TypeAlias

from svglab import models
from svglab.attrs import types


AlignmentBaseline: TypeAlias = (
    types.Auto
    | types.Inherit
    | Literal[
        "baseline",
        "before-edge",
        "text-before-edge",
        "middle",
        "central",
        "after-edge",
        "text-after-edge",
        "ideographic",
        "alphabetic",
        "hanging",
        "mathematical",
    ]
)
BaselineShift: TypeAlias = (
    Literal["baseline", "sub", "super"]
    | types.Percentage
    | types.Length
    | types.Inherit
)
ClipPath: TypeAlias = types.FuncIri | types.None_ | types.Inherit
ClipRule: TypeAlias = Literal["nonzero", "evenodd"] | types.Inherit
Clip: TypeAlias = types.Shape | types.Auto | types.Inherit
ColorInterpolationFilters: TypeAlias = (
    types.Auto | Literal["sRGB", "linearRGB"] | types.Inherit
)
ColorInterpolation: TypeAlias = (
    types.Auto | Literal["sRGB", "linearRGB"] | types.Inherit
)
ColorProfile: TypeAlias = (
    types.Auto | Literal["sRGB"] | types.Name | types.Iri | types.Inherit
)
ColorRendering: TypeAlias = (
    types.Auto
    | Literal["optimizeSpeed", "optimizeQuality"]
    | types.Inherit
)
Color: TypeAlias = types.Color | types.Inherit
Cursor: TypeAlias = (
    types.CursorValue | types.Inherit | models.List[types.CursorValue]
)
Direction: TypeAlias = Literal["ltr", "rtl"] | types.Inherit
Display: TypeAlias = (
    Literal[
        "block",
        "compact",
        "inline-table",
        "inline",
        "list-item",
        "marker",
        "run-in",
        "table-caption",
        "table-cell",
        "table-column-group",
        "table-column",
        "table-footer-group",
        "table-header-group",
        "table-row-group",
        "table-row",
        "table",
    ]
    | types.None_
    | types.Inherit
)
DominantBaseline: TypeAlias = (
    types.Auto
    | Literal[
        "use-script",
        "no-change",
        "reset-size",
        "ideographic",
        "alphabetic",
        "hanging",
        "mathematical",
        "central",
        "middle",
        "text-after-edge",
        "text-before-edge",
    ]
    | types.Inherit
)
EnableBackground: TypeAlias = (
    Literal["accumulate"]
    | types.Inherit
    | types.Unparsed  # new [ <x> <y> <width> <height> ]
)
FillOpacity: TypeAlias = types.OpacityValue | types.Inherit
FillRule: TypeAlias = Literal["nonzero", "evenodd"] | types.Inherit
# TODO: Fill
Filter: TypeAlias = types.FuncIri | types.None_ | types.Inherit
FloodColor: TypeAlias = (
    Literal["currentColor"]
    | types.Color
    | types.Inherit
    | types.Unparsed  # <color> [<icccolor>]
)
FloodOpacity: TypeAlias = types.OpacityValue | types.Inherit
FontSizeAdjust: TypeAlias = types.Number | types.None_ | types.Inherit
# TODO: font-size
# TODO: font-stretch
# TODO: font-style
# TODO: font-variant
# TODO: font-weight
GlyphOrientationHorizontal: TypeAlias = types.Angle | types.Inherit
GlyphOrientationVertical: TypeAlias = (
    types.Auto | types.Angle | types.Inherit
)
ImageRendering: TypeAlias = (
    types.Auto
    | Literal["optimizeSpeed", "optimizeQuality"]
    | types.Inherit
)
Kerning: TypeAlias = types.Auto | types.Length | types.Inherit
LetterSpacing: TypeAlias = Literal["normal"] | types.Length | types.Inherit
LightingColor: TypeAlias = (
    Literal["currentColor"] | types.Color | types.Inherit | types.Unparsed
)
MarkerEnd: TypeAlias = types.FuncIri | types.None_ | types.Inherit
MarkerMid: TypeAlias = types.FuncIri | types.None_ | types.Inherit
MarkerStart: TypeAlias = types.FuncIri | types.None_ | types.Inherit
Mask: TypeAlias = types.FuncIri | types.None_ | types.Inherit
Opacity: TypeAlias = types.OpacityValue | types.Inherit
Overflow: TypeAlias = (
    Literal["visible", "hidden", "scroll"] | types.Auto | types.Inherit
)
PointerEvents: TypeAlias = (
    Literal[
        "visiblePainted",
        "visibleFill",
        "visibleStroke",
        "visible",
        "painted",
        "fill",
        "stroke",
    ]
    | types.All
    | types.None_
    | types.Inherit
)
ShapeRendering: TypeAlias = (
    types.Auto
    | Literal["optimizeSpeed", "crispEdges", "geometricPrecision"]
    | types.Inherit
)
StopColor: TypeAlias = (
    Literal["currentColor"]
    | types.Inherit
    | types.Unparsed  # <color> <icccolor>
)
StopOpacity: TypeAlias = types.OpacityValue | types.Inherit
StrokeDasharray: TypeAlias = types.None_ | types.Dasharray | types.Inherit
StrokeDashoffset: TypeAlias = (
    types.Percentage | types.Length | types.Inherit
)
StrokeLinecap: TypeAlias = (
    Literal["butt", "round", "square"] | types.Inherit
)
StrokeLinejoin: TypeAlias = (
    Literal["miter", "round", "bevel"] | types.Inherit
)
StrokeMiterlimit: TypeAlias = types.Miterlimit | types.Inherit
StrokeOpacity: TypeAlias = types.OpacityValue | types.Inherit
StrokeWidth: TypeAlias = types.Percentage | types.Length | types.Inherit
Stroke: TypeAlias = types.Paint
TextAnchor: TypeAlias = Literal["start", "middle", "end"] | types.Inherit
TextDecoration: TypeAlias = (
    types.None_
    | Literal["underline", "overline", "line-through", "blink"]
    | types.Inherit
)
TextRendering: TypeAlias = (
    types.Auto
    | Literal["optimizeSpeed", "optimizeLegibility", "geometricPrecision"]
    | types.Inherit
)
UnicodeBidi: TypeAlias = (
    Literal["normal", "embed", "bidi-override"] | types.Inherit
)
Visibility: TypeAlias = (
    Literal["visible", "hidden", "collapse"] | types.Inherit
)
WordSpacing: TypeAlias = Literal["normal"] | types.Length | types.Inherit
WritingMode: TypeAlias = (
    Literal["lr-tb", "rl-tb", "tb-rl", "lr", "rl", "tb"] | types.Inherit
)
