"""A stylesheet may set a property on any element, so it is unknown there.

A stylesheet rule beats a presentation attribute, and which elements it picks
out cannot be told without a CSS engine. A property a stylesheet declares is
therefore unknown on every element whose own `style` attribute does not
settle it, and an element is held to what it could do under any value.
"""

import copy

from svglab import Length, Path, Rect, parse_svg
from tests.conftest import assert_svg_visually_equal, transforms_left


def test_a_stylesheet_stroke_makes_every_shape_possibly_stroked() -> None:
    # the path absorbs no more than a similarity, and its stroke width is
    # resized, since the class may well stroke it
    original = parse_svg("""
        <svg width="200" height="200">
            <style>.s { fill: none; stroke: #000 }</style>
            <path class="s" d="M10 10 L40 80" transform="scale(4 1)"/>
            <path class="s" d="M10 10 L40 80" transform="scale(2)"/>
        </svg>
    """)
    reified = copy.deepcopy(original)

    reified.reify()

    stretched, scaled = reified.find_all(Path)

    assert transforms_left(reified) == [stretched]
    assert scaled.stroke_width == Length(2)
    assert_svg_visually_equal(original, reified)


def test_a_stylesheet_paint_is_judged_by_the_document_paint_servers() -> (
    None
):
    original = parse_svg("""
        <svg width="200" height="200">
            <style>.f { fill: url(#g) }</style>
            <linearGradient id="g" gradientUnits="userSpaceOnUse"
                            x1="0" x2="100">
                <stop offset="0" stop-color="red"/>
                <stop offset="1" stop-color="blue"/>
            </linearGradient>
            <rect class="f" width="80" height="80"
                  transform="translate(30 0)"/>
        </svg>
    """)
    reified = copy.deepcopy(original)

    reified.reify()

    assert transforms_left(reified) == [reified.find(Rect)]
    assert_svg_visually_equal(original, reified)


def test_an_inline_style_settles_what_a_stylesheet_leaves_open() -> None:
    # the class may stroke the rect, which rules out the stretch, but the
    # inline fill settles the paint, so the move goes through
    original = parse_svg("""
        <svg width="200" height="200">
            <style>.s { stroke: #000; fill: url(#g) }</style>
            <linearGradient id="g" gradientUnits="userSpaceOnUse"
                            x1="0" x2="100">
                <stop offset="0" stop-color="red"/>
                <stop offset="1" stop-color="blue"/>
            </linearGradient>
            <rect class="s" style="fill: red" width="40" height="40"
                  transform="translate(30 0) scale(2 1)"/>
        </svg>
    """)
    reified = copy.deepcopy(original)

    reified.reify()

    rect = reified.find(Rect)

    assert transforms_left(reified) == [rect]
    assert rect.x == Length(15)
    assert_svg_visually_equal(original, reified)
