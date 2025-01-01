from typing import Annotated, Literal, TypeAlias

import pydantic

from svglab import attrparse, models, utils


# special pseudo-types
_NotImplemented: TypeAlias = str
"""Represents a type that is currently not parsed."""


# common string literals
_All: TypeAlias = Literal["all"]
_Auto: TypeAlias = Literal["auto"]
_Inherit: TypeAlias = Literal["inherit"]
_None: TypeAlias = Literal["none"]

# basic types that are not parsed
_AdvisoryTitle: TypeAlias = _NotImplemented
_BeginValueList: TypeAlias = _NotImplemented
_ClockValue: TypeAlias = _NotImplemented
_ContentType: TypeAlias = _NotImplemented  # MIME type
_Dasharray: TypeAlias = _NotImplemented  # list of percentages and lengths
_EndValueList: TypeAlias = _NotImplemented
_FamilyName: TypeAlias = _NotImplemented
_FilterPrimitiveReference: TypeAlias = _NotImplemented
_FuncIri: TypeAlias = _NotImplemented
_GenericFamily: TypeAlias = _NotImplemented
_Iri: TypeAlias = _NotImplemented
_LanguageCodes: TypeAlias = _NotImplemented
_LanguageId: TypeAlias = _NotImplemented
_ListOfCoordinates: TypeAlias = _NotImplemented
_ListOfLengths: TypeAlias = _NotImplemented
_MediaDescriptors: TypeAlias = _NotImplemented
_Name: TypeAlias = _NotImplemented
_Percentage: TypeAlias = _NotImplemented
_ProfileName: TypeAlias = _NotImplemented
_Shape: TypeAlias = _NotImplemented
_Urange: TypeAlias = _NotImplemented
_XmlName: TypeAlias = _NotImplemented

# basic types that are parsed
_Angle: TypeAlias = attrparse.AngleType
_Anything: TypeAlias = str
_Color: TypeAlias = attrparse.ColorType
_Integer: TypeAlias = int
_Length: TypeAlias = attrparse.LengthType
_ListOfPoints: TypeAlias = attrparse.PointsType
_Number: TypeAlias = float
_PathData: TypeAlias = attrparse.DType
_TransformList: TypeAlias = attrparse.TransformType
_Character: TypeAlias = Annotated[
    str, pydantic.Field(min_length=1, max_length=1)
]
_Miterlimit: TypeAlias = Annotated[_Number, pydantic.Field(ge=1)]

# composite types
_Boolean: TypeAlias = Literal["true", "false"]
_Coordinate: TypeAlias = _Length
_CursorValue: TypeAlias = (
    _FuncIri
    | _Auto
    | Literal[
        "crosshair",
        "default",
        "pointer",
        "move",
        "e-resize",
        "ne-resize",
        "nw-resize",
        "n-resize",
        "se-resize",
        "sw-resize",
        "s-resize",
        "w-resize",
        "text",
        "wait",
        "help",
    ]
)
_ListOfExtensions: TypeAlias = models.List[_Iri]
_ListOfFeatures: TypeAlias = models.List[_NotImplemented]
_ListOfNames: TypeAlias = models.List[_Name]
_ListOfNumbers: TypeAlias = models.List[_Number]
_ListOfStrings: TypeAlias = models.List[_Anything]
_NumericValue: TypeAlias = _Number
_NumberOptionalNumber: TypeAlias = (
    _Number | models.Tuple2[_Number, _Number]
)
_OpacityValue: TypeAlias = Annotated[
    _Number,
    pydantic.AfterValidator(
        lambda x: utils.clamp(x, min_value=0, max_value=1)
    ),
]
_Paint: TypeAlias = (
    _None
    | Literal["currentColor"]
    | _Inherit
    | _Color
    # <funciri> [ none | currentColor | <color> [<icccolor>] ]
    | _NotImplemented
)


AccentHeight: TypeAlias = _Number
Accumulate: TypeAlias = _None | Literal["sum"]
Additive: TypeAlias = Literal["replace", "sum"]
Alphabetic: TypeAlias = _Number
Amplitude: TypeAlias = _Number
ArabicForm: TypeAlias = Literal[
    "initial", "medial", "terminal", "isolated"
]
Ascent: TypeAlias = _Number
AttributeType: TypeAlias = Literal["CSS", "XML"] | _Auto
Azimuth: TypeAlias = _Number
BaseFrequency: TypeAlias = _NumberOptionalNumber
BaseProfile: TypeAlias = _ProfileName
Bbox: TypeAlias = models.Tuple4[_Number, _Number, _Number, _Number]
Begin: TypeAlias = _BeginValueList
Bias: TypeAlias = _Number
By: TypeAlias = _NotImplemented
CalcMode: TypeAlias = Literal["discrete", "linear", "paced", "spline"]
CapHeight: TypeAlias = _Number
Class: TypeAlias = _ListOfStrings
ClipPathUnits: TypeAlias = Literal["userSpaceOnUse", "objectBoundingBox"]
ContentScriptType: TypeAlias = _ContentType
ContentStyleType: TypeAlias = _ContentType
Cx: TypeAlias = _Coordinate
Cy: TypeAlias = _Coordinate
D: TypeAlias = _PathData
Descent: TypeAlias = _Number
DiffuseConstant: TypeAlias = _Number
Divisor: TypeAlias = _Number
Dur: TypeAlias = _ClockValue | Literal["media", "indefinite"]
Dx: TypeAlias = _ListOfLengths
Dy: TypeAlias = _ListOfLengths
EdgeMode: TypeAlias = Literal["duplicate", "wrap", "none"]
Elevation: TypeAlias = _Number
End: TypeAlias = _EndValueList
Exponent: TypeAlias = _Number
ExternalResourcesRequired: TypeAlias = _Boolean
Fill: TypeAlias = Literal["freeze", "remove"]
FilterRes: TypeAlias = _NumberOptionalNumber
FilterUnits: TypeAlias = Literal["userSpaceOnUse", "objectBoundingBox"]
FontFamily: TypeAlias = models.List[_FamilyName | _GenericFamily]
FontStyle: TypeAlias = (
    _All | models.List[Literal["normal", "italic", "oblique"]]
)
FontVariant: TypeAlias = models.List[Literal["normal", "small-caps"]]
FontWeight: TypeAlias = (
    _All
    | models.List[
        Literal[
            "normal", "bold", 100, 200, 300, 400, 500, 600, 700, 800, 900
        ]
    ]
)
FontStretch: TypeAlias = (
    _All
    | models.List[
        Literal[
            "normal",
            "ultra-condensed",
            "extra-condensed",
            "condensed ",
            "semi-condensed",
            "semi-expanded",
            "expanded",
            "extra-expanded",
            "ultra-expanded",
        ]
    ]
)
FontSize: TypeAlias = _All | _ListOfLengths
Format: TypeAlias = _NotImplemented
From: TypeAlias = _NotImplemented
Fx: TypeAlias = _Coordinate
Fy: TypeAlias = _Coordinate
G1: TypeAlias = _ListOfNames
G2: TypeAlias = G1
GlyphName: TypeAlias = _ListOfNames
GlyphRef: TypeAlias = _NotImplemented
GradientTransform: TypeAlias = _TransformList
GradientUnits: TypeAlias = Literal["userSpaceOnUse", "objectBoundingBox"]
Hanging: TypeAlias = _Number
Height: TypeAlias = _Length
HorizAdvX: TypeAlias = _Number
HorizOriginX: TypeAlias = _Number
HorizOriginY: TypeAlias = _Number
Id: TypeAlias = _Name
Ideographic: TypeAlias = _Number
In: TypeAlias = _Paint | _FilterPrimitiveReference | _NotImplemented
In2: TypeAlias = In
Intercept: TypeAlias = _Number
K: TypeAlias = _Number
K1: TypeAlias = _Number
K2: TypeAlias = _Number
K3: TypeAlias = _Number
K4: TypeAlias = _Number
KernelMatrix: TypeAlias = _ListOfNumbers
KernelUnitLength: TypeAlias = _NumberOptionalNumber
KeyPoints: TypeAlias = _ListOfNumbers
KeySplines: TypeAlias = _NotImplemented
KeyTimes: TypeAlias = _NotImplemented
Lang: TypeAlias = _LanguageCodes
LengthAdjust: TypeAlias = Literal["spacing", "spacingAndGlyphs"]
LimitingConeAngle: TypeAlias = _Number
Local: TypeAlias = _NotImplemented
MarkerHeight: TypeAlias = _Length
MarkerUnits: TypeAlias = Literal["strokeWidth", "userSpaceOnUse"]
MarkerWidth: TypeAlias = _Length
MaskContentUnits: TypeAlias = Literal[
    "userSpaceOnUse", "objectBoundingBox"
]
MaskUnits: TypeAlias = Literal["userSpaceOnUse", "objectBoundingBox"]
Mathematical: TypeAlias = _Number
Max: TypeAlias = Literal["media"] | _ClockValue
Media: TypeAlias = _MediaDescriptors
Method: TypeAlias = Literal["align", "stretch"]
Min: TypeAlias = Literal["media"] | _ClockValue
Mode: TypeAlias = Literal[
    "normal", "multiply", "screen", "darken", "lighten"
]
NumOctaves: TypeAlias = _Integer
Offset: TypeAlias = _Number | _Percentage
OnAbort: TypeAlias = _Anything
OnActivate: TypeAlias = _Anything
OnBegin: TypeAlias = _Anything
OnClick: TypeAlias = _Anything
OnEnd: TypeAlias = _Anything
OnError: TypeAlias = _Anything
OnFocusIn: TypeAlias = _Anything
OnLoad: TypeAlias = _Anything
OnMouseDown: TypeAlias = _Anything
OnMouseMove: TypeAlias = _Anything
OnMouseOut: TypeAlias = _Anything
OnMouseOver: TypeAlias = _Anything
OnMouseUp: TypeAlias = _Anything
OnRepeat: TypeAlias = _Anything
OnResize: TypeAlias = _Anything
OnScroll: TypeAlias = _Anything
OnUnload: TypeAlias = _Anything
OnZoom: TypeAlias = _Anything
Operator: TypeAlias = Literal[
    "over", "in", "out", "atop", "xor", "arithmetic"
]
Order: TypeAlias = _NumberOptionalNumber
Orient: TypeAlias = _Auto | _Angle
Orientation: TypeAlias = Literal["h", "v"]
Origin: TypeAlias = Literal["default"]
OverlinePosition: TypeAlias = _Number
OverlineThickness: TypeAlias = _Number
Panose1: TypeAlias = models.Tuple[
    tuple[
        _Integer,
        _Integer,
        _Integer,
        _Integer,
        _Integer,
        _Integer,
        _Integer,
        _Integer,
        _Integer,
        _Integer,
    ]
]
Path: TypeAlias = _PathData
PathLength: TypeAlias = _Number
PatternContentUnits: TypeAlias = Literal[
    "userSpaceOnUse", "objectBoundingBox"
]
PatternTransform: TypeAlias = _TransformList
PatternUnits: TypeAlias = Literal["userSpaceOnUse", "objectBoundingBox"]
Points: TypeAlias = _ListOfPoints
PointsAtX: TypeAlias = _Number
PointsAtY: TypeAlias = _Number
PointsAtZ: TypeAlias = _Number
PreserveAlpha: TypeAlias = _Boolean
PreserveAspectRatio: TypeAlias = (
    None
    | Literal[
        "xMinYMin",
        "xMidYMin",
        "xMaxYMin",
        "xMinYMid",
        "xMidYMid",
        "xMaxYMid",
        "xMinYMax",
        "xMidYMax",
        "xMaxYMax",
    ]
    | _NotImplemented
)
PrimitiveUnits: TypeAlias = Literal["userSpaceOnUse", "objectBoundingBox"]
R: TypeAlias = _Length
Radius: TypeAlias = _NumberOptionalNumber
RefX: TypeAlias = _Coordinate
RefY: TypeAlias = _Coordinate
RenderingIntent: TypeAlias = Literal[
    "auto",
    "perceptual",
    "relative-colorimetric",
    "saturation",
    "absolute-colorimetric",
]
RepeatCount: TypeAlias = Literal["indefinite"] | _NumericValue
RepeatDur: TypeAlias = Literal["indefinite"] | _ClockValue
RequiredExtensions: TypeAlias = _ListOfExtensions
RequiredFeatures: TypeAlias = _ListOfFeatures
Restart: TypeAlias = Literal["always", "whenNotActive", "never"]
Result: TypeAlias = _FilterPrimitiveReference
Rotate: TypeAlias = _ListOfNumbers
Rx: TypeAlias = _Length
Ry: TypeAlias = _Length
Scale: TypeAlias = _Number
Seed: TypeAlias = _Number
Slope: TypeAlias = _Number
Spacing: TypeAlias = Literal["auto", "exact"]
SpecularConstant: TypeAlias = _Number
SpecularExponent: TypeAlias = _Number
SpreadMethod: TypeAlias = Literal["pad", "reflect", "repeat"]
StartOffset: TypeAlias = _Length
StdDeviation: TypeAlias = _NumberOptionalNumber
Stemh: TypeAlias = _Number
Stemv: TypeAlias = _Number
StitchTiles: TypeAlias = Literal["stitch", "noStitch"]
StrikethroughPosition: TypeAlias = _Number
StrikethroughThickness: TypeAlias = _Number
String: TypeAlias = _Anything
Style: TypeAlias = _NotImplemented
SurfaceScale: TypeAlias = _Number
SystemLanguage: TypeAlias = _LanguageCodes
TableValues: TypeAlias = _ListOfNumbers
Target: TypeAlias = (
    Literal["_replace", "_self", "_parent", "_top", "_blank"] | _XmlName
)
TargetX: TypeAlias = _Integer
TargetY: TypeAlias = _Integer
TextLength: TypeAlias = _Length
Title: TypeAlias = _AdvisoryTitle
To: TypeAlias = _NotImplemented
Transform: TypeAlias = _TransformList
Type: TypeAlias = Literal["translate", "scale", "rotate", "skewX", "skewY"]
U1: TypeAlias = models.List[_Character | _Urange]
U2: TypeAlias = U1
UnderlinePosition: TypeAlias = _Number
UnderlineThickness: TypeAlias = _Number
Unicode: TypeAlias = _Anything
UnicodeRange: TypeAlias = models.List[_Urange]
UnitsPerEm: TypeAlias = _Number
VAlphabetic: TypeAlias = _Number
VHanging: TypeAlias = _Number
VIdeographic: TypeAlias = _Number
VMathematical: TypeAlias = _Number
Values: TypeAlias = _ListOfNumbers
Version: TypeAlias = Literal["1.1"]
VertAdvY: TypeAlias = _Number
VertOriginX: TypeAlias = _Number
VertOriginY: TypeAlias = _Number
ViewBox: TypeAlias = models.Tuple4[_Number, _Number, _Number, _Number]
ViewTarget: TypeAlias = models.List[_XmlName]
Width: TypeAlias = _Length
Widths: TypeAlias = models.List[_Urange | models.Tuple2[_Urange, _Number]]
X: TypeAlias = _ListOfCoordinates
XHeight: TypeAlias = _Number
X1: TypeAlias = _Coordinate
X2: TypeAlias = _Coordinate
XChannelSelector: TypeAlias = Literal["R", "G", "B", "A"]
XlinkActuate: TypeAlias = Literal["onRequest"]
XlinkArcrole: TypeAlias = _Iri
XlinkHref: TypeAlias = _Iri
XlinkRole: TypeAlias = _Iri
XlinkShow: TypeAlias = Literal["new", "replace", "embed", "other", "none"]
XlinkTitle: TypeAlias = _Anything
XlinkType: TypeAlias = Literal["simple"]
XmlBase: TypeAlias = _Iri
XmlLang: TypeAlias = _LanguageId
XmlSpace: TypeAlias = Literal["default", "preserve"]
Y: TypeAlias = _ListOfCoordinates
Y1: TypeAlias = _Coordinate
Y2: TypeAlias = _Coordinate
YChannelSelector: TypeAlias = Literal["R", "G", "B", "A"]
Z: TypeAlias = _Number
ZoomAndPan: TypeAlias = Literal["disable", "magnify"]


AlignmentBaseline: TypeAlias = (
    _Auto
    | _Inherit
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
    Literal["baseline", "sub", "super"] | _Percentage | _Length | _Inherit
)
ClipPath: TypeAlias = _FuncIri | _None | _Inherit
ClipRule: TypeAlias = Literal["nonzero", "evenodd"] | _Inherit
Clip: TypeAlias = _Shape | _Auto | _Inherit
ColorInterpolationFilters: TypeAlias = (
    _Auto | Literal["sRGB", "linearRGB"] | _Inherit
)
ColorInterpolation: TypeAlias = (
    _Auto | Literal["sRGB", "linearRGB"] | _Inherit
)
ColorProfile: TypeAlias = _Auto | Literal["sRGB"] | _Name | _Iri | _Inherit
ColorRendering: TypeAlias = (
    _Auto | Literal["optimizeSpeed", "optimizeQuality"] | _Inherit
)
Color: TypeAlias = _Color | _Inherit
Cursor: TypeAlias = _CursorValue | _Inherit | models.List[_CursorValue]
Direction: TypeAlias = Literal["ltr", "rtl"] | _Inherit
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
    | _None
    | _Inherit
)
DominantBaseline: TypeAlias = (
    _Auto
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
    | _Inherit
)
EnableBackground: TypeAlias = (
    Literal["accumulate"]
    | _Inherit
    | _NotImplemented  # new [ <x> <y> <width> <height> ]
)
FillOpacity: TypeAlias = _OpacityValue | _Inherit
FillRule: TypeAlias = Literal["nonzero", "evenodd"] | _Inherit
# TODO: Fill
Filter: TypeAlias = _FuncIri | _None | _Inherit
FloodColor: TypeAlias = (
    Literal["currentColor"]
    | _Color
    | _Inherit
    | _NotImplemented  # <color> [<icccolor>]
)
FloodOpacity: TypeAlias = _OpacityValue | _Inherit
FontSizeAdjust: TypeAlias = _Number | _None | _Inherit
# TODO: font-size
# TODO: font-stretch
# TODO: font-style
# TODO: font-variant
# TODO: font-weight
GlyphOrientationHorizontal: TypeAlias = _Angle | _Inherit
GlyphOrientationVertical: TypeAlias = _Auto | _Angle | _Inherit
ImageRendering: TypeAlias = (
    _Auto | Literal["optimizeSpeed", "optimizeQuality"] | _Inherit
)
Kerning: TypeAlias = _Auto | _Length | _Inherit
LetterSpacing: TypeAlias = Literal["normal"] | _Length | _Inherit
LightingColor: TypeAlias = (
    Literal["currentColor"] | _Color | _Inherit | _NotImplemented
)
MarkerEnd: TypeAlias = _FuncIri | _None | _Inherit
MarkerMid: TypeAlias = _FuncIri | _None | _Inherit
MarkerStart: TypeAlias = _FuncIri | _None | _Inherit
Mask: TypeAlias = _FuncIri | _None | _Inherit
Opacity: TypeAlias = _OpacityValue | _Inherit
Overflow: TypeAlias = (
    Literal["visible", "hidden", "scroll"] | _Auto | _Inherit
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
    | _All
    | _None
    | _Inherit
)
ShapeRendering: TypeAlias = (
    _Auto
    | Literal["optimizeSpeed", "crispEdges", "geometricPrecision"]
    | _Inherit
)
StopColor: TypeAlias = (
    Literal["currentColor"]
    | _Inherit
    | _NotImplemented  # <color> <icccolor>
)
StopOpacity: TypeAlias = _OpacityValue | _Inherit
StrokeDasharray: TypeAlias = _None | _Dasharray | _Inherit
StrokeDashoffset: TypeAlias = _Percentage | _Length | _Inherit
StrokeLinecap: TypeAlias = Literal["butt", "round", "square"] | _Inherit
StrokeLinejoin: TypeAlias = Literal["miter", "round", "bevel"] | _Inherit
StrokeMiterlimit: TypeAlias = _Miterlimit | _Inherit
StrokeOpacity: TypeAlias = _OpacityValue | _Inherit
StrokeWidth: TypeAlias = _Percentage | _Length | _Inherit
Stroke: TypeAlias = _Paint
TextAnchor: TypeAlias = Literal["start", "middle", "end"] | _Inherit
TextDecoration: TypeAlias = (
    _None
    | Literal["underline", "overline", "line-through", "blink"]
    | _Inherit
)
TextRendering: TypeAlias = (
    _Auto
    | Literal["optimizeSpeed", "optimizeLegibility", "geometricPrecision"]
    | _Inherit
)
UnicodeBidi: TypeAlias = (
    Literal["normal", "embed", "bidi-override"] | _Inherit
)
Visibility: TypeAlias = Literal["visible", "hidden", "collapse"] | _Inherit
WordSpacing: TypeAlias = Literal["normal"] | _Length | _Inherit
WritingMode: TypeAlias = (
    Literal["lr-tb", "rl-tb", "tb-rl", "lr", "rl", "tb"] | _Inherit
)
