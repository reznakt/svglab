"""Converting a basic shape to a path so it can absorb anything."""

import copy

import pytest

from svglab import (
    Animate,
    Circle,
    ClipPath,
    Color,
    Defs,
    Element,
    Ellipse,
    G,
    Length,
    Matrix,
    Path,
    RawText,
    Rect,
    Rotate,
    Scale,
    SkewX,
    SkewY,
    Svg,
    Title,
    Transform,
)
from tests.conftest import assert_svg_visually_equal, transforms_left


_TOLERANCE = 5e-5


def _svg(child: Element) -> Svg:
    return Svg(width=Length(200), height=Length(200)).add_child(child)


def _shapes() -> dict[str, Element]:
    return {
        "rect": Rect(
            x=Length(20),
            y=Length(20),
            width=Length(60),
            height=Length(40),
            fill=Color("#3366cc"),
        ),
        "rect-rounded": Rect(
            x=Length(20),
            y=Length(20),
            width=Length(60),
            height=Length(40),
            rx=Length(10),
            ry=Length(6),
            fill=Color("#3366cc"),
        ),
        "circle": Circle(
            cx=Length(60),
            cy=Length(60),
            r=Length(30),
            fill=Color("#cc3366"),
        ),
        "ellipse": Ellipse(
            cx=Length(60),
            cy=Length(60),
            rx=Length(40),
            ry=Length(20),
            fill=Color("#33cc66"),
        ),
    }


# transformations no basic shape can express, whichever one it is: a circle
# can still be rotated, and a rectangle can still be scaled along its axes
_BEYOND_EVERY_SHAPE = [
    [SkewX(20)],
    [SkewY(-15)],
    [Matrix(1.1, 0.2, -0.15, 0.9, 6, 4)],
    [Rotate(25), Scale(1.6, 0.7)],
]


@pytest.mark.parametrize("name", sorted(_shapes()))
@pytest.mark.parametrize("transform", _BEYOND_EVERY_SHAPE)
def test_a_shape_that_becomes_a_path_absorbs_everything(
    name: str, transform: Transform
) -> None:
    shape = _shapes()[name]
    shape.transform = transform
    original = _svg(copy.deepcopy(shape))

    reified = _svg(shape)
    reified.reify(convert_shapes_to_paths=True)

    assert reified.find(Path).transform is None
    assert_svg_visually_equal(original, reified, tolerance=_TOLERANCE)


@pytest.mark.parametrize("name", sorted(_shapes()))
@pytest.mark.parametrize("transform", _BEYOND_EVERY_SHAPE)
def test_a_shape_keeps_its_type_when_the_flag_is_off(
    name: str, transform: Transform
) -> None:
    shape = _shapes()[name]
    shape.transform = copy.deepcopy(transform)

    reified = _svg(shape)
    reified.reify()

    assert reified.find(Path, default=None) is None
    assert shape.transform


def test_a_shape_is_left_alone_when_the_path_would_not_help_either() -> (
    None
):
    # the clipping path is resolved in user space, so neither the rectangle
    # nor the path it would become may absorb anything
    clip = ClipPath(id="c").add_child(
        Circle(cx=Length(50), cy=Length(40), r=Length(25))
    )
    rect = Rect(
        x=Length(20),
        y=Length(20),
        width=Length(60),
        height=Length(40),
        clip_path=clip.get_func_iri(),
        transform=[Rotate(25)],
    )
    svg = Svg(width=Length(200), height=Length(200)).add_children(
        Defs().add_child(clip), rect
    )

    svg.reify(convert_shapes_to_paths=True)

    assert svg.find(Rect) is rect
    assert rect.transform == [Rotate(25)]


def test_a_shape_that_becomes_a_path_keeps_its_presentation_attrs() -> (
    None
):
    rect = Rect(
        id="box",
        x=Length(20),
        y=Length(20),
        width=Length(60),
        height=Length(40),
        fill=Color("red"),
        stroke=Color("black"),
        stroke_width=Length(3),
        transform=[Rotate(25)],
    )
    original = _svg(copy.deepcopy(rect))

    reified = _svg(rect)
    reified.reify(convert_shapes_to_paths=True)

    path = reified.find(Path)

    assert path.id == "box"
    assert path.fill == Color("red")
    assert path.stroke_width == Length(3)

    assert_svg_visually_equal(original, reified, tolerance=_TOLERANCE)


def test_an_animated_shape_stays_a_shape() -> None:
    # a path has no `x` for the animation to animate
    rect = Rect(
        x=Length(20),
        y=Length(20),
        width=Length(60),
        height=Length(40),
        transform=[Rotate(25)],
    ).add_child(Animate(attributeName="x", to="50", dur="1s"))
    svg = _svg(rect)

    svg.reify(convert_shapes_to_paths=True)

    assert svg.find(Rect) is rect
    assert rect.transform == [Rotate(25)]


def test_a_shape_that_becomes_a_path_keeps_its_children() -> None:
    rect = Rect(
        x=Length(20),
        y=Length(20),
        width=Length(60),
        height=Length(40),
        transform=[Rotate(25)],
    ).add_child(Title().add_child(RawText("a box")))
    svg = _svg(rect)

    svg.reify(convert_shapes_to_paths=True)
    path = svg.find(Path)
    title = path.find(Title)

    assert path.transform is None
    assert title.parent is path
    assert list(svg.find_all(Rect)) == []


def test_a_shape_handed_a_transformation_by_a_group_becomes_a_path() -> (
    None
):
    # the group has no geometry of its own, so the rotation has nowhere to go
    # but into the shapes; the rect can only take it as a path, the circle
    # takes it as it is
    rect = Rect(
        x=Length(80),
        y=Length(-60),
        width=Length(120),
        height=Length(120),
        fill=Color("green"),
    )
    circle = Circle(cx=Length(100), cy=Length(0), r=Length(20))
    original = _svg(G(transform=[Rotate(45)]).add_children(rect, circle))
    reified = copy.deepcopy(original)

    reified.reify(convert_shapes_to_paths=True)

    assert not transforms_left(reified)
    assert reified.find(Rect, default=None) is None
    assert isinstance(reified.find(Circle), Circle)
    assert isinstance(reified.find(Path), Path)
    assert_svg_visually_equal(original, reified, tolerance=_TOLERANCE)


def test_a_shape_that_can_take_what_the_group_hands_down_stays_a_shape() -> (
    None
):
    rect = Rect(
        x=Length(20),
        y=Length(20),
        width=Length(60),
        height=Length(40),
        fill=Color("green"),
    )
    original = _svg(G(transform=[Scale(2, 1.5)]).add_child(rect))
    reified = copy.deepcopy(original)

    reified.reify(convert_shapes_to_paths=True)

    assert not transforms_left(reified)
    assert isinstance(reified.find(Rect), Rect)
    assert_svg_visually_equal(original, reified)
