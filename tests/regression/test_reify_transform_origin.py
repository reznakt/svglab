"""A `transform-origin` reification cannot read stops the transformation."""

import copy

import pytest

import svglab
from tests import conftest


L = svglab.Length
C = svglab.Color


def _svg(*children: svglab.Element) -> svglab.Svg:
    return svglab.Svg(width=L(200), height=L(200)).add_children(*children)


def _rect(**kwargs: object) -> svglab.Rect:
    kwargs.setdefault("x", L(5))
    kwargs.setdefault("y", L(5))
    kwargs.setdefault("width", L(40))
    kwargs.setdefault("height", L(30))
    kwargs.setdefault("fill", C("#3366cc"))

    return svglab.Rect(**kwargs)  # type: ignore[arg-type]


@pytest.mark.parametrize("origin", ["center", "50% 50%", "left top"])
def test_an_origin_that_cannot_be_read_stops_the_parent_too(
    origin: str,
) -> None:
    # reifying the element itself already declined; the transformation the
    # *parent* hands down went through the same decomposition unguarded, and
    # raised half way through the children
    rect = _rect(transform_origin=origin)
    group = svglab.G(transform=[svglab.Translate(10, 10)]).add_child(rect)
    original = _svg(group)
    reified = copy.deepcopy(original)

    reified.reify()

    assert conftest.transforms_left(reified)
    conftest.assert_svg_visually_equal(original, reified)


def test_a_nested_container_with_such_an_origin_is_left_alone() -> None:
    inner = svglab.G(transform_origin="center").add_child(_rect())
    outer = svglab.G(transform=[svglab.Scale(2)]).add_child(inner)
    original = _svg(outer)
    reified = copy.deepcopy(original)

    reified.reify()

    assert conftest.transforms_left(reified)
    conftest.assert_svg_visually_equal(original, reified)


def test_an_origin_in_lengths_is_still_folded_in() -> None:
    rect = _rect(transform_origin="10 20")
    group = svglab.G(transform=[svglab.Translate(10, 10)]).add_child(rect)
    original = _svg(group)
    reified = copy.deepcopy(original)

    reified.reify()

    assert not conftest.transforms_left(reified)
    conftest.assert_svg_visually_equal(original, reified)
