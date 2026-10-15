"""The path a shape converts into draws exactly what the shape drew.

A rect without an extent, or an ellipse without a radius, is not rendered at
all, so its path has to be empty rather than a stroked sliver. An ellipse
with one radius takes the other from it, as SVG 2 has it.
"""

import pytest

from svglab import Circle, Color, Ellipse, Length, PathData, Rect, Svg
from tests.conftest import assert_svg_visually_equal


@pytest.mark.parametrize(
    "shape",
    [
        Rect(width=Length(0), height=Length(30), stroke=Color("black")),
        Rect(width=Length(30), height=Length(0), stroke=Color("black")),
        Circle(r=Length(0), stroke=Color("black")),
        Ellipse(rx=Length(0), ry=Length(20), stroke=Color("black")),
    ],
    ids=["rect-no-width", "rect-no-height", "circle", "ellipse"],
)
def test_a_shape_of_no_size_converts_to_an_empty_path(
    shape: Rect | Circle | Ellipse,
) -> None:
    assert shape.to_path_data() == PathData()


def test_an_ellipse_with_one_radius_takes_the_other_from_it() -> None:
    ellipse = Ellipse(
        cx=Length(100),
        cy=Length(100),
        rx=Length(40),
        fill="none",
        stroke=Color("black"),
        stroke_width=Length(6),
    )
    original = Svg(width=Length(200), height=Length(200)).add_child(
        ellipse
    )
    converted = Svg(width=Length(200), height=Length(200)).add_child(
        ellipse.to_path()
    )

    assert_svg_visually_equal(original, converted, tolerance=1e-5)
