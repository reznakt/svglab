"""Converting a basic shape to a path so it can absorb anything."""

import copy

import pytest

import svglab
from tests import conftest


_TOLERANCE = 5e-5


def _svg(child: svglab.Element) -> svglab.Svg:
    return svglab.Svg(
        width=svglab.Length(200), height=svglab.Length(200)
    ).add_child(child)


def _shapes() -> dict[str, svglab.Element]:
    return {
        "rect": svglab.Rect(
            x=svglab.Length(20),
            y=svglab.Length(20),
            width=svglab.Length(60),
            height=svglab.Length(40),
            fill=svglab.Color("#3366cc"),
        ),
        "rect-rounded": svglab.Rect(
            x=svglab.Length(20),
            y=svglab.Length(20),
            width=svglab.Length(60),
            height=svglab.Length(40),
            rx=svglab.Length(10),
            ry=svglab.Length(6),
            fill=svglab.Color("#3366cc"),
        ),
        "circle": svglab.Circle(
            cx=svglab.Length(60),
            cy=svglab.Length(60),
            r=svglab.Length(30),
            fill=svglab.Color("#cc3366"),
        ),
        "ellipse": svglab.Ellipse(
            cx=svglab.Length(60),
            cy=svglab.Length(60),
            rx=svglab.Length(40),
            ry=svglab.Length(20),
            fill=svglab.Color("#33cc66"),
        ),
    }


# transformations no basic shape can express, whichever one it is: a circle
# can still be rotated, and a rectangle can still be scaled along its axes
_BEYOND_EVERY_SHAPE = [
    [svglab.SkewX(20)],
    [svglab.SkewY(-15)],
    [svglab.Matrix(1.1, 0.2, -0.15, 0.9, 6, 4)],
    [svglab.Rotate(25), svglab.Scale(1.6, 0.7)],
]


@pytest.mark.parametrize("name", sorted(_shapes()))
@pytest.mark.parametrize("transform", _BEYOND_EVERY_SHAPE)
def test_a_shape_that_becomes_a_path_absorbs_everything(
    name: str, transform: svglab.Transform
) -> None:
    shape = _shapes()[name]
    shape.transform = transform
    original = _svg(copy.deepcopy(shape))

    reified = _svg(shape)
    reified.reify(convert_shapes_to_paths=True)

    assert reified.find(svglab.Path).transform is None
    conftest.assert_svg_visually_equal(
        original, reified, tolerance=_TOLERANCE
    )


@pytest.mark.parametrize("name", sorted(_shapes()))
@pytest.mark.parametrize("transform", _BEYOND_EVERY_SHAPE)
def test_a_shape_keeps_its_type_when_the_flag_is_off(
    name: str, transform: svglab.Transform
) -> None:
    shape = _shapes()[name]
    shape.transform = copy.deepcopy(transform)

    reified = _svg(shape)
    reified.reify()

    assert reified.find(svglab.Path, default=None) is None
    assert shape.transform


def test_a_shape_is_left_alone_when_the_path_would_not_help_either() -> (
    None
):
    # the clipping path is resolved in user space, so neither the rectangle
    # nor the path it would become may absorb anything
    clip = svglab.ClipPath(id="c").add_child(
        svglab.Circle(
            cx=svglab.Length(50), cy=svglab.Length(40), r=svglab.Length(25)
        )
    )
    rect = svglab.Rect(
        x=svglab.Length(20),
        y=svglab.Length(20),
        width=svglab.Length(60),
        height=svglab.Length(40),
        clip_path=clip.get_func_iri(),
        transform=[svglab.Rotate(25)],
    )
    svg = svglab.Svg(
        width=svglab.Length(200), height=svglab.Length(200)
    ).add_children(svglab.Defs().add_child(clip), rect)

    svg.reify(convert_shapes_to_paths=True)

    assert svg.find(svglab.Rect) is rect
    assert rect.transform == [svglab.Rotate(25)]


def test_a_shape_that_becomes_a_path_keeps_its_presentation_attrs() -> (
    None
):
    rect = svglab.Rect(
        id="box",
        x=svglab.Length(20),
        y=svglab.Length(20),
        width=svglab.Length(60),
        height=svglab.Length(40),
        fill=svglab.Color("red"),
        stroke=svglab.Color("black"),
        stroke_width=svglab.Length(3),
        transform=[svglab.Rotate(25)],
    )
    original = _svg(copy.deepcopy(rect))

    reified = _svg(rect)
    reified.reify(convert_shapes_to_paths=True)

    path = reified.find(svglab.Path)

    assert path.id == "box"
    assert path.fill == svglab.Color("red")
    assert path.stroke_width == svglab.Length(3)

    conftest.assert_svg_visually_equal(
        original, reified, tolerance=_TOLERANCE
    )
