from __future__ import annotations

from typing import Annotated, Literal, TypeAlias

import lark
import pydantic

from svglab.attrs import utils

__all__ = ["Length", "LengthType", "LengthUnit"]


LengthUnit: TypeAlias = Literal["em", "ex", "px", "in", "cm", "mm", "pt", "pc", "%"]


@pydantic.dataclasses.dataclass
class Length:
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

    def __str__(self) -> str:
        return f"{self.value}{self.unit or ''}"


@lark.v_args(inline=True)
class Transformer(lark.Transformer[object, Length]):
    number = float
    start = Length


LengthType: TypeAlias = Annotated[
    Length, utils.get_validator(grammar="length", transformer=Transformer())
]
