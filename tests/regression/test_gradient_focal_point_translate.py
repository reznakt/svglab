import copy

from svglab import Length, RadialGradient, Svg, parse_svg
from tests.conftest import assert_svg_visually_equal


def _svg() -> Svg:
    return parse_svg("""
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
    gradient = reified.find(RadialGradient)

    assert gradient.cx == Length(150)
    assert gradient.cy == Length(150)
    assert gradient.fx == Length(170)
    assert gradient.fy == Length(130)

    assert_svg_visually_equal(original, reified)


def test_half_set_focal_point_is_translated_once() -> None:
    original = parse_svg("""
        <svg width="200" height="200">
            <defs>
                <radialGradient id="g" gradientUnits="userSpaceOnUse"
                                cx="50" cy="50" r="50" fx="70"
                                gradientTransform="translate(100, 100)">
                    <stop offset="0" stop-color="red"/>
                    <stop offset="1" stop-color="blue"/>
                </radialGradient>
            </defs>
            <rect width="200" height="200" fill="url(#g)"/>
        </svg>
    """)
    reified = copy.deepcopy(original)

    reified.reify()
    gradient = reified.find(RadialGradient)

    assert gradient.fx == Length(170)
    assert gradient.fy == Length(150)

    assert_svg_visually_equal(original, reified)
