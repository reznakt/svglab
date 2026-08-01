import pytest

import svglab


@pytest.mark.parametrize(
    ("value", "unit", "target", "expected"),
    [
        (1, "in", "cm", 2.54),
        (2.54, "cm", "in", 1),
        (1, "in", "mm", 25.4),
        (1, "in", "Q", 101.6),
        (10, "cm", "mm", 100),
        (1, "pc", "px", 15),
        (1, "pt", "px", 1.25),
        (1, None, "px", 1),
        (1, "mm", "Q", 4),
    ],
)
def test_length_conversion_rate(
    value: float,
    unit: svglab.LengthUnit,
    target: svglab.LengthUnit,
    expected: float,
) -> None:
    assert svglab.Length(value, unit).to(target).value == pytest.approx(
        expected
    )
