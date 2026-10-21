import pytest
from typing_extensions import TypeVar

from svglab import Angle, Length, Point


_ValueT = TypeVar("_ValueT", Length, Angle, Point)


@pytest.mark.parametrize("value", [Point(1, 4), Length(4), Angle(4)])
def test_number_minus_value_type_is_unsupported(value: object) -> None:
    with pytest.raises(TypeError):
        _ = 2 - value  # pyright: ignore[reportOperatorIssue]


@pytest.mark.parametrize(
    ("left", "right", "expected"),
    [
        (Length(3), Length(5), Length(-2)),
        (Angle(3), Angle(5), Angle(-2)),
        (Point(3, 4), Point(5, 7), Point(-2, -3)),
    ],
)
def test_subtraction_of_the_same_type(
    left: _ValueT, right: _ValueT, expected: _ValueT
) -> None:
    assert left - right == expected
