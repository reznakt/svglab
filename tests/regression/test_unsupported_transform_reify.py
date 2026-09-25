import copy

import pytest

import svglab
from tests import conftest


def _svg(transform: svglab.Transform, *, group: bool) -> svglab.Svg:
    rect = svglab.Rect(
        x=svglab.Length(10),
        y=svglab.Length(10),
        width=svglab.Length(30),
        height=svglab.Length(20),
        fill=svglab.Color("blue"),
    )

    child = rect

    if group:
        child = svglab.G().add_child(rect)

    child.transform = transform

    return svglab.Svg(
        width=svglab.Length(200), height=svglab.Length(200)
    ).add_child(child)


@pytest.mark.parametrize("group", [False, True])
@pytest.mark.parametrize(
    "transform",
    [
        [svglab.SkewX(20)],
        [svglab.Translate(10, 20), svglab.SkewY(15)],
        [svglab.SkewX(20), svglab.Translate(10, 20)],
        [svglab.Rotate(35)],
        [svglab.Matrix(1, 0.4, 0.2, 1, 5, 5)],
    ],
)
def test_unsupported_transform_is_not_dropped(
    transform: svglab.Transform, *, group: bool
) -> None:
    # a rectangle has no attribute that could express a skew or a rotation,
    # so whatever cannot be folded into its geometry has to stay behind
    original = _svg(transform, group=group)
    reified = copy.deepcopy(original)

    reified.reify()

    assert conftest.transforms_left(reified)
    conftest.assert_svg_visually_equal(original, reified)


@pytest.mark.parametrize("group", [False, True])
@pytest.mark.parametrize(
    "transform",
    [
        [svglab.Scale(2, 3)],
        [svglab.Translate(10, 20), svglab.Scale(2, 3)],
        [svglab.Scale(2, 3), svglab.Translate(10, 20)],
        # a quarter turn swaps the extents, a mirror moves the anchor to
        # the opposite corner; both are kept inside the viewport here
        [svglab.Rotate(90, 100, 100), svglab.Scale(2, 3)],
        [svglab.Translate(100, 0), svglab.Scale(-1, 1)],
    ],
)
def test_axis_preserving_transform_is_absorbed(
    transform: svglab.Transform, *, group: bool
) -> None:
    original = _svg(transform, group=group)
    reified = copy.deepcopy(original)

    reified.reify()

    assert reified.find(svglab.Rect).transform is None
    conftest.assert_svg_visually_equal(original, reified)


def test_a_group_keeps_the_leftover_once_instead_of_on_every_child() -> (
    None
):
    # handing a group's transformation to children that cannot absorb it
    # writes the leftover onto every one of them, where it started out
    # written once -- reification is supposed to remove transformations, not
    # multiply them
    group = svglab.G(transform=[svglab.SkewX(20)])

    for i in range(10):
        group.add_child(
            svglab.Text(
                x=[svglab.Length(10 * i)],
                y=[svglab.Length(20)],
                font_size=svglab.Length(8),
            ).add_child(svglab.RawText("x"))
        )

    original = svglab.Svg(
        width=svglab.Length(200), height=svglab.Length(200)
    ).add_child(group)
    reified = copy.deepcopy(original)

    reified.reify()

    assert len(conftest.transforms_left(reified)) == 1
    conftest.assert_svg_visually_equal(original, reified)
