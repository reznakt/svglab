from __future__ import annotations

import lark
import pydantic
from typing_extensions import (
    Annotated,
    Final,
    Literal,
    Self,
    SupportsFloat,
    TypeAlias,
    final,
    override,
)

from svglab import mixins, protocols, serialize, units
from svglab.attrparse import parse


LengthUnit: TypeAlias = (
    Literal[
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
    | None
)

_convert: Final[units.Converter[Length, LengthUnit]] = (
    units.make_converter(
        conversion_table={
            ("cm", "in"): 2.54,
            ("cm", "mm"): 10,
            ("pc", "px"): 15,
            ("pt", "px"): 1.25,
            (None, "px"): 1,
        }
    )
)


@final
@pydantic.dataclasses.dataclass(frozen=True)
class Length(
    mixins.AddSub["Length"],
    mixins.FloatMulDiv,
    SupportsFloat,
    protocols.CustomSerializable,
):
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
    unit: LengthUnit = None

    def to(self, unit: LengthUnit) -> Length:
        """Convert the length to a different unit.

        Args:
            unit: The unit to convert to.

        Returns:
            A new `Length` object with the converted value and new unit.

        Raises:
            SvgUnitConversionError: If the conversion is not possible.

        Examples:
            >>> length = Length(10, "cm")
            >>> length.to("mm")
            Length(value=100.0, unit='mm')

        """
        return _convert(self, unit)

    @override
    def serialize(self) -> str:
        value = serialize.serialize(self.value)
        return f"{value}{self.unit or ''}"

    @classmethod
    def zero(cls) -> Length:
        return cls(0)

    @override
    def __add__(self, other: Length) -> Self:
        other_value = other.to(self.unit).value

        return type(self)(value=self.value + other_value, unit=self.unit)

    @override
    def __mul__(self, other: float) -> Self:
        return type(self)(value=self.value * other, unit=self.unit)

    def __bool__(self) -> bool:
        return bool(self.value)

    @override
    def __float__(self) -> float:
        return self.to(None).value


@lark.v_args(inline=True)
class _Transformer(lark.Transformer[object, Length]):
    number = float
    length = Length


LengthType: TypeAlias = Annotated[
    Length,
    parse.get_validator(grammar="length.lark", transformer=_Transformer()),
]
