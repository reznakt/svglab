from __future__ import annotations

import lark
import pydantic
from typing_extensions import Annotated, Literal, TypeAlias, override

from svglab import serialize
from svglab.attrparse import utils


LengthUnit: TypeAlias = Literal[
    "em", "ex", "px", "in", "cm", "mm", "pt", "pc", "%"
]


@pydantic.dataclasses.dataclass
class Length(serialize.CustomSerializable):
    """Represents the SVG `<length>` type.

    A length is a number optionally followed by a unit. Available units are:

    - `em`: the font size of the element
    - `ex`: the x-height of the element's font
    - `px`: pixels
    - `in`: inches
    - `cm`: centimeters
    - `mm`: millimeters
    - `pt`: points
    - `pc`: picas
    - `%`: percentage of another value
    """

    value: float
    unit: LengthUnit | None = None

    @override
    def serialize(self) -> str:
        value = serialize.serialize(self.value)
        return f"{value}{self.unit or ''}"


@lark.v_args(inline=True)
class _Transformer(lark.Transformer[object, Length]):
    number = float
    length = Length


LengthType: TypeAlias = Annotated[
    Length,
    utils.get_validator(grammar="length.lark", transformer=_Transformer()),
]
