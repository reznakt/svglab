"""An image has no outline to stroke, whatever stroke it inherits."""

import copy

from svglab import Image, parse_svg
from tests.conftest import assert_svg_visually_equal, transforms_left


def test_an_image_under_a_stroke_may_still_be_stretched() -> None:
    original = parse_svg("""
        <svg width="200" height="200">
            <g stroke="black" stroke-width="4">
                <image x="10" y="10" width="40" height="40"
                       preserveAspectRatio="none" transform="scale(3 2)"
                       href="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAgAAAAICAIAAABLbSncAAAAIElEQVR4nGNgYGD4z8CASbIwyEHY6ICFQY4Rl8TA6QAAyQsI6uMMKtQAAAAASUVORK5CYII="/>
            </g>
        </svg>
    """)
    reified = copy.deepcopy(original)

    reified.reify()

    assert not transforms_left(reified)
    assert reified.find(Image).stroke_width is None
    assert_svg_visually_equal(original, reified)
