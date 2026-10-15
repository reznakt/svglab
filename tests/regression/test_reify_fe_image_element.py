"""An element drawn by `feImage` stays where it sits in user space."""

import copy

from svglab import Rect, parse_svg
from tests.conftest import assert_svg_visually_equal, transforms_left


def test_a_filter_drawing_an_element_pins_the_filtered_element() -> None:
    original = parse_svg("""
        <svg width="200" height="200">
            <defs>
                <circle id="dot" cx="60" cy="60" r="15" fill="blue"/>
                <filter id="f">
                    <feImage href="#dot"/>
                    <feMerge>
                        <feMergeNode/>
                        <feMergeNode in="SourceGraphic"/>
                    </feMerge>
                </filter>
            </defs>
            <rect x="40" y="40" width="80" height="80" fill="green"
                  filter="url(#f)" transform="translate(30 20)"/>
        </svg>
    """)
    reified = copy.deepcopy(original)

    reified.reify()

    assert transforms_left(reified) == [reified.find(Rect)]
    assert_svg_visually_equal(original, reified)
