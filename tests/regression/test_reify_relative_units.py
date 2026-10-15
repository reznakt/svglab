"""A magnitude in a relative unit is resized by multiplying its number.

An element's own `font-size="2em"` is relative to its parent's font size,
which a transformation on the element leaves as it is, so the glyphs are
resized by writing `4em`. A value the element inherits has already been
computed against the ancestor's reference, so it has to be in user units
before it can be resized -- and a percentage of anything but the parent's
font size is of the viewport.
"""

import copy

from svglab import Length, Path, Rect, Svg, Text, parse_svg
from tests.conftest import assert_svg_visually_equal, transforms_left


def test_an_own_em_font_size_is_multiplied() -> None:
    original = parse_svg("""
        <svg width="200" height="200" font-size="10">
            <text x="10" y="50" font-size="2em" transform="scale(2)">Re</text>
            <text x="10" y="90" font-size="150%" transform="scale(2)">if</text>
        </svg>
    """)
    reified = copy.deepcopy(original)

    reified.reify()

    em, percent = reified.find_all(Text)

    assert not transforms_left(reified)
    assert em.font_size == Length(4, "em")
    assert percent.font_size == Length(300, "%")
    assert_svg_visually_equal(original, reified, tolerance=1e-5)


def test_an_inherited_em_font_size_only_lets_the_text_move() -> None:
    svg = parse_svg("""
        <svg width="200" height="200" font-size="10">
            <g font-size="2em">
                <text x="10" y="50" transform="scale(2)">Re</text>
            </g>
        </svg>
    """)

    svg.reify()

    assert transforms_left(svg) == [svg.find(Text)]


def test_an_own_em_stroke_width_is_multiplied() -> None:
    original = parse_svg("""
        <svg width="200" height="200" font-size="10">
            <path d="M10 10 L90 60" stroke="black" stroke-width="0.5em"
                  transform="scale(2)"/>
            <rect x="10" y="10" width="40" height="20" stroke="black"
                  stroke-width="5%" transform="scale(2)"/>
        </svg>
    """)
    reified = copy.deepcopy(original)

    reified.reify()

    assert transforms_left(reified) == [reified.find(Rect)]
    assert reified.find(Path).stroke_width == Length(1, "em")
    assert_svg_visually_equal(original, reified, tolerance=1e-5)


def test_an_extent_in_em_only_lets_a_box_move() -> None:
    # a box is mapped corner by corner, which needs numbers; a nested svg
    # as tall as six lines of text is only moved
    svg = parse_svg("""
        <svg width="200" height="200" font-size="10">
            <svg x="20" y="20" width="120" height="6.25em"
                 viewBox="0 0 30 30" preserveAspectRatio="none"
                 transform="scale(1.5) translate(10 0)">
                <rect x="5" y="5" width="20" height="20" fill="orange"/>
            </svg>
        </svg>
    """)
    nested = svg.find(Svg)

    svg.reify()

    assert transforms_left(svg) == [nested]
    # the move went in, the scale stayed
    assert nested.x == Length(30)
