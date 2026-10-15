"""A marker is sized in stroke widths whether or not the shape is stroked.

A `marker` in the default `markerUnits` is scaled by the `stroke-width` of
the shape carrying it, which has its initial value of one even where the
shape has no stroke. Resizing such a shape resizes its markers, so the
stroke width has to be written out and resized along with the geometry.
"""

import copy

from svglab import Length, Polyline, parse_svg
from tests.conftest import assert_svg_visually_equal, transforms_left


def test_an_unstroked_marked_shape_has_its_stroke_width_resized() -> None:
    original = parse_svg("""
        <svg width="200" height="200">
            <defs>
                <marker id="m" markerWidth="8" markerHeight="8" refX="4"
                        refY="4" orient="45" viewBox="0 0 10 10">
                    <path d="M1,1 L7,4 L1,7 z" fill="crimson"/>
                </marker>
            </defs>
            <g transform="scale(1.5)">
                <polyline points="20,30 60,80 100,40" fill="teal"
                          marker-end="url(#m)"/>
            </g>
        </svg>
    """)
    reified = copy.deepcopy(original)

    reified.reify()

    polyline = reified.find(Polyline)

    assert not transforms_left(reified)
    assert polyline.stroke_width == Length(1.5)
    assert_svg_visually_equal(original, reified, tolerance=1e-5)
