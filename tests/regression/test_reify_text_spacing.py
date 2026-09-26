"""The spacing between glyphs is resized along with the glyphs themselves."""

import copy

import pytest

import svglab
from tests import conftest


L = svglab.Length


def _text(**kwargs: object) -> svglab.Text:
    kwargs.setdefault("x", [L(10)])
    kwargs.setdefault("y", [L(40)])
    kwargs.setdefault("font_size", L(12))

    return svglab.Text(**kwargs).add_child(  # type: ignore[arg-type]
        svglab.RawText("Hamburge fonstiv")
    )


def _svg(*children: svglab.Element) -> svglab.Svg:
    return svglab.Svg(width=L(200), height=L(200)).add_children(*children)


def test_glyph_spacing_is_scaled() -> None:
    original = _svg(
        _text(
            letter_spacing=L(2),
            word_spacing=L(5),
            kerning=L(1),
            transform=[svglab.Scale(2)],
        )
    )
    reified = copy.deepcopy(original)

    reified.reify()
    text = reified.find(svglab.Text)

    assert text.transform is None
    assert text.font_size == L(24)
    assert text.letter_spacing == L(4)
    assert text.word_spacing == L(10)
    assert text.kerning == L(2)

    conftest.assert_svg_visually_equal(original, reified)


def test_inherited_glyph_spacing_is_spelled_out() -> None:
    text = _text(transform=[svglab.Scale(2)])
    original = _svg(
        svglab.G(letter_spacing=L(3), word_spacing=L(4)).add_child(text)
    )
    reified = copy.deepcopy(original)

    reified.reify()
    text = reified.find(svglab.Text)
    group = reified.find(svglab.G)

    assert text.transform is None
    assert text.letter_spacing == L(6)
    assert text.word_spacing == L(8)
    assert group.letter_spacing == L(3)

    conftest.assert_svg_visually_equal(original, reified)


@pytest.mark.parametrize("spacing", ["normal", "auto"])
def test_spacing_left_to_the_font_is_left_alone(spacing: str) -> None:
    kwargs = (
        {"kerning": spacing}
        if spacing == "auto"
        else {"letter_spacing": spacing, "word_spacing": spacing}
    )
    original = _svg(_text(transform=[svglab.Scale(2)], **kwargs))
    reified = copy.deepcopy(original)

    reified.reify()
    text = reified.find(svglab.Text)

    assert text.transform is None
    for name, value in kwargs.items():
        assert getattr(text, name) == value

    conftest.assert_svg_visually_equal(original, reified)


def test_font_relative_spacing_keeps_the_scale() -> None:
    text = _text(letter_spacing=L(0.2, "em"), transform=[svglab.Scale(2)])
    _svg(text)

    text.reify()

    assert text.transform == [svglab.Scale(2)]
    assert text.letter_spacing == L(0.2, "em")
