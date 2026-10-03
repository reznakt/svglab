"""Definition of the SVG `<length>` type.

Use `Length` to represent lengths in SVG. Use `LengthType` in Pydantic fields.
"""

from __future__ import annotations

import contextlib
import fractions
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

from svglab import (
    errors,
    mixins,
    models,
    protocols,
    serialize,
    units,
    utiltypes,
)
from svglab.attrparse import parse


DPI: Final = 96
"""
The number of user units (`px`) in an inch.

CSS anchors the physical units to the reference pixel at 96 per inch, and SVG 2
takes its units from CSS, so `1in` is `96px`, `2.54cm`, `72pt` and `6pc`. SVG
1.1 left the figure to the user agent; browsers and resvg use 96 as well.
"""

_convert: Final[units.Converter[Length, utiltypes.LengthUnit]] = (
    units.make_converter(
        {
            None: fractions.Fraction(1),
            "px": fractions.Fraction(1),
            "in": fractions.Fraction(DPI),
            "cm": fractions.Fraction(DPI) / fractions.Fraction("2.54"),
            "mm": fractions.Fraction(DPI) / fractions.Fraction("25.4"),
            "Q": fractions.Fraction(DPI) / fractions.Fraction("101.6"),
            "pt": fractions.Fraction(DPI, 72),
            "pc": fractions.Fraction(DPI, 6),
        }
    )
)


@final
@models.dataclass(frozen=True, config=models.DATACLASS_CONFIG)
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

    If the unit is set to `None`, the length is considered to be in user units.

    The absolute units (`px`, `cm`, `mm`, `Q`, `in`, `pt` and `pc`) convert to
    user units and to each other, with `DPI` user units to an inch. The
    relative units depend on the font, the viewport or the parent element, so
    they do not convert to anything but themselves.

    """

    value: float
    unit: utiltypes.LengthUnit = None

    def to(self, unit: utiltypes.LengthUnit) -> Length:
        """Convert the length to a different unit.

        Args:
            unit: The unit to convert to.

        Returns:
            A new `Length` object with the converted value and new unit.

        Raises:
            SvgUnitConversionError: If either unit is relative, such as `%`
                or `em`, and the units differ.

        Examples:
            >>> length = Length(10, "cm")
            >>> length.to("mm")
            Length(value=100.0, unit='mm')
            >>> Length(1, "in").to("cm")
            Length(value=2.54, unit='cm')
            >>> Length(1, "in").to("mm")
            Length(value=25.4, unit='mm')
            >>> Length(1, "in").to(None)
            Length(value=96.0, unit=None)
            >>> Length(12, "pt").to("px")
            Length(value=16.0, unit='px')

        """
        return _convert(self, unit)

    @override
    def serialize(self) -> str:
        formatter = serialize.get_current_formatter()
        units: Iterator[utiltypes.LengthUnit | Literal["preserve"]] = (
            more_itertools.always_iterable(formatter.length_unit)
        )
        converted = self

        for unit in units:
            if unit == "preserve":
                break

            with contextlib.suppress(errors.SvgUnitConversionError):
                converted = self.to(unit)
                break

        value = serialize.serialize(
            converted.value, precision_group="coordinate"
        )

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


@parse.inline_args
class _Transformer(lark.Transformer[object, Length]):
    number = parse.FiniteFloat
    length = Length


LengthType: TypeAlias = Annotated[
    Length,
    parse.get_validator(grammar="length.lark", transformer=_Transformer()),
]
