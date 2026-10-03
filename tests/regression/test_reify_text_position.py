"""A `text` without a position of its own is moved all the same."""

import copy

import svglab
from tests import conftest


L = svglab.Length


def _text(**kwargs: object) -> svglab.Text:
    kwargs.setdefault("font_size", L(12))

    return svglab.Text(**kwargs).add_child(  # type: ignore[arg-type]
        svglab.RawText("Hamburgefonstiv")
    )


def _svg(*children: svglab.Element) -> svglab.Svg:
    return svglab.Svg(width=L(200), height=L(200)).add_children(*children)


def test_text_without_a_position_is_translated() -> None:
    original = _svg(
        svglab.G(transform=[svglab.Translate(20, 150)]).add_children(
            _text(), _text(dy=[L(25)])
        )
    )
    reified = copy.deepcopy(original)

    reified.reify()
    first, second = reified.find_all(svglab.Text)

    assert conftest.transforms_left(reified) == []
    assert (first.x, first.y) == ([L(20)], [L(150)])
    assert (second.x, second.y, second.dy) == ([L(20)], [L(150)], [L(25)])

    conftest.assert_svg_visually_equal(original, reified)


def test_text_without_a_position_is_scaled_about_the_origin() -> None:
    original = _svg(_text(transform=[svglab.Scale(2)], dy=[L(20)]))
    reified = copy.deepcopy(original)

    reified.reify()
    text = reified.find(svglab.Text)

    assert text.transform is None
    assert (text.x, text.y, text.dy) == (None, None, [L(40)])

    conftest.assert_svg_visually_equal(original, reified)


def test_a_tspan_without_a_position_carries_on_after_the_text() -> None:
    tspan = svglab.Tspan().add_child(svglab.RawText(" fonstiv"))
    text = (
        svglab.Text(
            x=[L(10)],
            y=[L(20)],
            font_size=L(12),
            transform=[svglab.Translate(30, 40)],
        )
        .add_child(svglab.RawText("Hamburge"))
        .add_child(tspan)
    )
    original = _svg(text)
    reified = copy.deepcopy(original)

    reified.reify()
    tspan = reified.find(svglab.Tspan)

    assert conftest.transforms_left(reified) == []
    assert (tspan.x, tspan.y) == (None, None)

    conftest.assert_svg_visually_equal(original, reified)
