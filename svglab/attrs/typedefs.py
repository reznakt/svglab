"""Definitions of basic types that can be composed to define attributes."""

import pydantic
from typing_extensions import Annotated, Literal, TypeAlias

from svglab import models
from svglab.attrparse import (
    angle,
    color,
    iri,
    length,
    path_data,
    points,
    transform,
)
from svglab.utils import mathutils


Unparsed: TypeAlias = str
"""Represents a type that is currently not parsed."""


# common string literals
All: TypeAlias = Literal["all"]
Auto: TypeAlias = Literal["auto"]
Inherit: TypeAlias = Literal["inherit"]
None_: TypeAlias = Literal["none"]

# basic types that are not parsed
AdvisoryTitle: TypeAlias = Unparsed
BeginValueList: TypeAlias = Unparsed
ClockValue: TypeAlias = Unparsed
ContentType: TypeAlias = Unparsed  # MIME type
EndValueList: TypeAlias = Unparsed
FamilyName: TypeAlias = Unparsed
FilterPrimitiveReference: TypeAlias = Unparsed
GenericFamily: TypeAlias = Unparsed
IccColor: TypeAlias = Unparsed
LanguageCodes: TypeAlias = Unparsed
LanguageId: TypeAlias = Unparsed
LanguageTag: TypeAlias = Unparsed
MediaDescriptors: TypeAlias = Unparsed
Name: TypeAlias = Unparsed
ProfileName: TypeAlias = Unparsed
Shape: TypeAlias = Unparsed
Urange: TypeAlias = Unparsed
XmlName: TypeAlias = Unparsed

# basic types that are parsed
AbsoluteSize: TypeAlias = Literal[
    "xx-small",
    "x-small",
    "small",
    "medium",
    "large",
    "x-large",
    "xx-large",
]
Angle: TypeAlias = angle.AngleType
Anything: TypeAlias = str
Boolean: TypeAlias = bool
Character: TypeAlias = Annotated[
    str, pydantic.Field(min_length=1, max_length=1)
]
Color: TypeAlias = color.ColorType
FuncIri: TypeAlias = iri.FuncIriType
Integer: TypeAlias = int
Iri: TypeAlias = iri.IriType
Length: TypeAlias = length.LengthType
ListOfPoints: TypeAlias = points.PointsType
Number: TypeAlias = pydantic.FiniteFloat
PathData: TypeAlias = path_data.PathDataType
RelativeSize: TypeAlias = Literal["smaller", "larger"]
TransformList: TypeAlias = transform.TransformType


# composite types
Coordinate: TypeAlias = Length
CursorValue: TypeAlias = (
    FuncIri
    | Auto
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
ListOfCoordinates: TypeAlias = models.List[Coordinate]
ListOfExtensions: TypeAlias = models.List[Iri]
ListOfFeatures: TypeAlias = models.List[Unparsed]
ListOfLengths: TypeAlias = models.List[Length]
ListOfNames: TypeAlias = models.List[Name]
ListOfNumbers: TypeAlias = models.List[Number]
ListOfStrings: TypeAlias = models.List[Anything]
Miterlimit: TypeAlias = Annotated[Number, pydantic.Field(ge=1)]
NumericValue: TypeAlias = Number
NumberOptionalNumber: TypeAlias = Number | models.Tuple2[Number, Number]
OpacityValue: TypeAlias = Annotated[
    Number,
    pydantic.AfterValidator(
        lambda x: mathutils.clamp(x, min_value=0, max_value=1)
    ),
]
Paint: TypeAlias = (
    None_
    | Literal["currentColor", "context-fill", "context-stroke"]
    | Inherit
    | Color
    | FuncIri
)
Percentage: TypeAlias = Length

_TransformOriginDirection: TypeAlias = Literal[
    "left", "center", "right", "top", "bottom"
]
_TransformOriginValue: TypeAlias = (
    _TransformOriginDirection | Percentage | Length
)
TransformOrigin: TypeAlias = (
    _TransformOriginValue
    | models.Tuple2[_TransformOriginValue, _TransformOriginValue]
    | models.Tuple3[_TransformOriginValue, _TransformOriginValue, Length]
)
Dasharray: TypeAlias = models.List[Length | Percentage]


# SVG 2 / CSS values. svglab models SVG 1.1, and these are the handful of
# CSS values that the SVG 1.1 grammars leave out but that real documents and
# every browser use. They are kept as text -- the point is to read and write
# the document faithfully, not to interpret the function -- but constrained
# enough that a value which is simply wrong is still refused.

_FILTER_FUNCTION = (
    r"blur|brightness|contrast|drop-shadow|grayscale|hue-rotate|invert"
    r"|opacity|saturate|sepia"
)
_ARGUMENTS = r"\([^()]*(?:\([^()]*\)[^()]*)*\)"

CssFilterList: TypeAlias = Annotated[
    str,
    pydantic.StringConstraints(
        pattern=rf"^\s*(?:(?:{_FILTER_FUNCTION}){_ARGUMENTS}\s*)+$"
    ),
]
"""A list of CSS filter functions, such as `blur(2px) saturate(2)`."""

_BASIC_SHAPE = r"inset|circle|ellipse|polygon|path|rect|xywh"
_GEOMETRY_BOX = (
    r"content-box|padding-box|border-box|margin-box"
    r"|fill-box|stroke-box|view-box"
)

CssBasicShape: TypeAlias = Annotated[
    str,
    pydantic.StringConstraints(
        pattern=(
            rf"^\s*(?:(?:{_BASIC_SHAPE}){_ARGUMENTS}"
            rf"|(?:{_GEOMETRY_BOX}))"
            rf"(?:\s+(?:(?:{_BASIC_SHAPE}){_ARGUMENTS}"
            rf"|(?:{_GEOMETRY_BOX})))*\s*$"
        )
    ),
]
"""A CSS basic shape, such as `inset(0 round 4px)` or `circle(40%)`."""

BlendMode: TypeAlias = Literal[
    "normal",
    "multiply",
    "screen",
    "overlay",
    "darken",
    "lighten",
    "color-dodge",
    "color-burn",
    "hard-light",
    "soft-light",
    "difference",
    "exclusion",
    "hue",
    "saturation",
    "color",
    "luminosity",
]
"""The blend modes of CSS Compositing, which SVG 2 gives `feBlend`."""
