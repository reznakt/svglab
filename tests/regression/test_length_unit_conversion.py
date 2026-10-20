import pytest

from svglab import Length, LengthUnit, Svg


@pytest.mark.parametrize(
    ("value", "unit", "target", "expected"),
    [
        (1, "in", "cm", 2.54),
        (2.54, "cm", "in", 1),
        (1, "in", "mm", 25.4),
        (1, "in", "Q", 101.6),
        (10, "cm", "mm", 100),
        (1, "pc", "px", 16),
        (1, "pt", "px", 4 / 3),
        (1, None, "px", 1),
        (1, "mm", "Q", 4),
        (1, "in", "px", 96),
        (72, "pt", "in", 1),
        (6, "pc", "in", 1),
        (25.4, "mm", None, 96),
    ],
)
def test_length_conversion_rate(
    value: float, unit: LengthUnit, target: LengthUnit, expected: float
) -> None:
    assert Length(value, unit).to(target).value == pytest.approx(expected)


def test_physical_size_renders_at_96_dpi() -> None:
    svg = Svg(width=Length(210, "mm"), height=Length(1, "in"))

    assert svg.render().size == (794, 96)
