"""A `style` declaration overrides the attribute reification would rewrite."""

import pytest

from svglab import (
    Color,
    Element,
    G,
    Length,
    RawText,
    Rect,
    Scale,
    Style,
    Svg,
    Text,
    Translate,
)
from svglab.reify import style_declarations


L = Length


def _rect(**kwargs: object) -> Rect:
    kwargs.setdefault("x", L(10))
    kwargs.setdefault("y", L(10))
    kwargs.setdefault("width", L(40))
    kwargs.setdefault("height", L(30))

    return Rect(**kwargs)  # type: ignore[arg-type]


def _svg(*children: Element) -> Svg:
    return Svg(width=L(200), height=L(200)).add_children(*children)


@pytest.mark.parametrize(
    "style",
    [
        "transform: rotate(45deg)",
        "transform-origin: 20px 20px",
        "clip-path: url(#c)",
        "mask: url(#m)",
        "filter: url(#f)",
        "fill: url(#g)",
        "stroke: url(#g)",
    ],
)
def test_a_style_that_decides_the_geometry_stops_reification(
    style: str,
) -> None:
    rect = _rect(style=style, transform=[Translate(5, 5)])
    _svg(rect)

    rect.reify()

    assert rect.transform == [Translate(5, 5)]
    assert rect.x == L(10)


@pytest.mark.parametrize(
    "style",
    [
        "stroke-width: 3",
        "stroke-dasharray: 4 2",
        "stroke-dasharray: 4 2; stroke-dashoffset: 2",
    ],
)
def test_a_stroke_magnitude_in_a_style_leaves_only_a_move(
    style: str,
) -> None:
    # reification cannot resize what it cannot rewrite, so it does not resize
    # the geometry either
    scaled = _rect(
        stroke=Color("black"), style=style, transform=[Scale(2)]
    )
    moved = _rect(
        stroke=Color("black"), style=style, transform=[Translate(5, 5)]
    )
    _svg(scaled, moved)

    scaled.reify()
    moved.reify()

    assert scaled.transform == [Scale(2)]
    assert scaled.width == L(40)

    assert moved.transform is None
    assert moved.x == L(15)


@pytest.mark.parametrize(
    "style",
    [
        "font-size: 12px",
        "font: italic 12px serif",
        "letter-spacing: 2px",
        "word-spacing: 4px",
        "kerning: 1",
    ],
)
def test_a_font_magnitude_in_a_style_leaves_only_a_move(
    style: str,
) -> None:
    scaled = Text(
        x=[L(10)],
        y=[L(20)],
        font_size=L(12),
        style=style,
        transform=[Scale(2)],
    )
    moved = Text(
        x=[L(10)],
        y=[L(20)],
        font_size=L(12),
        style=style,
        transform=[Translate(5, 5)],
    )
    _svg(scaled, moved)

    scaled.reify()
    moved.reify()

    assert scaled.transform == [Scale(2)]
    assert scaled.font_size == L(12)

    assert moved.transform is None
    assert moved.x == [L(15)]


def test_a_magnitude_in_a_style_the_element_does_not_use_is_harmless() -> (
    None
):
    # a rect has no glyphs to size and no stroke to widen
    rect = _rect(
        style="font-size: 12px; stroke-width: 3", transform=[Scale(2)]
    )
    _svg(rect)

    rect.reify()

    assert rect.transform is None
    assert rect.width == L(80)


def test_a_magnitude_in_an_ancestor_style_is_read_too() -> None:
    # the stroke width the rect inherits is written in a style, which cannot
    # be resized any more than the rect's own would be
    rect = _rect(stroke=Color("black"), transform=[Scale(2)])
    _svg(G(style="stroke-width: 3").add_child(rect))

    rect.reify()

    assert rect.transform == [Scale(2)]
    assert rect.stroke_width is None


def test_an_ordinary_style_does_not_stop_reification() -> None:
    rect = _rect(
        style="fill:#3366cc;fill-opacity:0.8;stroke:none",
        transform=[Scale(2)],
    )
    _svg(rect)

    rect.reify()

    assert rect.transform is None
    assert rect.width == L(80)


def test_a_stroke_declared_in_a_style_still_counts_as_a_stroke() -> None:
    # `style` wins over the presentation attribute, so the checks that decide
    # what is safe have to read it too
    rect = _rect(style="stroke: black", transform=[Scale(2, 3)])
    _svg(rect)

    rect.reify()

    assert rect.transform == [Scale(2, 3)]


def test_a_stylesheet_that_could_set_a_transform_stops_reification() -> (
    None
):
    stylesheet = Style()
    stylesheet.add_child(RawText(".a { transform: rotate(30deg) }"))

    rect = _rect(class_=["a"], transform=[Translate(5, 5)])
    svg = _svg(stylesheet, rect)

    svg.reify()

    assert rect.transform == [Translate(5, 5)]


def test_a_stylesheet_that_sets_nothing_geometric_is_harmless() -> None:
    stylesheet = Style()
    stylesheet.add_child(RawText(".a { fill: red; opacity: 0.5 }"))

    rect = _rect(class_=["a"], transform=[Translate(5, 5)])
    svg = _svg(stylesheet, rect)

    svg.reify()

    assert rect.transform is None
    assert rect.x == L(15)


def test_style_declarations_are_read_as_written() -> None:
    rect = _rect(style="fill: red; stroke-width: 4 !important;;")

    assert dict(style_declarations(rect)) == {
        "fill": "red",
        "stroke-width": "4",
    }
