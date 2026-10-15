"""The path a shape converts into is drawn in the same direction as the shape.

A dash pattern starts where the outline starts and follows it around, so the
path has to begin at the same point as the shape and run the same way: a
rect from its top-left corner clockwise, an ellipse from its rightmost point
in the positive angle direction.
"""

import pytest

from svglab import Circle, Ellipse, Length, Rect, Svg
from tests.conftest import assert_svg_visually_equal


_DASHED: dict[str, object] = {
    "fill": "none",
    "stroke": "black",
    "stroke_width": Length(12),
    "stroke_dasharray": [Length(40), Length(25)],
}


@pytest.mark.parametrize(
    "shape",
    [
        Circle(cx=Length(100), cy=Length(100), r=Length(60), **_DASHED),  # type: ignore[arg-type]
        Ellipse(
            cx=Length(100),
            cy=Length(100),
            rx=Length(80),
            ry=Length(50),
            **_DASHED,  # type: ignore[arg-type]
        ),
        Rect(
            x=Length(30),
            y=Length(40),
            width=Length(140),
            height=Length(100),
            **_DASHED,  # type: ignore[arg-type]
        ),
        Rect(
            x=Length(30),
            y=Length(40),
            width=Length(140),
            height=Length(100),
            rx=Length(20),
            **_DASHED,  # type: ignore[arg-type]
        ),
    ],
    ids=["circle", "ellipse", "rect", "rounded-rect"],
)
def test_a_dashed_shape_and_its_path_are_dashed_alike(
    shape: Rect | Circle | Ellipse,
) -> None:
    original = Svg(width=Length(200), height=Length(200)).add_child(shape)
    converted = Svg(width=Length(200), height=Length(200)).add_child(
        shape.to_path()
    )

    assert_svg_visually_equal(original, converted, tolerance=1e-5)
