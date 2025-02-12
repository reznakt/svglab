from __future__ import annotations

import lark
import pydantic
from typing_extensions import (
    Annotated,
    Literal,
    TypeAlias,
    final,
    override,
)

from svglab import serialize
from svglab.attrparse import utils


LengthUnit: TypeAlias = Literal[
    "%",
    "ch",
    "cm",
    "em",
    "ex",
    "in",
    "mm",
    "pc",
    "pt",
    "px",
    "Q",
    "rem",
    "vh",
    "vmax",
    "vmin",
    "vw",
]


@final
@pydantic.dataclasses.dataclass
class Length(serialize.CustomSerializable):
    """Represents the SVG `<length>` type.

    A length is a number optionally followed by a unit. Available units are:
    - `%`: percentage
    - `ch`: character unit
    - `cm`: centimeters
    - `em`: relative to the font size of the element
    - `ex`: relative to the x-height of the element's font
    - `in`: inches
    - `mm`: millimeters
    - `pc`: picas
    - `pt`: points
    - `px`: pixels
    - `Q`: quarter-millimeters
    - `rem`: relative to the font size of the root element
    - `vh`: viewport height
    - `vmax`: maximum of the viewport's height and width
    - `vmin`: minimum of the viewport's height and width
    - `vw`: viewport width

    """

    value: float
    unit: LengthUnit | None = pydantic.Field(default=None, frozen=True)

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
