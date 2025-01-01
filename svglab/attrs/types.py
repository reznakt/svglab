from typing import Annotated, Literal, TypeAlias

import pydantic

from svglab import attrparse, models, utils


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
Dasharray: TypeAlias = Unparsed  # list of percentages and lengths
EndValueList: TypeAlias = Unparsed
FamilyName: TypeAlias = Unparsed
FilterPrimitiveReference: TypeAlias = Unparsed
FuncIri: TypeAlias = Unparsed
GenericFamily: TypeAlias = Unparsed
Iri: TypeAlias = Unparsed
LanguageCodes: TypeAlias = Unparsed
LanguageId: TypeAlias = Unparsed
ListOfCoordinates: TypeAlias = Unparsed
ListOfLengths: TypeAlias = Unparsed
MediaDescriptors: TypeAlias = Unparsed
Name: TypeAlias = Unparsed
Percentage: TypeAlias = Unparsed
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
Angle: TypeAlias = attrparse.AngleType
Anything: TypeAlias = str
Boolean: TypeAlias = Literal["true", "false"]
Character: TypeAlias = Annotated[
    str, pydantic.Field(min_length=1, max_length=1)
]
Color: TypeAlias = attrparse.ColorType
Integer: TypeAlias = int
Length: TypeAlias = attrparse.LengthType
ListOfPoints: TypeAlias = attrparse.PointsType
Number: TypeAlias = float
PathData: TypeAlias = attrparse.DType
RelativeSize: TypeAlias = Literal["smaller", "larger"]
TransformList: TypeAlias = attrparse.TransformType

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
ListOfExtensions: TypeAlias = models.List[Iri]
ListOfFeatures: TypeAlias = models.List[Unparsed]
ListOfNames: TypeAlias = models.List[Name]
ListOfNumbers: TypeAlias = models.List[Number]
ListOfStrings: TypeAlias = models.List[Anything]
Miterlimit: TypeAlias = Annotated[Number, pydantic.Field(ge=1)]
NumericValue: TypeAlias = Number
NumberOptionalNumber: TypeAlias = Number | models.Tuple2[Number, Number]
OpacityValue: TypeAlias = Annotated[
    Number,
    pydantic.AfterValidator(
        lambda x: utils.clamp(x, min_value=0, max_value=1)
    ),
]
Paint: TypeAlias = (
    None_
    | Literal["currentColor"]
    | Inherit
    | Color
    # <funciri> [ none | currentColor | <color> [<icccolor>] ]
    | Unparsed
)
