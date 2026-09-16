import copy

import pytest

from svglab import (
    Color,
    G,
    Length,
    Matrix,
    Rect,
    Rotate,
    Scale,
    SkewX,
    SkewY,
    Svg,
    Transform,
    Translate,
)
from tests.conftest import assert_svg_visually_equal


def _svg(transform: Transform, *, group: bool) -> Svg:
    rect = Rect(
        x=Length(10),
        y=Length(10),
        width=Length(30),
        height=Length(20),
        fill=Color("blue"),
    )

    child = rect

    if group:
        child = G().add_child(rect)

    child.transform = transform

    return Svg(width=Length(200), height=Length(200)).add_child(child)


@pytest.mark.parametrize("group", [False, True])
@pytest.mark.parametrize(
    "transform",
    [
        [SkewX(20)],
        [Translate(10, 20), SkewY(15)],
        [SkewX(20), Translate(10, 20)],
        [Rotate(35)],
        [Matrix(1, 0.4, 0.2, 1, 5, 5)],
    ],
)
def test_unsupported_transform_is_not_dropped(
    transform: Transform, *, group: bool
) -> None:
    # a rectangle has no attribute that could express a skew or a rotation,
    # so whatever cannot be folded into its geometry has to stay behind
    original = _svg(transform, group=group)
    reified = copy.deepcopy(original)

    reified.reify()

    assert reified.find(Rect).transform
    assert_svg_visually_equal(original, reified)


@pytest.mark.parametrize("group", [False, True])
@pytest.mark.parametrize(
    "transform",
    [
        [Scale(2, 3)],
        [Translate(10, 20), Scale(2, 3)],
        [Scale(2, 3), Translate(10, 20)],
        # a quarter turn swaps the extents, a mirror moves the anchor to
        # the opposite corner; both are kept inside the viewport here
        [Rotate(90, 100, 100), Scale(2, 3)],
        [Translate(100, 0), Scale(-1, 1)],
    ],
)
def test_axis_preserving_transform_is_absorbed(
    transform: Transform, *, group: bool
) -> None:
    original = _svg(transform, group=group)
    reified = copy.deepcopy(original)

    reified.reify()

    assert reified.find(Rect).transform is None
    assert_svg_visually_equal(original, reified)
