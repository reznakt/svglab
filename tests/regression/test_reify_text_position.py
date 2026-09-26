"""A `text` without a position of its own is moved all the same."""

import copy

from svglab import (
    Element,
    G,
    Length,
    RawText,
    Scale,
    Svg,
    Text,
    Translate,
    Tspan,
)
from tests.conftest import assert_svg_visually_equal, transforms_left


L = Length


def _text(**kwargs: object) -> Text:
    kwargs.setdefault("font_size", L(12))

    return Text(**kwargs).add_child(  # type: ignore[arg-type]
        RawText("Hamburgefonstiv")
    )


def _svg(*children: Element) -> Svg:
    return Svg(width=L(200), height=L(200)).add_children(*children)


def test_text_without_a_position_is_translated() -> None:
    original = _svg(
        G(transform=[Translate(20, 150)]).add_children(
            _text(), _text(dy=[L(25)])
        )
    )
    reified = copy.deepcopy(original)

    reified.reify()
    first, second = reified.find_all(Text)

    assert transforms_left(reified) == []
    assert (first.x, first.y) == ([L(20)], [L(150)])
    assert (second.x, second.y, second.dy) == ([L(20)], [L(150)], [L(25)])

    assert_svg_visually_equal(original, reified)


def test_text_without_a_position_is_scaled_about_the_origin() -> None:
    original = _svg(_text(transform=[Scale(2)], dy=[L(20)]))
    reified = copy.deepcopy(original)

    reified.reify()
    text = reified.find(Text)

    assert text.transform is None
    assert (text.x, text.y, text.dy) == (None, None, [L(40)])

    assert_svg_visually_equal(original, reified)


def test_a_tspan_without_a_position_carries_on_after_the_text() -> None:
    tspan = Tspan().add_child(RawText(" fonstiv"))
    text = (
        Text(
            x=[L(10)],
            y=[L(20)],
            font_size=L(12),
            transform=[Translate(30, 40)],
        )
        .add_child(RawText("Hamburge"))
        .add_child(tspan)
    )
    original = _svg(text)
    reified = copy.deepcopy(original)

    reified.reify()
    tspan = reified.find(Tspan)

    assert transforms_left(reified) == []
    assert (tspan.x, tspan.y) == (None, None)

    assert_svg_visually_equal(original, reified)
