"""A text hands its transformation to its spans without resizing twice.

A text element draws glyphs itself and establishes the coordinate system its
spans are laid out in. When it absorbs a scaling it resizes the font size,
stroke width and dash pattern it uses, and spells them out on itself -- which
is what its spans then inherit. A span receiving the same scaling must
therefore resize only the magnitudes it spells out itself.
"""

import copy

from svglab import Length, Text, Tspan, parse_svg
from tests.conftest import assert_svg_visually_equal, transforms_left


def test_a_span_inherits_the_resized_font_size_once() -> None:
    original = parse_svg("""
        <svg width="200" height="200">
            <text x="10" y="60" font-size="10" transform="scale(2)">
                a<tspan>bbb</tspan><tspan font-size="8">c</tspan>
            </text>
        </svg>
    """)
    reified = copy.deepcopy(original)

    reified.reify()

    text = reified.find(Text)
    inheriting, own = reified.find_all(Tspan)

    assert not transforms_left(reified)
    assert text.font_size == Length(20)
    assert inheriting.font_size is None
    assert own.font_size == Length(16)
    assert_svg_visually_equal(original, reified, tolerance=1e-5)


def test_a_span_inherits_the_resized_stroke_once() -> None:
    original = parse_svg("""
        <svg width="200" height="200">
            <text x="10" y="60" font-size="12" stroke="black" stroke-width="1"
                  stroke-dasharray="2 1" transform="scale(2)">
                a<tspan>bbb</tspan>
            </text>
        </svg>
    """)
    reified = copy.deepcopy(original)

    reified.reify()

    text = reified.find(Text)
    span = reified.find(Tspan)

    assert not transforms_left(reified)
    assert text.stroke_width == Length(2)
    assert text.stroke_dasharray == [Length(4), Length(2)]
    assert span.stroke_width is None
    assert span.stroke_dasharray is None
    assert_svg_visually_equal(original, reified, tolerance=1e-5)


def test_a_text_reified_alone_still_finishes_its_spans() -> None:
    # a span cannot carry a transformation, so what the text hands down has
    # to be folded in even when nothing else below the text is touched
    original = parse_svg("""
        <svg width="200" height="200">
            <text x="10" y="60" font-size="12" transform="translate(10 0)">
                a<tspan x="40">bb</tspan>
            </text>
        </svg>
    """)
    reified = copy.deepcopy(original)

    reified.find(Text).reify(recursive=False)

    assert not transforms_left(reified)
    assert reified.find(Tspan).x == [Length(50)]
    assert_svg_visually_equal(original, reified)
