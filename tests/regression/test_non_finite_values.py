import math
from collections.abc import Callable

import pytest

from svglab import Angle, Length, Point, PrecisionInterval, Translate


def _point(value: float) -> Point:
    return Point(value, 0)


def _translate(value: float) -> Translate:
    return Translate(value, 0)


@pytest.mark.parametrize("value", [math.nan, math.inf, -math.inf])
@pytest.mark.parametrize("build", [Length, Angle, _point, _translate])
def test_value_types_reject_non_finite_numbers(
    build: Callable[[float], object], value: float
) -> None:
    with pytest.raises(ValueError, match="finite"):
        build(value)


def test_precision_interval_accepts_an_infinite_end() -> None:
    assert PrecisionInterval(0, math.inf, 2).end == math.inf
