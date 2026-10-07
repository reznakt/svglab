"""Definitions of basic types that can be composed to define attributes."""

import pydantic
from typing_extensions import Annotated, Literal, TypeAlias

from svglab.attrparse.angle import AngleType
from svglab.attrparse.color import ColorType
from svglab.attrparse.iri import FuncIriType, IriType
from svglab.attrparse.length import LengthType
from svglab.attrparse.path_data import PathDataType
from svglab.attrparse.points import PointsType
from svglab.attrparse.transform import TransformType
from svglab.models import List, Tuple
from svglab.utils.mathutils import clamp


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
Angle: TypeAlias = AngleType
Anything: TypeAlias = str
Boolean: TypeAlias = bool
Character: TypeAlias = Annotated[
    str, pydantic.Field(min_length=1, max_length=1)
]
Color: TypeAlias = ColorType
FuncIri: TypeAlias = FuncIriType
ImageRendering: TypeAlias = Literal["optimizeSpeed", "optimizeQuality"]
Integer: TypeAlias = int
Iri: TypeAlias = IriType
Length: TypeAlias = LengthType
ListOfPoints: TypeAlias = PointsType
Number: TypeAlias = pydantic.FiniteFloat
PathData: TypeAlias = PathDataType
RelativeSize: TypeAlias = Literal["smaller", "larger"]
ShapeRendering: TypeAlias = Literal[
    "optimizeSpeed", "crispEdges", "geometricPrecision"
]
TextRendering: TypeAlias = Literal[
    "optimizeSpeed", "optimizeLegibility", "geometricPrecision"
]
TransformList: TypeAlias = TransformType


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
ListOfCoordinates: TypeAlias = List[Coordinate]
ListOfExtensions: TypeAlias = List[Iri]
ListOfFeatures: TypeAlias = List[Unparsed]
ListOfLengths: TypeAlias = List[Length]
ListOfNames: TypeAlias = List[Name]
ListOfNumbers: TypeAlias = List[Number]
ListOfStrings: TypeAlias = List[Anything]
Miterlimit: TypeAlias = Annotated[Number, pydantic.Field(ge=1)]
NumericValue: TypeAlias = Number
NumberOptionalNumber: TypeAlias = Number | Tuple[Number, Number]
OpacityValue: TypeAlias = Annotated[
    Number,
    pydantic.AfterValidator(lambda x: clamp(x, min_value=0, max_value=1)),
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
    | Tuple[_TransformOriginValue, _TransformOriginValue]
    | Tuple[_TransformOriginValue, _TransformOriginValue, Length]
)
Dasharray: TypeAlias = List[Length | Percentage]
