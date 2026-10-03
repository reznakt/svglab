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
        (1, "pc", "px", 16),
        (1, "pt", "px", 4 / 3),
        (1, "pc", "pt", 12),
        (1, "in", "px", 96),
        (1, "in", None, 96),
        (1, "in", "pt", 72),
        (1, "in", "pc", 6),
        (2.54, "cm", "px", 96),
        (25.4, "mm", None, 96),
        (101.6, "Q", "px", 96),
        (72, "pt", "cm", 2.54),
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


def test_inch_holds_dpi_user_units() -> None:
    assert svglab.Length(1, "in").to(None).value == svglab.DPI


@pytest.mark.parametrize("unit", ["%", "em", "ex", "ch", "rem", "vw"])
def test_relative_units_do_not_convert_to_user_units(
    unit: svglab.LengthUnit,
) -> None:
    with pytest.raises(svglab.SvgUnitConversionError):
        svglab.Length(1, unit).to(None)


_ABSOLUTE_UNITS: list[svglab.LengthUnit] = [
    None,
    "px",
    "in",
    "cm",
    "mm",
    "Q",
    "pt",
    "pc",
]


@pytest.mark.parametrize("source", _ABSOLUTE_UNITS)
@pytest.mark.parametrize("via", _ABSOLUTE_UNITS)
@pytest.mark.parametrize("target", _ABSOLUTE_UNITS)
def test_conversion_does_not_depend_on_the_route(
    source: svglab.LengthUnit,
    via: svglab.LengthUnit,
    target: svglab.LengthUnit,
) -> None:
    length = svglab.Length(7.25, source)

    assert length.to(via).to(target).value == pytest.approx(
        length.to(target).value, rel=1e-15
    )
