"""A container is still painted where it sits, even with no geometry."""

import copy

import pytest

from svglab import (
    Circle,
    ClipPath,
    Color,
    Defs,
    FuncIri,
    G,
    Length,
    Mask,
    Rect,
    Svg,
    Translate,
)
from tests.conftest import assert_svg_visually_equal, transforms_left


L = Length
C = Color


def _defs() -> Defs:
    clip = ClipPath(id="c", clipPathUnits="userSpaceOnUse")
    clip.add_child(Rect(x=L(10), y=L(10), width=L(60), height=L(60)))

    mask = Mask(
        id="m",
        maskUnits="userSpaceOnUse",
        x=L(0),
        y=L(0),
        width=L(200),
        height=L(200),
    )
    mask.add_child(
        Rect(x=L(10), y=L(10), width=L(60), height=L(60), fill=C("white"))
    )

    return Defs().add_children(clip, mask)


def _group(**kwargs: object) -> G:
    group = G(transform=[Translate(60, 40)], **kwargs)  # type: ignore[arg-type]

    return group.add_children(
        Rect(x=L(0), y=L(0), width=L(80), height=L(80), fill=C("#3366cc")),
        Circle(cx=L(20), cy=L(20), r=L(15), fill=C("#cc3366")),
    )


@pytest.mark.parametrize(
    "attrs",
    [
        {"clip_path": FuncIri(fragment="c")},
        {"mask": FuncIri(fragment="m")},
        {"style": "clip-path: url(#c)"},
    ],
    ids=["clip-path", "mask", "style"],
)
def test_a_group_in_user_space_keeps_what_its_content_is_cut_against(
    attrs: dict[str, object],
) -> None:
    # a `g` has no geometry to fold a transformation into, but a clip path or
    # a mask in user space is still resolved where the `g` sits -- handing
    # the transformation to the children slides them out from under it
    group = _group(**attrs)
    original = Svg(width=L(200), height=L(200)).add_children(
        _defs(), group
    )
    reified = copy.deepcopy(original)

    reified.reify()

    assert reified.find(G).transform
    assert_svg_visually_equal(original, reified)


def test_a_group_with_nothing_in_the_way_still_hands_it_down() -> None:
    original = Svg(width=L(200), height=L(200)).add_children(
        _defs(), _group()
    )
    reified = copy.deepcopy(original)

    reified.reify()

    assert not transforms_left(reified)
    assert_svg_visually_equal(original, reified)
