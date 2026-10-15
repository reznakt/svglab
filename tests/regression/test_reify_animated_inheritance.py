"""An animation changes what the elements below its target inherit.

A motion animation moves its target outside the target's own transformation,
a motion path is followed as it is written, and an animated inherited
property such as a stroke width on a group has no fixed value a descendant
could spell out.
"""

import copy

from svglab import Path, Rect, parse_svg
from tests.conftest import transforms_left


def test_a_motion_animation_pins_its_target() -> None:
    svg = parse_svg("""
        <svg width="200" height="200">
            <g transform="scale(2)">
                <rect width="20" height="20">
                    <animateMotion path="M0 0 L50 0" dur="2s"/>
                </rect>
            </g>
        </svg>
    """)

    svg.reify()

    assert [type(e) for e in transforms_left(svg)] == [type(svg.find("g"))]


def test_a_motion_path_is_followed_as_written() -> None:
    svg = parse_svg("""
        <svg width="200" height="200"
             xmlns:xlink="http://www.w3.org/1999/xlink">
            <path id="track" d="M0 0 L50 0" fill="none"
                  transform="translate(20 20)"/>
            <rect width="20" height="20">
                <animateMotion dur="2s">
                    <mpath xlink:href="#track"/>
                </animateMotion>
            </rect>
        </svg>
    """)

    svg.reify()

    assert transforms_left(svg) == [svg.find(Path)]


def test_an_animated_inherited_property_keeps_a_descendant_from_resizing() -> (
    None
):
    original = parse_svg("""
        <svg width="200" height="200">
            <g stroke="black" stroke-width="2">
                <animate attributeName="stroke-width" to="10" dur="1s"/>
                <rect width="20" height="20" transform="scale(2)"/>
                <rect x="50" width="20" height="20"
                      transform="translate(5 5)"/>
            </g>
        </svg>
    """)
    reified = copy.deepcopy(original)

    reified.reify()

    scaled, moved = reified.find_all(Rect)

    assert transforms_left(reified) == [scaled]
    assert scaled.stroke_width is None
    assert moved.transform is None
