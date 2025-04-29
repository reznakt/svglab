"""Definitions of basic types that can be composed to define attributes."""

import pydantic
from typing_extensions import Annotated, Literal, TypeAlias

from svglab import models
from svglab.attrparse import (
    angle,
    color,
    d,
    iri,
    length,
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
Url: TypeAlias = Unparsed
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
Number: TypeAlias = float
PathData: TypeAlias = d.DType
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
