import copy

import svglab
from tests import conftest


def _reify(markup: str) -> tuple[svglab.Svg, svglab.Svg]:
    original = svglab.parse_svg(markup)
    reified = copy.deepcopy(original)

    reified.reify()

    return original, reified


def test_bounding_box_gradient_is_left_alone() -> None:
    original, reified = _reify("""
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

    assert reified.find(svglab.LinearGradient).gradientTransform is None
    conftest.assert_svg_visually_equal(original, reified)


def test_bounding_box_pattern_is_left_alone() -> None:
    # the offset must not be a multiple of the tile size, or the shifted
    # tiling would be indistinguishable from the original
    original, reified = _reify("""
        <svg width="200" height="200">
            <g transform="translate(13, 7)">
                <pattern id="p" width="0.25" height="0.25">
                    <rect width="10" height="10" fill="red"/>
                </pattern>
                <rect width="100" height="100" fill="url(#p)"/>
            </g>
        </svg>
    """)

    assert reified.find(svglab.Pattern).patternTransform is None
    conftest.assert_svg_visually_equal(original, reified)
