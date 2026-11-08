"""Rotations and skews, which the old reifier could never apply."""

import copy

import pytest

from svglab import (
    Color,
    Element,
    Length,
    Matrix,
    Path,
    PathData,
    Point,
    Polygon,
    Rect,
    Rotate,
    Scale,
    SkewX,
    SkewY,
    Svg,
    Transform,
    Translate,
    compose,
)
from tests.conftest import assert_svg_visually_equal


# replacing a rotated shape with an equivalent one in a new position
# antialiases differently, so an exact match is not on offer here
_TOLERANCE = 5e-5


def _svg(child: Element) -> Svg:
    return Svg(width=Length(200), height=Length(200)).add_child(child)


_TRANSFORMS = [
    [Rotate(25)],
    [Rotate(40, 60, 50)],
    [SkewX(20)],
    [SkewY(-15)],
    [Matrix(1.1, 0.2, -0.15, 0.9, 6, 4)],
    [Translate(8, 4), Rotate(15), Scale(1.2, 0.8), SkewX(10)],
]


@pytest.mark.parametrize("transform", _TRANSFORMS)
def test_a_path_absorbs_any_affine_transformation(
    transform: Transform,
) -> None:
    path = Path(
        d=PathData.from_str(
            "M 20,40 C 40,20 70,90 100,50 Q 110,30 70,80 T 30,90 Z"
        ),
        fill=Color("#00aaff"),
        transform=transform,
    )
    original = _svg(copy.deepcopy(path))

    reified = _svg(path)
    reified.reify()

    assert path.transform is None
    assert_svg_visually_equal(original, reified, tolerance=_TOLERANCE)


@pytest.mark.parametrize("transform", _TRANSFORMS)
def test_a_path_with_arcs_absorbs_any_affine_transformation(
    transform: Transform,
) -> None:
    # an affine map takes an ellipse to another ellipse, so an arc always has
    # an exact transformed form
    path = Path(
        d=PathData.from_str(
            "M 30,70 A 40 20 30 1 0 100,70 L 100,90 H 30 V 70 Z"
        ),
        fill=Color("#aa00ff"),
        transform=transform,
    )
    original = _svg(copy.deepcopy(path))

    reified = _svg(path)
    reified.reify()

    assert path.transform is None
    assert_svg_visually_equal(original, reified, tolerance=_TOLERANCE)


@pytest.mark.parametrize("transform", _TRANSFORMS[:2])
def test_a_matrix_is_no_harder_than_a_translation(
    transform: Transform,
) -> None:
    # the list is composed into a single matrix before anything else happens,
    # so a `matrix(...)` is reified like everything else
    polygon = Polygon(
        points=[
            Point(20, 30),
            Point(90, 20),
            Point(100, 80),
            Point(30, 90),
        ],
        fill=Color("#ffaa00"),
        transform=[compose(transform)],
    )
    original = _svg(copy.deepcopy(polygon))

    reified = _svg(polygon)
    reified.reify()

    assert polygon.transform is None
    assert_svg_visually_equal(original, reified, tolerance=_TOLERANCE)


def test_a_rect_takes_the_scaling_out_of_a_rotation() -> None:
    # the rectangle cannot turn, but it can still absorb the shape change
    # that survives the rotation
    rect = Rect(
        x=Length(20),
        y=Length(20),
        width=Length(30),
        height=Length(20),
        fill=Color("red"),
        transform=[Rotate(30), Scale(2, 3)],
    )
    original = _svg(copy.deepcopy(rect))

    reified = _svg(rect)
    reified.reify()

    assert rect.width == Length(60)
    assert rect.height == Length(60)
    assert rect.transform == [Rotate(30)]

    assert_svg_visually_equal(original, reified, tolerance=_TOLERANCE)
