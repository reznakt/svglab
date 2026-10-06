"""A container is still painted where it sits, even with no geometry."""

import copy

import pytest

import svglab
from tests import conftest


L = svglab.Length
C = svglab.Color


def _defs() -> svglab.Defs:
    clip = svglab.ClipPath(id="c", clipPathUnits="userSpaceOnUse")
    clip.add_child(
        svglab.Rect(x=L(10), y=L(10), width=L(60), height=L(60))
    )

    mask = svglab.Mask(
        id="m",
        maskUnits="userSpaceOnUse",
        x=L(0),
        y=L(0),
        width=L(200),
        height=L(200),
    )
    mask.add_child(
        svglab.Rect(
            x=L(10), y=L(10), width=L(60), height=L(60), fill=C("white")
        )
    )

    return svglab.Defs().add_children(clip, mask)


def _group(**kwargs: object) -> svglab.G:
    group = svglab.G(transform=[svglab.Translate(60, 40)], **kwargs)  # type: ignore[arg-type]

    return group.add_children(
        svglab.Rect(
            x=L(0), y=L(0), width=L(80), height=L(80), fill=C("#3366cc")
        ),
        svglab.Circle(cx=L(20), cy=L(20), r=L(15), fill=C("#cc3366")),
    )


@pytest.mark.parametrize(
    "attrs",
    [
        {"clip_path": svglab.FuncIri(fragment="c")},
        {"mask": svglab.FuncIri(fragment="m")},
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
    original = svglab.Svg(width=L(200), height=L(200)).add_children(
        _defs(), group
    )
    reified = copy.deepcopy(original)

    reified.reify()

    assert reified.find(svglab.G).transform
    conftest.assert_svg_visually_equal(original, reified)


def test_a_group_with_nothing_in_the_way_still_hands_it_down() -> None:
    original = svglab.Svg(width=L(200), height=L(200)).add_children(
        _defs(), _group()
    )
    reified = copy.deepcopy(original)

    reified.reify()

    assert not conftest.transforms_left(reified)
    conftest.assert_svg_visually_equal(original, reified)
