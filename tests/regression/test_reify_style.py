"""A `style` declaration overrides the attribute reification would rewrite.

So it is read the way the attribute would be, and a magnitude it declares is
resized in the declaration itself.
"""

import pytest

from svglab import (
    Color,
    Element,
    G,
    Length,
    LinearGradient,
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


@pytest.mark.parametrize("name", ["fill", "stroke"])
def test_a_paint_declared_in_a_style_is_resolved_like_the_attribute(
    name: str,
) -> None:
    # a gradient in user space pins the shape where it is, one in bounding
    # box units follows it
    pinned = _rect(style=f"{name}: url(#u)", transform=[Translate(5, 5)])
    following = _rect(
        style=f"{name}: url(#b)", transform=[Translate(5, 5)]
    )
    _svg(
        LinearGradient(id="u", gradientUnits="userSpaceOnUse"),
        LinearGradient(id="b"),
        pinned,
        following,
    )

    pinned.reify()
    following.reify()

    assert pinned.transform == [Translate(5, 5)]
    assert following.transform is None
    assert following.x == L(15)


@pytest.mark.parametrize(
    ("style", "resized"),
    [
        ("stroke-width: 3", "stroke-width: 6"),
        ("stroke-dasharray: 4 2", "stroke-dasharray: 8 4"),
        (
            "stroke-dasharray: 4 2; stroke-dashoffset: 2",
            "stroke-dasharray: 8 4; stroke-dashoffset: 4",
        ),
    ],
)
def test_a_stroke_magnitude_in_a_style_is_resized_in_the_declaration(
    style: str, resized: str
) -> None:
    scaled = _rect(
        stroke=Color("black"), style=style, transform=[Scale(2)]
    )
    moved = _rect(
        stroke=Color("black"), style=style, transform=[Translate(5, 5)]
    )
    _svg(scaled, moved)

    scaled.reify()
    moved.reify()

    assert scaled.transform is None
    assert scaled.width == L(80)
    assert scaled.style == resized

    assert moved.transform is None
    assert moved.x == L(15)
    assert moved.style == style


@pytest.mark.parametrize(
    ("style", "resized"),
    [
        ("font-size: 12px", "font-size: 24px"),
        ("letter-spacing: 2px", "letter-spacing: 4px"),
        ("word-spacing: 4px", "word-spacing: 8px"),
        ("kerning: 1", "kerning: 2"),
    ],
)
def test_a_font_magnitude_in_a_style_is_resized_in_the_declaration(
    style: str, resized: str
) -> None:
    text = Text(
        x=[L(10)],
        y=[L(20)],
        font_size=L(12),
        style=style,
        transform=[Scale(2)],
    )
    _svg(text)

    text.reify()

    assert text.transform is None
    assert text.x == [L(20)]
    assert text.style == resized


def test_a_font_shorthand_in_a_style_leaves_only_a_move() -> None:
    # the shorthand sets a font size reification does not read out of it
    scaled = Text(
        x=[L(10)],
        y=[L(20)],
        style="font: italic 12px serif",
        transform=[Scale(2)],
    )
    moved = Text(
        x=[L(10)],
        y=[L(20)],
        style="font: italic 12px serif",
        transform=[Translate(5, 5)],
    )
    _svg(scaled, moved)

    scaled.reify()
    moved.reify()

    assert scaled.transform == [Scale(2)]

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
    # the stroke width the rect inherits is written in a style on the group,
    # which is shared, so the resized value is written onto the rect
    rect = _rect(stroke=Color("black"), transform=[Scale(2)])
    _svg(G(style="stroke-width: 3").add_child(rect))

    rect.reify()

    assert rect.transform is None
    assert rect.stroke_width == L(6)


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
