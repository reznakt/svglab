import pytest

import svglab
from tests import conftest


def _rect(rx: float, ry: float) -> svglab.Rect:
    return svglab.Rect(
        x=svglab.Length(20),
        y=svglab.Length(20),
        width=svglab.Length(100),
        height=svglab.Length(60),
        rx=svglab.Length(rx),
        ry=svglab.Length(ry),
        fill=svglab.Color("blue"),
    )


@pytest.mark.parametrize(("rx", "ry"), [(200, 200), (100, 60), (51, 31)])
def test_oversized_radii_are_clamped(rx: float, ry: float) -> None:
    assert _rect(rx, ry).to_path_data() == _rect(50, 30).to_path_data()


@pytest.mark.parametrize(("rx", "ry"), [(200, 200), (10, 10), (100, 20)])
def test_rect_and_path_are_visually_equal(rx: float, ry: float) -> None:
    def svg(shape: svglab.Element) -> svglab.Svg:
        return svglab.Svg(
            width=svglab.Length(200), height=svglab.Length(200)
        ).add_child(shape)

    rect = _rect(rx, ry)
    path = rect.to_path()

    conftest.assert_svg_visually_equal(svg(rect), svg(path))
