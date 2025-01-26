import functools
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


ConversionTable: TypeAlias = Mapping[tuple[_UnitT_co, _UnitT_co], float]
"""
A table of conversion rates between units.

The keys are tuples of the form `(source, target)`, where `source` is the
unit to convert from and `target` is the unit to convert to. The values are
the conversion rates.
"""

Converter: TypeAlias = Callable[[_HasUnitT, _UnitT_co], _HasUnitT]
"""A function that converts a value to a different unit."""


def _get_conversion_rate_helper(
    source: _UnitT_co,
    target: _UnitT_co,
    *,
    visited: set[_UnitT_co],
    conversion_table: ConversionTable[_UnitT_co],
) -> float | None:
    if source == target:
        return 1

    if (source, target) in conversion_table:
        return conversion_table[(source, target)]

    if (target, source) in conversion_table:
        return 1 / conversion_table[(target, source)]

    for (from_unit, to_unit), rate in conversion_table.items():
        if from_unit == source and to_unit not in visited:
            visited.add(to_unit)

            sub_rate = _get_conversion_rate_helper(
                to_unit,
                target,
                visited=visited,
                conversion_table=conversion_table,
            )

            if sub_rate is not None:
                return rate * sub_rate

        elif to_unit == source and from_unit not in visited:
            visited.add(from_unit)

            sub_rate = _get_conversion_rate_helper(
                from_unit,
                target,
                visited=visited,
                conversion_table=conversion_table,
            )

            if sub_rate is not None:
                return sub_rate / rate

    return None


def _get_conversion_rate(
    source: _UnitT_co,
    target: _UnitT_co,
    *,
    conversion_table: ConversionTable[_UnitT_co],
) -> float | None:
    """Get the conversion rate for conversion from `source` to `target`.

    Args:
        source: The source unit.
        target: The target unit.
        conversion_table: A table of conversion rates.

    Returns:
        The conversion rate for converting from `source` to `target`,
        or `None` if the conversion is not possible.

    Examples:
        >>> conversion_table = {
        ...     ("foo", "bar"): 2,
        ...     ("bar", "baz"): 4,
        ...     ("abc", "def"): 1,
        ... }
        >>> _get_conversion_rate(
        ...     "foo", "bar", conversion_table=conversion_table
        ... )
        2
        >>> _get_conversion_rate(
        ...     "foo", "baz", conversion_table=conversion_table
        ... )
        8
        >>> _get_conversion_rate(
        ...     "foo", "abc", conversion_table=conversion_table
        ... ) is None
        True


    """
    return _get_conversion_rate_helper(
        source, target, visited=set(), conversion_table=conversion_table
    )


def make_converter(
    conversion_table: ConversionTable[_UnitT_co],
) -> Converter[_HasUnitT, _UnitT_co]:
    """Create a converter function using the given conversion table.

    Args:
        conversion_table: A table of conversion rates.

    Returns:
        A converter function that can convert between units. The function
        accepts an object with a `value` and `unit` attribute, and a target
        unit. It returns a new object with the converted value and unit.
        If the conversion is not possible,
        a `SvgUnitConversionError` is raised.

    """

    @functools.cache
    def rate(source: _UnitT_co, target: _UnitT_co) -> float | None:
        return _get_conversion_rate(
            source, target, conversion_table=conversion_table
        )

    def convert(obj: _HasUnitT, unit: _UnitT_co) -> _HasUnitT:
        conversion_rate: float | None = rate(obj.unit, unit)

        if conversion_rate is None:
            raise errors.SvgUnitConversionError(
                original_unit=obj.unit, target_unit=unit
            )

        return type(obj)(obj.value * conversion_rate, unit)

    return convert
