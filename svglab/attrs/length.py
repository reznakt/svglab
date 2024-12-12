from __future__ import annotations

from typing import Annotated, Literal, TypeAlias

import lark
import pydantic
from typing_extensions import override

from svglab import serialize
from svglab.attrs import utils

__all__ = ["Length", "LengthType", "LengthUnit"]


LengthUnit: TypeAlias = Literal[
    "em", "ex", "px", "in", "cm", "mm", "pt", "pc", "%"
]


@pydantic.dataclasses.dataclass
class Length(serialize.Serializable):
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
        value = serialize.format_number(self.value)
        return f"{value}{self.unit or ''}"


@lark.v_args(inline=True)
class Transformer(lark.Transformer[object, Length]):
    number = float
    start = Length


LengthType: TypeAlias = Annotated[
    Length,
    utils.get_validator(grammar="length", transformer=Transformer()),
]
