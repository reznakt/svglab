"""Utilities for converting between units.

This module provides a way to convert between different units of measurement.

The main output of this module is the `make_converter` function, which creates
a converter function from the size of each unit, expressed in a common base
unit.

"""

import fractions
import itertools
from collections.abc import Callable, Mapping

from typing_extensions import (
    Final,
    LiteralString,
    Protocol,
    TypeAlias,
    TypeVar,
    runtime_checkable,
)

from svglab import errors


_Unit: TypeAlias = LiteralString | None
_UnitT_co = TypeVar("_UnitT_co", bound=_Unit, covariant=True)


@runtime_checkable
class _HasUnit(Protocol[_UnitT_co]):
    value: Final[float]
    unit: Final[_UnitT_co]

    def __init__(self, value: float, unit: _UnitT_co) -> None: ...


_HasUnitT = TypeVar("_HasUnitT", bound=_HasUnit[_Unit])

UnitScale: TypeAlias = Mapping[_UnitT_co, fractions.Fraction | float]
"""
The size of each unit, expressed in a common base unit.

A `Fraction` keeps the conversion rates between two rational sizes exact
until the rate is rounded to a float, so every such rate is the float nearest
to the true one. A float is for sizes that are not rational, such as a radian
in degrees.
"""

Converter: TypeAlias = Callable[[_HasUnitT, _UnitT_co], _HasUnitT]
"""A function that converts a value to a different unit."""


def make_converter(
    scale: UnitScale[_UnitT_co],
) -> Converter[_HasUnitT, _UnitT_co]:
    """Create a converter function from the size of each unit.

    Every unit in `scale` converts to every other one. A unit missing from
    `scale` converts only to itself.

    Args:
        scale: The size of each convertible unit, in a common base unit.

    Returns:
        A converter function that can convert between units. The function
        accepts an object with a `value` and `unit` attribute, and a target
        unit. It returns a new object with the converted value and unit.
        If the conversion is not possible,
        a `SvgUnitConversionError` is raised.

    """
    rates: dict[tuple[_Unit, _Unit], float] = {
        (source, target): float(scale[source] / scale[target])
        for source, target in itertools.product(scale, repeat=2)
    }

    def convert(obj: _HasUnitT, unit: _UnitT_co) -> _HasUnitT:
        if obj.unit == unit:
            return type(obj)(obj.value, unit)

        try:
            rate = rates[obj.unit, unit]
        except KeyError:
            raise errors.SvgUnitConversionError(
                original_unit=obj.unit, target_unit=unit
            ) from None

        return type(obj)(obj.value * rate, unit)

    return convert
