"""A `style` declaration overrides the attribute reification would rewrite."""

import pytest

import svglab
from svglab import reify


L = svglab.Length


def _rect(**kwargs: object) -> svglab.Rect:
    kwargs.setdefault("x", L(10))
    kwargs.setdefault("y", L(10))
    kwargs.setdefault("width", L(40))
    kwargs.setdefault("height", L(30))

    return svglab.Rect(**kwargs)  # type: ignore[arg-type]


def _svg(*children: svglab.Element) -> svglab.Svg:
    return svglab.Svg(width=L(200), height=L(200)).add_children(*children)


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
    rect = _rect(style=style, transform=[svglab.Translate(5, 5)])
    _svg(rect)

    rect.reify()

    assert rect.transform == [svglab.Translate(5, 5)]
    assert rect.x == L(10)


@pytest.mark.parametrize(
    "style",
    [
        "stroke-width: 3",
        "font-size: 12px",
        "stroke-dasharray: 4 2",
        "stroke-dashoffset: 2",
        "marker-end: url(#m)",
        "vector-effect: non-scaling-stroke",
    ],
)
def test_a_magnitude_in_a_style_leaves_only_a_move(style: str) -> None:
    # reification cannot resize what it cannot rewrite, so it does not resize
    # the geometry either
    scaled = _rect(style=style, transform=[svglab.Scale(2)])
    moved = _rect(style=style, transform=[svglab.Translate(5, 5)])
    _svg(scaled, moved)

    scaled.reify()
    moved.reify()

    assert scaled.transform == [svglab.Scale(2)]
    assert scaled.width == L(40)

    assert moved.transform is None
    assert moved.x == L(15)


def test_an_ordinary_style_does_not_stop_reification() -> None:
    rect = _rect(
        style="fill:#3366cc;fill-opacity:0.8;stroke:none",
        transform=[svglab.Scale(2)],
    )
    _svg(rect)

    rect.reify()

    assert rect.transform is None
    assert rect.width == L(80)


def test_a_stroke_declared_in_a_style_still_counts_as_a_stroke() -> None:
    # `style` wins over the presentation attribute, so the checks that decide
    # what is safe have to read it too
    rect = _rect(style="stroke: black", transform=[svglab.Scale(2, 3)])
    _svg(rect)

    rect.reify()

    assert rect.transform == [svglab.Scale(2, 3)]


def test_a_stylesheet_that_could_set_a_transform_stops_reification() -> (
    None
):
    stylesheet = svglab.Style()
    stylesheet.add_child(svglab.RawText(".a { transform: rotate(30deg) }"))

    rect = _rect(class_=["a"], transform=[svglab.Translate(5, 5)])
    svg = _svg(stylesheet, rect)

    svg.reify()

    assert rect.transform == [svglab.Translate(5, 5)]


def test_a_stylesheet_that_sets_nothing_geometric_is_harmless() -> None:
    stylesheet = svglab.Style()
    stylesheet.add_child(svglab.RawText(".a { fill: red; opacity: 0.5 }"))

    rect = _rect(class_=["a"], transform=[svglab.Translate(5, 5)])
    svg = _svg(stylesheet, rect)

    svg.reify()

    assert rect.transform is None
    assert rect.x == L(15)


def test_style_declarations_are_read_as_written() -> None:
    rect = _rect(style="fill: red; stroke-width: 4 !important;;")

    assert dict(reify.style_declarations(rect)) == {
        "fill": "red",
        "stroke-width": "4",
    }
