from typing import Literal, TypeAlias

from svglab import attrs

_NotImplemented: TypeAlias = str
"""Represents a type that is currently not parsed."""

_Incomplete: TypeAlias = str
"""Represents a "catch-all" part of a partially parsed type."""

# common string literals
Inherit: TypeAlias = Literal["inherit"]
None_: TypeAlias = Literal["none"]

# basic types that are not parsed
Angle: TypeAlias = _NotImplemented
DashArray: TypeAlias = _NotImplemented
Frequency: TypeAlias = _NotImplemented
FuncIri: TypeAlias = _NotImplemented
IccColor: TypeAlias = _NotImplemented
Iri: TypeAlias = _NotImplemented
LanguageId: TypeAlias = _NotImplemented
ListOfFamilyNames: TypeAlias = _NotImplemented
ListOfStrings: TypeAlias = _NotImplemented
Name: TypeAlias = _NotImplemented
NumberOptionalNumber: TypeAlias = _NotImplemented
Percentage: TypeAlias = _NotImplemented
Time: TypeAlias = _NotImplemented
XmlName: TypeAlias = _NotImplemented

# basic types that are parsed
Anything: TypeAlias = str
Color: TypeAlias = attrs.ColorType
Integer: TypeAlias = int
Length: TypeAlias = attrs.LengthType
ListOfPoints: TypeAlias = attrs.PointsType
Number: TypeAlias = float
PathData: TypeAlias = attrs.DType
TransformList: TypeAlias = attrs.TransformType

Coordinate: TypeAlias = Length
OpacityValue: TypeAlias = Number
Paint: TypeAlias = (
    None_ | Literal["currentColor"] | Inherit | Color | _Incomplete
)
