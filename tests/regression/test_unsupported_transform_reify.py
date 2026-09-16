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

    assert reified.find(svglab.Rect).transform
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
