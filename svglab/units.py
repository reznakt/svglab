"""Utilities for converting between units.

This module provides a way to convert between different units of measurement.

The main output of this module is the `make_converter` function, which creates
a converter function that can convert between units based on a conversion
table.

"""

import collections
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
_ConversionGraph: TypeAlias = Mapping[_UnitT_co, Mapping[_UnitT_co, float]]

ConversionTable: TypeAlias = Mapping[tuple[_UnitT_co, _UnitT_co], float]
"""
A table of conversion rates between units.

The keys are tuples of the form `(source, target)`, where `source` is the
unit to convert from and `target` is the unit to convert to. The values are
the conversion rates.
"""

Converter: TypeAlias = Callable[[_HasUnitT, _UnitT_co], _HasUnitT]
"""A function that converts a value to a different unit."""


def _table_to_graph(
    conversion_table: ConversionTable[_UnitT_co],
) -> _ConversionGraph[_UnitT_co]:
    graph = collections.defaultdict(dict)

    for (source, target), rate in conversion_table.items():
        graph[source][target] = rate
        graph[target][source] = 1 / rate

    return graph


def _get_conversion_rate(
    source: _UnitT_co,
    target: _UnitT_co,
    *,
    graph: _ConversionGraph[_UnitT_co],
) -> float | None:
    if source == target:
        return 1

    queue = collections.deque([(source, 1.0)])
    visited = {source}

    while queue:
        u, u_rate = queue.popleft()

        for v, v_rate in graph[u].items():
            if v in visited:
                continue

            rate = u_rate * v_rate

            if v == target:
                return rate

            queue.append((v, rate))
            visited.add(v)

    return None


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
    graph = _table_to_graph(conversion_table)

    @functools.cache
    def get_conversion_rate(
        source: _UnitT_co, target: _UnitT_co
    ) -> float | None:
        return _get_conversion_rate(source, target, graph=graph)

    def convert(obj: _HasUnitT, unit: _UnitT_co) -> _HasUnitT:
        conversion_rate: float | None = get_conversion_rate(obj.unit, unit)

        if conversion_rate is None:
            raise errors.SvgUnitConversionError(
                original_unit=obj.unit, target_unit=unit
            )

        return type(obj)(obj.value * conversion_rate, unit)

    return convert
