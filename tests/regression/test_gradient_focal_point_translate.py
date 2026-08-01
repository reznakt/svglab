import copy

import svglab
from tests import conftest


def _svg() -> svglab.Svg:
    return svglab.parse_svg("""
        <svg width="200" height="200">
            <defs>
                <radialGradient id="g" gradientUnits="userSpaceOnUse"
                                cx="50" cy="50" r="50" fx="70" fy="30"
                                gradientTransform="translate(100, 100)">
                    <stop offset="0" stop-color="red"/>
                    <stop offset="1" stop-color="blue"/>
                </radialGradient>
            </defs>
            <rect width="200" height="200" fill="url(#g)"/>
        </svg>
    """)


def test_focal_point_is_translated() -> None:
    original = _svg()
    reified = copy.deepcopy(original)

    reified.reify()
    gradient = reified.find(svglab.RadialGradient)

    assert gradient.cx == svglab.Length(150)
    assert gradient.cy == svglab.Length(150)
    assert gradient.fx == svglab.Length(170)
    assert gradient.fy == svglab.Length(130)

    conftest.assert_svg_visually_equal(original, reified)
