from typing import Literal, TypeAlias

from svglab import models
from svglab.attrs import types


AccentHeight: TypeAlias = types.Number
Accumulate: TypeAlias = types.None_ | Literal["sum"]
Additive: TypeAlias = Literal["replace", "sum"]
Alphabetic: TypeAlias = types.Number
Amplitude: TypeAlias = types.Number
ArabicForm: TypeAlias = Literal[
    "initial", "medial", "terminal", "isolated"
]
Ascent: TypeAlias = types.Number
AttributeType: TypeAlias = Literal["CSS", "XML"] | types.Auto
Azimuth: TypeAlias = types.Number
BaseFrequency: TypeAlias = types.NumberOptionalNumber
BaseProfile: TypeAlias = types.ProfileName
Bbox: TypeAlias = models.Tuple4[
    types.Number, types.Number, types.Number, types.Number
]
Begin: TypeAlias = types.BeginValueList
Bias: TypeAlias = types.Number
By: TypeAlias = types.Unparsed
CalcMode: TypeAlias = Literal["discrete", "linear", "paced", "spline"]
CapHeight: TypeAlias = types.Number
Class: TypeAlias = types.ListOfStrings
ClipPathUnits: TypeAlias = Literal["userSpaceOnUse", "objectBoundingBox"]
ContentScriptType: TypeAlias = types.ContentType
ContentStyleType: TypeAlias = types.ContentType
Cx: TypeAlias = types.Coordinate
Cy: TypeAlias = types.Coordinate
D: TypeAlias = types.PathData
Descent: TypeAlias = types.Number
DiffuseConstant: TypeAlias = types.Number
Divisor: TypeAlias = types.Number
Dur: TypeAlias = types.ClockValue | Literal["media", "indefinite"]
Dx: TypeAlias = types.ListOfLengths
Dy: TypeAlias = types.ListOfLengths
EdgeMode: TypeAlias = Literal["duplicate", "wrap", "none"]
Elevation: TypeAlias = types.Number
End: TypeAlias = types.EndValueList
Exponent: TypeAlias = types.Number
ExternalResourcesRequired: TypeAlias = types.Boolean
Fill: TypeAlias = Literal["freeze", "remove"]
FilterRes: TypeAlias = types.NumberOptionalNumber
FilterUnits: TypeAlias = Literal["userSpaceOnUse", "objectBoundingBox"]
FontFamily: TypeAlias = models.List[types.FamilyName | types.GenericFamily]
FontStyle: TypeAlias = (
    types.All | models.List[Literal["normal", "italic", "oblique"]]
)
FontVariant: TypeAlias = models.List[Literal["normal", "small-caps"]]
FontWeight: TypeAlias = (
    types.All
    | models.List[
        Literal[
            "normal", "bold", 100, 200, 300, 400, 500, 600, 700, 800, 900
        ]
    ]
)
FontStretch: TypeAlias = (
    types.All
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
FontSize: TypeAlias = types.All | types.ListOfLengths
Format: TypeAlias = types.Unparsed
From: TypeAlias = types.Unparsed
Fx: TypeAlias = types.Coordinate
Fy: TypeAlias = types.Coordinate
G1: TypeAlias = types.ListOfNames
G2: TypeAlias = G1
GlyphName: TypeAlias = types.ListOfNames
GlyphRef: TypeAlias = types.Unparsed
GradientTransform: TypeAlias = types.TransformList
GradientUnits: TypeAlias = Literal["userSpaceOnUse", "objectBoundingBox"]
Hanging: TypeAlias = types.Number
Height: TypeAlias = types.Length
HorizAdvX: TypeAlias = types.Number
HorizOriginX: TypeAlias = types.Number
HorizOriginY: TypeAlias = types.Number
Id: TypeAlias = types.Name
Ideographic: TypeAlias = types.Number
In: TypeAlias = (
    types.Paint | types.FilterPrimitiveReference | types.Unparsed
)
In2: TypeAlias = In
Intercept: TypeAlias = types.Number
K: TypeAlias = types.Number
K1: TypeAlias = types.Number
K2: TypeAlias = types.Number
K3: TypeAlias = types.Number
K4: TypeAlias = types.Number
KernelMatrix: TypeAlias = types.ListOfNumbers
KernelUnitLength: TypeAlias = types.NumberOptionalNumber
KeyPoints: TypeAlias = types.ListOfNumbers
KeySplines: TypeAlias = types.Unparsed
KeyTimes: TypeAlias = types.Unparsed
Lang: TypeAlias = types.LanguageCodes
LengthAdjust: TypeAlias = Literal["spacing", "spacingAndGlyphs"]
LimitingConeAngle: TypeAlias = types.Number
Local: TypeAlias = types.Unparsed
MarkerHeight: TypeAlias = types.Length
MarkerUnits: TypeAlias = Literal["strokeWidth", "userSpaceOnUse"]
MarkerWidth: TypeAlias = types.Length
MaskContentUnits: TypeAlias = Literal[
    "userSpaceOnUse", "objectBoundingBox"
]
MaskUnits: TypeAlias = Literal["userSpaceOnUse", "objectBoundingBox"]
Mathematical: TypeAlias = types.Number
Max: TypeAlias = Literal["media"] | types.ClockValue
Media: TypeAlias = types.MediaDescriptors
Method: TypeAlias = Literal["align", "stretch"]
Min: TypeAlias = Literal["media"] | types.ClockValue
Mode: TypeAlias = Literal[
    "normal", "multiply", "screen", "darken", "lighten"
]
NumOctaves: TypeAlias = types.Integer
Offset: TypeAlias = types.Number | types.Percentage
OnAbort: TypeAlias = types.Anything
OnActivate: TypeAlias = types.Anything
OnBegin: TypeAlias = types.Anything
OnClick: TypeAlias = types.Anything
OnEnd: TypeAlias = types.Anything
OnError: TypeAlias = types.Anything
OnFocusIn: TypeAlias = types.Anything
OnLoad: TypeAlias = types.Anything
OnMouseDown: TypeAlias = types.Anything
OnMouseMove: TypeAlias = types.Anything
OnMouseOut: TypeAlias = types.Anything
OnMouseOver: TypeAlias = types.Anything
OnMouseUp: TypeAlias = types.Anything
OnRepeat: TypeAlias = types.Anything
OnResize: TypeAlias = types.Anything
OnScroll: TypeAlias = types.Anything
OnUnload: TypeAlias = types.Anything
OnZoom: TypeAlias = types.Anything
Operator: TypeAlias = Literal[
    "over", "in", "out", "atop", "xor", "arithmetic"
]
Order: TypeAlias = types.NumberOptionalNumber
Orient: TypeAlias = types.Auto | types.Angle
Orientation: TypeAlias = Literal["h", "v"]
Origin: TypeAlias = Literal["default"]
OverlinePosition: TypeAlias = types.Number
OverlineThickness: TypeAlias = types.Number
Panose1: TypeAlias = models.Tuple[
    tuple[
        types.Integer,
        types.Integer,
        types.Integer,
        types.Integer,
        types.Integer,
        types.Integer,
        types.Integer,
        types.Integer,
        types.Integer,
        types.Integer,
    ]
]
Path: TypeAlias = types.PathData
PathLength: TypeAlias = types.Number
PatternContentUnits: TypeAlias = Literal[
    "userSpaceOnUse", "objectBoundingBox"
]
PatternTransform: TypeAlias = types.TransformList
PatternUnits: TypeAlias = Literal["userSpaceOnUse", "objectBoundingBox"]
Points: TypeAlias = types.ListOfPoints
PointsAtX: TypeAlias = types.Number
PointsAtY: TypeAlias = types.Number
PointsAtZ: TypeAlias = types.Number
PreserveAlpha: TypeAlias = types.Boolean
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
    | types.Unparsed
)
PrimitiveUnits: TypeAlias = Literal["userSpaceOnUse", "objectBoundingBox"]
R: TypeAlias = types.Length
Radius: TypeAlias = types.NumberOptionalNumber
RefX: TypeAlias = types.Coordinate
RefY: TypeAlias = types.Coordinate
RenderingIntent: TypeAlias = Literal[
    "auto",
    "perceptual",
    "relative-colorimetric",
    "saturation",
    "absolute-colorimetric",
]
RepeatCount: TypeAlias = Literal["indefinite"] | types.NumericValue
RepeatDur: TypeAlias = Literal["indefinite"] | types.ClockValue
RequiredExtensions: TypeAlias = types.ListOfExtensions
RequiredFeatures: TypeAlias = types.ListOfFeatures
Restart: TypeAlias = Literal["always", "whenNotActive", "never"]
Result: TypeAlias = types.FilterPrimitiveReference
Rotate: TypeAlias = types.ListOfNumbers
Rx: TypeAlias = types.Length
Ry: TypeAlias = types.Length
Scale: TypeAlias = types.Number
Seed: TypeAlias = types.Number
Slope: TypeAlias = types.Number
Spacing: TypeAlias = Literal["auto", "exact"]
SpecularConstant: TypeAlias = types.Number
SpecularExponent: TypeAlias = types.Number
SpreadMethod: TypeAlias = Literal["pad", "reflect", "repeat"]
StartOffset: TypeAlias = types.Length
StdDeviation: TypeAlias = types.NumberOptionalNumber
Stemh: TypeAlias = types.Number
Stemv: TypeAlias = types.Number
StitchTiles: TypeAlias = Literal["stitch", "noStitch"]
StrikethroughPosition: TypeAlias = types.Number
StrikethroughThickness: TypeAlias = types.Number
String: TypeAlias = types.Anything
Style: TypeAlias = types.Unparsed
SurfaceScale: TypeAlias = types.Number
SystemLanguage: TypeAlias = types.LanguageCodes
TableValues: TypeAlias = types.ListOfNumbers
Target: TypeAlias = (
    Literal["_replace", "_self", "_parent", "_top", "_blank"]
    | types.XmlName
)
TargetX: TypeAlias = types.Integer
TargetY: TypeAlias = types.Integer
TextLength: TypeAlias = types.Length
Title: TypeAlias = types.AdvisoryTitle
To: TypeAlias = types.Unparsed
Transform: TypeAlias = types.TransformList
Type: TypeAlias = Literal["translate", "scale", "rotate", "skewX", "skewY"]
U1: TypeAlias = models.List[types.Character | types.Urange]
U2: TypeAlias = U1
UnderlinePosition: TypeAlias = types.Number
UnderlineThickness: TypeAlias = types.Number
Unicode: TypeAlias = types.Anything
UnicodeRange: TypeAlias = models.List[types.Urange]
UnitsPerEm: TypeAlias = types.Number
VAlphabetic: TypeAlias = types.Number
VHanging: TypeAlias = types.Number
VIdeographic: TypeAlias = types.Number
VMathematical: TypeAlias = types.Number
Values: TypeAlias = types.ListOfNumbers
Version: TypeAlias = Literal["1.1"]
VertAdvY: TypeAlias = types.Number
VertOriginX: TypeAlias = types.Number
VertOriginY: TypeAlias = types.Number
ViewBox: TypeAlias = models.Tuple4[
    types.Number, types.Number, types.Number, types.Number
]
ViewTarget: TypeAlias = models.List[types.XmlName]
Width: TypeAlias = types.Length
Widths: TypeAlias = models.List[
    types.Urange | models.Tuple2[types.Urange, types.Number]
]
X: TypeAlias = types.ListOfCoordinates
XHeight: TypeAlias = types.Number
X1: TypeAlias = types.Coordinate
X2: TypeAlias = types.Coordinate
XChannelSelector: TypeAlias = Literal["R", "G", "B", "A"]
XlinkActuate: TypeAlias = Literal["onRequest"]
XlinkArcrole: TypeAlias = types.Iri
XlinkHref: TypeAlias = types.Iri
XlinkRole: TypeAlias = types.Iri
XlinkShow: TypeAlias = Literal["new", "replace", "embed", "other", "none"]
XlinkTitle: TypeAlias = types.Anything
XlinkType: TypeAlias = Literal["simple"]
XmlBase: TypeAlias = types.Iri
XmlLang: TypeAlias = types.LanguageId
XmlSpace: TypeAlias = Literal["default", "preserve"]
Y: TypeAlias = types.ListOfCoordinates
Y1: TypeAlias = types.Coordinate
Y2: TypeAlias = types.Coordinate
YChannelSelector: TypeAlias = Literal["R", "G", "B", "A"]
Z: TypeAlias = types.Number
ZoomAndPan: TypeAlias = Literal["disable", "magnify"]
