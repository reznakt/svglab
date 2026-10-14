import pytest

from svglab import Angle, Length, Point


@pytest.mark.parametrize("value", [Point(1, 4), Length(4), Angle(4)])
def test_number_divided_by_value_type_is_unsupported(
    value: object,
) -> None:
    with pytest.raises(TypeError):
        _ = 2 / value  # pyright: ignore[reportOperatorIssue]
