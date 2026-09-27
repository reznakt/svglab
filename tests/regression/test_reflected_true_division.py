import pytest

import svglab


@pytest.mark.parametrize(
    "value", [svglab.Point(1, 4), svglab.Length(4), svglab.Angle(4)]
)
def test_number_divided_by_value_type_is_unsupported(
    value: object,
) -> None:
    with pytest.raises(TypeError):
        _ = 2 / value  # pyright: ignore[reportOperatorIssue]
