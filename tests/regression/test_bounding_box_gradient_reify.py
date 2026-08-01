import copy

import svglab
from tests import conftest


def test_bounding_box_gradient_is_left_alone() -> None:
    original = svglab.parse_svg("""
        <svg width="200" height="200">
            <g transform="translate(50, 50)">
                <linearGradient id="g" x1="0" y1="0" x2="1" y2="0">
                    <stop offset="0" stop-color="red"/>
                    <stop offset="1" stop-color="blue"/>
                </linearGradient>
                <rect width="100" height="100" fill="url(#g)"/>
            </g>
        </svg>
    """)
    reified = copy.deepcopy(original)

    reified.reify()

    assert reified.find(svglab.LinearGradient).gradientTransform is None
    conftest.assert_svg_visually_equal(original, reified)
