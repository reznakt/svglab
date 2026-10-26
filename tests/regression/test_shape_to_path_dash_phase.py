"""The path a shape converts into is drawn in the same direction as the shape.

A dash pattern starts where the outline starts and follows it around, so the
path has to begin at the same point as the shape and run the same way: a
rect from its top-left corner clockwise, an ellipse from its rightmost point
in the positive angle direction. It has to be closed like the shape, too, or
a square cap sticks out on either side of where it starts.
"""

import pytest

from svglab import Circle, Color, Ellipse, Length, Rect, Svg
from tests.conftest import assert_svg_visually_equal


def _dashed_svg() -> Svg:
    return Svg(
        width=Length(200),
        height=Length(200),
        fill="none",
        stroke=Color("black"),
        stroke_width=Length(12),
        stroke_dasharray=[Length(40), Length(25)],
    )


def _square_capped_svg() -> Svg:
    return Svg(
        width=Length(200),
        height=Length(200),
        fill="none",
        stroke=Color("black"),
        stroke_width=Length(30),
        stroke_linecap="square",
    )


@pytest.mark.parametrize(
    "shape",
    [
        Circle(cx=Length(100), cy=Length(100), r=Length(60)),
        Ellipse(
            cx=Length(100), cy=Length(100), rx=Length(80), ry=Length(50)
        ),
        Rect(
            x=Length(30),
            y=Length(40),
            width=Length(140),
            height=Length(100),
        ),
        Rect(
            x=Length(30),
            y=Length(40),
            width=Length(140),
            height=Length(100),
            rx=Length(20),
        ),
    ],
    ids=["circle", "ellipse", "rect", "rounded-rect"],
)
def test_a_dashed_shape_and_its_path_are_dashed_alike(
    shape: Rect | Circle | Ellipse,
) -> None:
    original = _dashed_svg().add_child(shape)
    converted = _dashed_svg().add_child(shape.to_path())

    assert_svg_visually_equal(original, converted, tolerance=1e-5)


@pytest.mark.parametrize(
    "shape",
    [
        Circle(cx=Length(100), cy=Length(100), r=Length(60)),
        Ellipse(
            cx=Length(100), cy=Length(100), rx=Length(80), ry=Length(50)
        ),
    ],
    ids=["circle", "ellipse"],
)
def test_the_path_of_an_ellipse_is_closed(shape: Circle | Ellipse) -> None:
    original = _square_capped_svg().add_child(shape)
    converted = _square_capped_svg().add_child(shape.to_path())

    assert_svg_visually_equal(original, converted, tolerance=1e-5)
