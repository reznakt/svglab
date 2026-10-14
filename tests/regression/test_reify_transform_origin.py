"""A `transform-origin` is resolved against the viewport, or stops everything.

`transform-box` is `view-box` for SVG elements, so a keyword or a percentage
in `transform-origin` is a point of the nearest viewport. Where the viewport's
size is not known, the origin cannot be taken apart, and the transformation
has to stay where it is -- on the element, and on every ancestor that would
have handed it down.
"""

import copy

import pytest

from svglab import (
    Color,
    Element,
    G,
    Length,
    Rect,
    Rotate,
    Scale,
    Svg,
    Translate,
)
from tests.conftest import assert_svg_visually_equal, transforms_left


L = Length
C = Color


def _svg(*children: Element) -> Svg:
    return Svg(width=L(200), height=L(200)).add_children(*children)


def _rect(**kwargs: object) -> Rect:
    kwargs.setdefault("x", L(5))
    kwargs.setdefault("y", L(5))
    kwargs.setdefault("width", L(40))
    kwargs.setdefault("height", L(30))
    kwargs.setdefault("fill", C("#3366cc"))

    return Rect(**kwargs)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    "origin",
    ["center", "50% 50%", "left top", "right", "bottom", "30px", "25% 10"],
)
def test_an_origin_relative_to_the_viewport_is_resolved(
    origin: str,
) -> None:
    # a small turn about any point of the viewport keeps a rect in the
    # middle of it in view
    rect = _rect(
        x=L(80), y=L(80), transform=[Rotate(10)], transform_origin=origin
    )
    original = _svg(G(transform=[Translate(10, 10)]).add_child(rect))
    reified = copy.deepcopy(original)

    reified.reify(convert_shapes_to_paths=True)

    assert not transforms_left(reified)
    assert reified.find(Rect, default=None) is None
    assert_svg_visually_equal(original, reified, tolerance=1e-5)


def test_the_outermost_svg_turns_about_its_center() -> None:
    original = Svg(
        width=L(200),
        height=L(200),
        viewBox=(20, 40, 100, 100),
        transform=[Scale(0.5)],
    ).add_child(_rect(x=L(60), y=L(80)))
    rect = original.find(Rect)
    reified = copy.deepcopy(original)

    reified.reify()

    # resvg 0.48 turns the root about the origin, so this is checked
    # algebraically: the rect sits halfway between its place and the center
    # (50, 50) of the viewBox's size
    assert not transforms_left(reified)
    assert reified.find(Rect).x == L(55)
    assert reified.find(Rect).y == L(65)
    assert rect.x == L(60)


@pytest.mark.parametrize("origin", ["center", "50% 50%"])
def test_an_origin_relative_to_an_unknown_viewport_stops_the_parent_too(
    origin: str,
) -> None:
    # the nested svg is sized relative to its parent, so nothing says how
    # big a percentage of it is; the transformation the parent hands down
    # goes through the same decomposition and has to stop as well
    rect = _rect(transform=[Rotate(30)], transform_origin=origin)
    inner = Svg(width=L(50, "%"), height=L(50, "%")).add_child(
        G(transform=[Translate(10, 10)]).add_child(rect)
    )
    original = _svg(inner)
    reified = copy.deepcopy(original)

    reified.reify()

    assert transforms_left(reified)
    assert_svg_visually_equal(original, reified)


def test_an_origin_without_a_transformation_is_dropped() -> None:
    # the origin did nothing, and would start to once the group's
    # transformation arrives
    rect = _rect(transform_origin="bottom right")
    inner = G(transform_origin="center").add_child(rect)
    original = _svg(G(transform=[Scale(2)]).add_child(inner))
    reified = copy.deepcopy(original)

    reified.reify()

    assert not transforms_left(reified)
    assert reified.find(Rect).transform_origin is None
    assert_svg_visually_equal(original, reified)


def test_an_origin_in_lengths_is_still_folded_in() -> None:
    rect = _rect(transform_origin="10 20")
    group = G(transform=[Translate(10, 10)]).add_child(rect)
    original = _svg(group)
    reified = copy.deepcopy(original)

    reified.reify()

    assert not transforms_left(reified)
    assert_svg_visually_equal(original, reified)
