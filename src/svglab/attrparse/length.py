"""Definition of the SVG `<length>` type.

Use `Length` to represent lengths in SVG. Use `LengthType` in Pydantic fields.
"""

from __future__ import annotations

import contextlib
from collections.abc import Iterator

import lark
import more_itertools
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

from svglab.attrparse.parse import FiniteFloat, get_validator, inline_args
from svglab.errors import SvgUnitConversionError
from svglab.mixins import AddSub, FloatMulDiv
from svglab.models import DATACLASS_CONFIG, dataclass
from svglab.protocols import CustomSerializable
from svglab.serialize import get_current_formatter, serialize
from svglab.units import Converter, make_converter
from svglab.utiltypes import LengthUnit


_convert: Final[Converter[Length, LengthUnit]] = make_converter(
    conversion_table={
        ("in", "cm"): 2.54,
        ("cm", "mm"): 10,
        ("pc", "px"): 15,
        ("pt", "px"): 1.25,
        (None, "px"): 1,
        ("mm", "Q"): 4,
    }
)


@final
@dataclass(frozen=True, config=DATACLASS_CONFIG)
class Length(
    AddSub["Length"], FloatMulDiv, SupportsFloat, CustomSerializable
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

    If the unit is set to `None`, the length is considered to be in user units.

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
            >>> Length(1, "in").to("cm")
            Length(value=2.54, unit='cm')
            >>> Length(1, "in").to("mm")
            Length(value=25.4, unit='mm')
            >>> Length(10).to("px")
            Length(value=10.0, unit='px')
            >>> Length(10, "px").to(None)
            Length(value=10.0, unit=None)
            >>> Length(1, "em").to("px")
            Traceback (most recent call last):
                ...
            svglab.errors.SvgUnitConversionError: Unable to convert 'em' to ...

        """
        return _convert(self, unit)

    @override
    def serialize(self) -> str:
        formatter = get_current_formatter()
        units: Iterator[LengthUnit | Literal["preserve"]] = (
            more_itertools.always_iterable(formatter.length_unit)
        )
        converted = self

        for unit in units:
            if unit == "preserve":
                break

            with contextlib.suppress(SvgUnitConversionError):
                converted = self.to(unit)
                break

        value = serialize(converted.value, precision_group="coordinate")

        return f"{value}{converted.unit or ''}"

    @classmethod
    def zero(cls) -> Length:
        """Return a length of zero."""
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


@inline_args
class _Transformer(lark.Transformer[object, Length]):
    number = FiniteFloat
    length = Length


LengthType: TypeAlias = Annotated[
    Length,
    get_validator(grammar="length.lark", transformer=_Transformer()),
]
