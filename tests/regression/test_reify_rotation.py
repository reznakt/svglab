"""Rotations and skews, which the old reifier could never apply."""

import copy

import pytest

import svglab
from tests import conftest


# replacing a rotated shape with an equivalent one in a new position
# antialiases differently, so an exact match is not on offer here
_TOLERANCE = 5e-5


def _svg(child: svglab.Element) -> svglab.Svg:
    return svglab.Svg(
        width=svglab.Length(200), height=svglab.Length(200)
    ).add_child(child)


_TRANSFORMS = [
    [svglab.Rotate(25)],
    [svglab.Rotate(40, 60, 50)],
    [svglab.SkewX(20)],
    [svglab.SkewY(-15)],
    [svglab.Matrix(1.1, 0.2, -0.15, 0.9, 6, 4)],
    [
        svglab.Translate(8, 4),
        svglab.Rotate(15),
        svglab.Scale(1.2, 0.8),
        svglab.SkewX(10),
    ],
]


@pytest.mark.parametrize("transform", _TRANSFORMS)
def test_a_path_absorbs_any_affine_transformation(
    transform: svglab.Transform,
) -> None:
    path = svglab.Path(
        d=svglab.PathData.from_str(
            "M 20,40 C 40,20 70,90 100,50 Q 110,30 70,80 T 30,90 Z"
        ),
        fill=svglab.Color("#00aaff"),
        transform=transform,
    )
    original = _svg(copy.deepcopy(path))

    reified = _svg(path)
    reified.reify()

    assert path.transform is None
    conftest.assert_svg_visually_equal(
        original, reified, tolerance=_TOLERANCE
    )


@pytest.mark.parametrize("transform", _TRANSFORMS)
def test_a_path_with_arcs_absorbs_any_affine_transformation(
    transform: svglab.Transform,
) -> None:
    # an affine map takes an ellipse to another ellipse, so an arc always has
    # an exact transformed form
    path = svglab.Path(
        d=svglab.PathData.from_str(
            "M 30,70 A 40 20 30 1 0 100,70 L 100,90 H 30 V 70 Z"
        ),
        fill=svglab.Color("#aa00ff"),
        transform=transform,
    )
    original = _svg(copy.deepcopy(path))

    reified = _svg(path)
    reified.reify()

    assert path.transform is None
    conftest.assert_svg_visually_equal(
        original, reified, tolerance=_TOLERANCE
    )


@pytest.mark.parametrize("transform", _TRANSFORMS[:2])
def test_a_matrix_is_no_harder_than_a_translation(
    transform: svglab.Transform,
) -> None:
    # the list is composed into a single matrix before anything else happens,
    # so a `matrix(...)` is reified like everything else
    polygon = svglab.Polygon(
        points=[
            svglab.Point(20, 30),
            svglab.Point(90, 20),
            svglab.Point(100, 80),
            svglab.Point(30, 90),
        ],
        fill=svglab.Color("#ffaa00"),
        transform=[svglab.compose(transform)],
    )
    original = _svg(copy.deepcopy(polygon))

    reified = _svg(polygon)
    reified.reify()

    assert polygon.transform is None
    conftest.assert_svg_visually_equal(
        original, reified, tolerance=_TOLERANCE
    )


def test_a_rect_takes_the_scaling_out_of_a_rotation() -> None:
    # the rectangle cannot turn, but it can still absorb the shape change
    # that survives the rotation
    rect = svglab.Rect(
        x=svglab.Length(20),
        y=svglab.Length(20),
        width=svglab.Length(30),
        height=svglab.Length(20),
        fill=svglab.Color("red"),
        transform=[svglab.Rotate(30), svglab.Scale(2, 3)],
    )
    original = _svg(copy.deepcopy(rect))

    reified = _svg(rect)
    reified.reify()

    assert rect.width == svglab.Length(60)
    assert rect.height == svglab.Length(60)
    assert rect.transform == [svglab.Rotate(30)]

    conftest.assert_svg_visually_equal(
        original, reified, tolerance=_TOLERANCE
    )
