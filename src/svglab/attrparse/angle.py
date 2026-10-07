"""Definition of the SVG `<angle>` type.

Use `Angle` to represent angles in SVG. Use `AngleType` in Pydantic fields.
"""

from __future__ import annotations

import math

import lark
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
from svglab.mixins import AddSub, FloatMulDiv
from svglab.models import DATACLASS_CONFIG, dataclass
from svglab.protocols import CustomSerializable
from svglab.serialize import serialize
from svglab.units import Converter, make_converter


AngleUnit: TypeAlias = Literal["deg", "grad", "rad", "turn"] | None

_convert: Final[Converter[Angle, AngleUnit]] = make_converter(
    conversion_table={
        ("deg", "grad"): 10 / 9,
        ("rad", "deg"): 180 / math.pi,
        ("turn", "deg"): 360,
        (None, "deg"): 1,
    }
)


@final
@dataclass(frozen=True, config=DATACLASS_CONFIG)
class Angle(
    AddSub["Angle"], FloatMulDiv, SupportsFloat, CustomSerializable
):
    """Represents the SVG `<angle>` type.

    An angle is a number optionally followed by a unit. Available units are:

    - `deg`: degrees
    - `grad`: gradians
    - `rad`: radians
    - `turn`: turns
    """

    value: float
    unit: AngleUnit = None

    def to(self, unit: AngleUnit) -> Angle:
        """Convert the angle to a different unit.

        Args:
            unit: The unit to convert to.

        Returns:
            A new `Angle` object with the converted value and new unit.

        Raises:
            SvgUnitConversionError: If the conversion is not possible.

        Examples:
            >>> angle = Angle(360, "deg")
            >>> angle.to("grad")
            Angle(value=400.0, unit='grad')

        """
        return _convert(self, unit)

    @override
    def serialize(self) -> str:
        value = serialize(self.value, precision_group="angle")
        return f"{value}{self.unit or ''}"

    @override
    def __add__(self, other: Angle) -> Self:
        other_value = other.to(self.unit).value

        return type(self)(value=self.value + other_value, unit=self.unit)

    @override
    def __mul__(self, other: float) -> Self:
        return type(self)(value=self.value * other, unit=self.unit)

    @override
    def __float__(self) -> float:
        return self.to(None).value


@inline_args
class _Transformer(lark.Transformer[object, Angle]):
    number = FiniteFloat
    angle = Angle


AngleType: TypeAlias = Annotated[
    Angle, get_validator(grammar="angle.lark", transformer=_Transformer())
]
