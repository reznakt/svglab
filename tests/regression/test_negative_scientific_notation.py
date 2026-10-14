import pytest

from svglab import Length, Rect


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (-1e9, "-1e+09"),
        (1e9, "1e+09"),
        (-1234567.0, "-1.234567e+06"),
        (-1e-7, "-1e-07"),
        (1e-7, "1e-07"),
    ],
)
def test_scientific_notation_keeps_sign(
    value: float, expected: str
) -> None:
    rect = Rect(x=Length(value))

    assert rect.to_xml() == f'<rect x="{expected}"/>'
