import pytest

from svglab import Length, LengthUnit


@pytest.mark.parametrize(
    ("value", "unit", "target", "expected"),
    [
        (1, "in", "cm", 2.54),
        (2.54, "cm", "in", 1),
        (1, "in", "mm", 25.4),
        (1, "in", "Q", 101.6),
        (10, "cm", "mm", 100),
        # the reference pixel is 1/96 in, so a point is 96/72 of one and a
        # pica is twelve points
        (1, "pc", "px", 16),
        (1, "pt", "px", 4 / 3),
        (1, "pc", "pt", 12),
        (1, None, "px", 1),
        (1, "mm", "Q", 4),
    ],
)
def test_length_conversion_rate(
    value: float, unit: LengthUnit, target: LengthUnit, expected: float
) -> None:
    assert Length(value, unit).to(target).value == pytest.approx(expected)
