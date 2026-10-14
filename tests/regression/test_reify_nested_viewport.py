import copy

import pytest

from svglab import (
    Color,
    Element,
    G,
    Length,
    Rect,
    Scale,
    Svg,
    Transform,
    Translate,
    parse_svg,
)
from tests.conftest import assert_svg_visually_equal, transforms_left


def _svg(inner: Element, transform: Transform) -> Svg:
    return Svg(width=Length(200), height=Length(200)).add_child(
        G(transform=transform).add_child(inner)
    )


def _nested(*, viewbox: bool) -> Svg:
    inner = Svg(
        x=Length(10),
        y=Length(10),
        width=Length(60),
        height=Length(60),
        viewBox=(0, 0, 60, 60) if viewbox else None,
    )

    return inner.add_child(
        Rect(
            x=Length(10),
            y=Length(10),
            width=Length(30),
            height=Length(20),
            fill=Color("red"),
        )
    )


@pytest.mark.parametrize("viewbox", [False, True])
@pytest.mark.parametrize(
    "transform",
    [[Translate(20, 30)], [Translate(5, 5), Translate(10, 10)]],
)
def test_a_nested_viewport_does_not_apply_the_transform_twice(
    transform: Transform, *, viewbox: bool
) -> None:
    # a nested `svg` has geometry of its own, so a transformation handed to it
    # must not also be handed to its content
    original = _svg(_nested(viewbox=viewbox), transform)
    reified = copy.deepcopy(original)

    reified.reify()

    assert_svg_visually_equal(original, reified)


def test_a_nested_viewport_is_resized_only_when_it_has_a_view_box() -> (
    None
):
    # without a view box the content keeps its own size, so resizing the
    # viewport would only reveal more of it
    without = _svg(_nested(viewbox=False), [Scale(1.5)])
    with_viewbox = _svg(_nested(viewbox=True), [Scale(1.5)])

    for svg in (without, with_viewbox):
        reified = copy.deepcopy(svg)
        reified.reify()
        assert_svg_visually_equal(svg, reified)

    reified_without = copy.deepcopy(without)
    reified_without.reify()
    assert transforms_left(reified_without)

    reified_with = copy.deepcopy(with_viewbox)
    reified_with.reify()
    assert not transforms_left(reified_with)


def test_the_outermost_svg_transforms_its_content() -> None:
    # `x`, `y`, `width` and `height` describe the canvas there, so the
    # transformation belongs to the children
    svg = Svg(
        width=Length(200),
        height=Length(200),
        transform=[Translate(20, 30)],
    ).add_child(
        Rect(
            x=Length(10),
            y=Length(10),
            width=Length(30),
            height=Length(20),
            fill=Color("red"),
        )
    )

    original = copy.deepcopy(svg)
    svg.reify()

    assert svg.transform is None
    assert svg.width == Length(200)
    assert svg.find(Rect).x == Length(30)

    assert_svg_visually_equal(original, svg)


def test_a_document_with_a_nested_viewport_survives_a_round_trip() -> None:
    # a nested `svg` establishes a viewport inside the document; it is not a
    # second root, and the parser has to read back what reification writes
    svg = _svg(_nested(viewbox=True), [Translate(20, 30)])
    svg.reify()

    xml = svg.to_xml()
    reparsed = parse_svg(xml)

    assert reparsed.to_xml() == xml
    assert len(list(reparsed.find_all(Svg))) == 1
