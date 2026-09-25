import copy

import pytest

import svglab
from tests import conftest


def _svg(inner: svglab.Element, transform: svglab.Transform) -> svglab.Svg:
    return svglab.Svg(
        width=svglab.Length(200), height=svglab.Length(200)
    ).add_child(svglab.G(transform=transform).add_child(inner))


def _nested(*, viewbox: bool) -> svglab.Svg:
    inner = svglab.Svg(
        x=svglab.Length(10),
        y=svglab.Length(10),
        width=svglab.Length(60),
        height=svglab.Length(60),
        viewBox=(0, 0, 60, 60) if viewbox else None,
    )

    return inner.add_child(
        svglab.Rect(
            x=svglab.Length(10),
            y=svglab.Length(10),
            width=svglab.Length(30),
            height=svglab.Length(20),
            fill=svglab.Color("red"),
        )
    )


@pytest.mark.parametrize("viewbox", [False, True])
@pytest.mark.parametrize(
    "transform",
    [
        [svglab.Translate(20, 30)],
        [svglab.Translate(5, 5), svglab.Translate(10, 10)],
    ],
)
def test_a_nested_viewport_does_not_apply_the_transform_twice(
    transform: svglab.Transform, *, viewbox: bool
) -> None:
    # a nested `svg` has geometry of its own, so a transformation handed to it
    # must not also be handed to its content
    original = _svg(_nested(viewbox=viewbox), transform)
    reified = copy.deepcopy(original)

    reified.reify()

    conftest.assert_svg_visually_equal(original, reified)


def test_a_nested_viewport_is_resized_only_when_it_has_a_view_box() -> (
    None
):
    # without a view box the content keeps its own size, so resizing the
    # viewport would only reveal more of it
    without = _svg(_nested(viewbox=False), [svglab.Scale(1.5)])
    with_viewbox = _svg(_nested(viewbox=True), [svglab.Scale(1.5)])

    for svg in (without, with_viewbox):
        reified = copy.deepcopy(svg)
        reified.reify()
        conftest.assert_svg_visually_equal(svg, reified)

    reified_without = copy.deepcopy(without)
    reified_without.reify()
    assert conftest.transforms_left(reified_without)

    reified_with = copy.deepcopy(with_viewbox)
    reified_with.reify()
    assert not conftest.transforms_left(reified_with)


def test_the_outermost_svg_transforms_its_content() -> None:
    # `x`, `y`, `width` and `height` describe the canvas there, so the
    # transformation belongs to the children
    svg = svglab.Svg(
        width=svglab.Length(200),
        height=svglab.Length(200),
        transform=[svglab.Translate(20, 30)],
    ).add_child(
        svglab.Rect(
            x=svglab.Length(10),
            y=svglab.Length(10),
            width=svglab.Length(30),
            height=svglab.Length(20),
            fill=svglab.Color("red"),
        )
    )

    original = copy.deepcopy(svg)
    svg.reify()

    assert svg.transform is None
    assert svg.width == svglab.Length(200)
    assert svg.find(svglab.Rect).x == svglab.Length(30)

    conftest.assert_svg_visually_equal(original, svg)


def test_a_document_with_a_nested_viewport_survives_a_round_trip() -> None:
    # a nested `svg` establishes a viewport inside the document; it is not a
    # second root, and the parser has to read back what reification writes
    svg = _svg(_nested(viewbox=True), [svglab.Translate(20, 30)])
    svg.reify()

    xml = svg.to_xml()
    reparsed = svglab.parse_svg(xml)

    assert reparsed.to_xml() == xml
    assert len(list(reparsed.find_all(svglab.Svg))) == 1
