import pytest

from svglab import Color, Element, Length, Rect, Svg
from tests.conftest import assert_svg_visually_equal


def _rect(rx: float, ry: float) -> Rect:
    return Rect(
        x=Length(20),
        y=Length(20),
        width=Length(100),
        height=Length(60),
        rx=Length(rx),
        ry=Length(ry),
        fill=Color("blue"),
    )


@pytest.mark.parametrize(("rx", "ry"), [(200, 200), (100, 60), (51, 31)])
def test_oversized_radii_are_clamped(rx: float, ry: float) -> None:
    assert _rect(rx, ry).to_path_data() == _rect(50, 30).to_path_data()


@pytest.mark.parametrize(("rx", "ry"), [(200, 200), (10, 10), (100, 20)])
def test_rect_and_path_are_visually_equal(rx: float, ry: float) -> None:
    def svg(shape: Element) -> Svg:
        return Svg(width=Length(200), height=Length(200)).add_child(shape)

    rect = _rect(rx, ry)
    path = rect.to_path()

    assert_svg_visually_equal(svg(rect), svg(path))
