import copy

import numpy as np
import pytest

import svglab
from tests import conftest


# reifying a rotation replaces a rotated shape with an equivalent shape in a
# different position, which the renderer antialiases slightly differently. the
# measured floor of that difference is around 1.4e-5, while displacing a shape
# by a tenth of a pixel already produces around 7e-5, so this tolerance still
# catches a sub-pixel error in the reified geometry
_TOLERANCE = 5e-5

_ROTATION = svglab.Rotate(30, 100, 100)


def _svg(child: svglab.Element) -> svglab.Svg:
    return svglab.Svg(
        width=svglab.Length(200), height=svglab.Length(200)
    ).add_child(child)


_REIFIABLE: list[svglab.Element] = [
    svglab.Circle(
        cx=svglab.Length(100),
        cy=svglab.Length(60),
        r=svglab.Length(30),
        fill=svglab.Color("red"),
    ),
    svglab.Line(
        x1=svglab.Length(40),
        y1=svglab.Length(40),
        x2=svglab.Length(160),
        y2=svglab.Length(120),
        stroke=svglab.Color("blue"),
        stroke_width=svglab.Length(4),
    ),
    svglab.Polygon(
        points=[
            svglab.Point(60, 60),
            svglab.Point(140, 60),
            svglab.Point(100, 140),
        ],
        fill=svglab.Color("yellow"),
    ),
    svglab.Polyline(
        points=[
            svglab.Point(50, 50),
            svglab.Point(150, 80),
            svglab.Point(90, 150),
        ],
        fill="none",
        stroke=svglab.Color("purple"),
        stroke_width=svglab.Length(3),
    ),
    svglab.Path(
        d=svglab.PathData.from_str(
            "M 60,60 L 140,60 A 20,20 0 0 1 100,140 Z"
        ),
        fill=svglab.Color("orange"),
    ),
]

_CONVERTED: list[svglab.Element] = [
    svglab.Rect(
        x=svglab.Length(60),
        y=svglab.Length(60),
        width=svglab.Length(80),
        height=svglab.Length(40),
        fill=svglab.Color("red"),
    ),
    svglab.Rect(
        x=svglab.Length(60),
        y=svglab.Length(60),
        width=svglab.Length(80),
        height=svglab.Length(40),
        rx=svglab.Length(12),
        ry=svglab.Length(6),
        fill=svglab.Color("red"),
        stroke=svglab.Color("black"),
        stroke_width=svglab.Length(4),
    ),
    svglab.Ellipse(
        cx=svglab.Length(100),
        cy=svglab.Length(100),
        rx=svglab.Length(40),
        ry=svglab.Length(20),
        fill=svglab.Color("green"),
    ),
]

_UNREIFIABLE: list[svglab.Element] = [
    svglab.Text(x=[svglab.Length(50)], y=[svglab.Length(100)]).add_child(
        svglab.RawText("hello")
    ),
    svglab.Image(
        x=svglab.Length(60),
        y=svglab.Length(60),
        width=svglab.Length(80),
        height=svglab.Length(40),
        # a 1x1 red PNG; the image has to render for the comparison to mean
        # anything
        href=svglab.Iri.from_str(
            "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAAB"
            "CAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU"
            "5ErkJggg=="
        ),
    ),
]


@pytest.mark.parametrize(
    "shape", _REIFIABLE, ids=lambda s: type(s).__name__.lower()
)
@pytest.mark.parametrize("angle", [30.0, 90.0, 180.0, -45.0])
def test_rotation_is_reified_on_shapes_that_can_express_it(
    shape: svglab.Element, angle: float
) -> None:
    shape = copy.deepcopy(shape)
    shape.transform = [svglab.Rotate(angle, 100, 100)]

    original = _svg(copy.deepcopy(shape))
    reified = _svg(shape)
    reified.reify()

    assert shape.transform is None
    conftest.assert_svg_visually_equal(
        original, reified, tolerance=_TOLERANCE
    )


@pytest.mark.parametrize(
    "shape", _UNREIFIABLE, ids=lambda s: type(s).__name__.lower()
)
def test_rotation_is_kept_on_elements_with_no_path_equivalent(
    shape: svglab.Element,
) -> None:
    shape = copy.deepcopy(shape)
    shape.transform = [_ROTATION]

    original = _svg(copy.deepcopy(shape))
    reified = _svg(shape)

    assert reified.reify() is reified
    assert shape.transform == [_ROTATION]
    conftest.assert_svg_visually_equal(original, reified)


@pytest.mark.parametrize(
    "shape", _CONVERTED, ids=lambda s: type(s).__name__.lower()
)
@pytest.mark.parametrize("angle", [30.0, -45.0])
def test_shape_that_cannot_express_a_rotation_becomes_a_path(
    shape: svglab.Element, angle: float
) -> None:
    shape = copy.deepcopy(shape)
    shape.transform = [svglab.Rotate(angle, 100, 100)]

    original = _svg(copy.deepcopy(shape))
    reified = _svg(shape)
    reified.reify()

    path = reified.find(svglab.Path)

    assert path.transform is None
    assert not list(reified.find_all(type(shape)))
    conftest.assert_svg_visually_equal(
        original, reified, tolerance=_TOLERANCE
    )


@pytest.mark.parametrize("angle", [90.0, 180.0, 270.0, -90.0])
def test_quarter_turns_do_not_convert_a_rect_or_an_ellipse(
    angle: float,
) -> None:
    rect = svglab.Rect(
        x=svglab.Length(60),
        y=svglab.Length(40),
        width=svglab.Length(80),
        height=svglab.Length(40),
        fill=svglab.Color("red"),
        transform=[svglab.Rotate(angle, 100, 100)],
    )
    ellipse = svglab.Ellipse(
        cx=svglab.Length(100),
        cy=svglab.Length(140),
        rx=svglab.Length(40),
        ry=svglab.Length(20),
        fill=svglab.Color("green"),
        transform=[svglab.Rotate(angle, 100, 100)],
    )

    original = _svg(
        svglab.G().add_children(*copy.deepcopy([rect, ellipse]))
    )
    reified = _svg(svglab.G().add_children(rect, ellipse))
    reified.reify()

    # a quarter turn maps an axis-aligned box onto an axis-aligned box, so
    # neither shape has to degrade into a path
    assert rect.transform is None
    assert ellipse.transform is None
    assert not list(reified.find_all(svglab.Path))
    conftest.assert_svg_visually_equal(
        original, reified, tolerance=_TOLERANCE
    )


def test_a_converted_shape_keeps_its_place_and_children() -> None:
    rect = svglab.Rect(
        x=svglab.Length(60),
        y=svglab.Length(60),
        width=svglab.Length(80),
        height=svglab.Length(40),
        fill=svglab.Color("red"),
        transform=[_ROTATION],
    )
    rect.add_child(svglab.Title().add_child(svglab.RawText("a rectangle")))

    group = svglab.G().add_children(
        svglab.Circle(r=svglab.Length(1)),
        rect,
        svglab.Circle(r=svglab.Length(2)),
    )
    _svg(group).reify()

    path = group.find(svglab.Path)

    assert group.get_child_index(path) == 1
    assert path.find(svglab.Title) is not None
    assert rect.parent is None


def test_a_converted_root_element_is_returned() -> None:
    rect = svglab.Rect(
        x=svglab.Length(60),
        y=svglab.Length(60),
        width=svglab.Length(80),
        height=svglab.Length(40),
        transform=[_ROTATION],
    )

    # a root element cannot be replaced in a tree, so the caller has to use
    # the returned element
    result = rect.reify()

    assert isinstance(result, svglab.Path)
    assert result.parent is None
    assert rect.transform == [_ROTATION]


def test_a_transformation_no_path_can_express_does_not_convert() -> None:
    rect = svglab.Rect(
        x=svglab.Length(60),
        y=svglab.Length(60),
        width=svglab.Length(80),
        height=svglab.Length(40),
        fill=svglab.Color("red"),
        transform=[svglab.Scale(2, 3)],
    )

    original = _svg(copy.deepcopy(rect))
    reified = _svg(rect)
    reified.reify()

    # converting would not have helped, so the rect must be left alone
    assert reified.find(svglab.Rect) is rect
    assert rect.transform == [svglab.Scale(2, 3)]
    conftest.assert_svg_visually_equal(original, reified)


def test_rotation_of_a_percentage_length_is_kept() -> None:
    # a rotation mixes the axes, so a length relative to the viewport cannot
    # be carried through
    circle = svglab.Circle(
        cx=svglab.Length(50, "%"),
        cy=svglab.Length(50, "%"),
        r=svglab.Length(30),
        fill=svglab.Color("red"),
        transform=[_ROTATION],
    )

    original = _svg(copy.deepcopy(circle))
    reified = _svg(circle)
    reified.reify()

    assert circle.transform == [_ROTATION]
    conftest.assert_svg_visually_equal(original, reified)


def test_rotation_is_pushed_down_through_a_group() -> None:
    group = svglab.G(transform=[_ROTATION]).add_children(
        svglab.Circle(
            cx=svglab.Length(60),
            cy=svglab.Length(60),
            r=svglab.Length(20),
            fill=svglab.Color("red"),
        ),
        svglab.Line(
            x1=svglab.Length(40),
            y1=svglab.Length(140),
            x2=svglab.Length(160),
            y2=svglab.Length(140),
            stroke=svglab.Color("blue"),
            stroke_width=svglab.Length(4),
        ),
    )

    original = _svg(copy.deepcopy(group))
    reified = _svg(group)
    reified.reify()

    assert group.transform is None
    assert all(child.transform is None for child in group.find_all())
    conftest.assert_svg_visually_equal(
        original, reified, tolerance=_TOLERANCE
    )


def test_rotation_of_a_nested_viewport_is_kept() -> None:
    # rotating a nested <svg> rotates the viewport it establishes, which
    # pushing the rotation down to the children cannot reproduce
    nested = svglab.Svg(
        x=svglab.Length(50),
        y=svglab.Length(50),
        width=svglab.Length(60),
        height=svglab.Length(60),
        transform=[_ROTATION],
    ).add_child(
        svglab.Rect(
            x=svglab.Length(0),
            y=svglab.Length(0),
            width=svglab.Length(100),
            height=svglab.Length(100),
            fill=svglab.Color("red"),
        )
    )

    original = _svg(copy.deepcopy(nested))
    reified = _svg(nested)
    reified.reify()

    assert nested.transform == [_ROTATION]
    conftest.assert_svg_visually_equal(original, reified)


@pytest.mark.parametrize(
    ("a", "b"),
    [
        (svglab.Rotate(30), svglab.Scale(2, 3)),
        (svglab.Scale(2, 3), svglab.Rotate(30)),
        (svglab.Rotate(30, 5, 7), svglab.Scale(2, 3)),
    ],
)
def test_rotate_and_anisotropic_scale_cannot_be_swapped(
    a: svglab.TransformFunction, b: svglab.TransformFunction
) -> None:
    # `S R S^-1` is an elliptical rotation, which cannot be expressed as a
    # `rotate()`, so no adjustment of the parameters makes the swap possible
    with pytest.raises(svglab.SvgTransformSwapError):
        svglab.swap_transforms(a, b)


@pytest.mark.parametrize(
    ("a", "b"),
    [
        # isotropic scaling commutes with any rotation
        (svglab.Rotate(30, 5, 7), svglab.Scale(2)),
        (svglab.Scale(2), svglab.Rotate(30, 5, 7)),
        # a rotation by a multiple of 180 degrees is the identity or a point
        # reflection, both of which commute with any scaling
        (svglab.Rotate(180, 5, 7), svglab.Scale(2, 3)),
        (svglab.Scale(2, 3), svglab.Rotate(180, 5, 7)),
        # rotations about a common center commute
        (svglab.Rotate(30, 5, 7), svglab.Rotate(45, 5, 7)),
    ],
)
def test_swappable_rotations_preserve_the_composed_matrix(
    a: svglab.TransformFunction, b: svglab.TransformFunction
) -> None:
    c, d = svglab.swap_transforms(a, b)

    assert np.allclose(
        np.asarray(svglab.compose([a, b]), dtype=np.float64),
        np.asarray(svglab.compose([c, d]), dtype=np.float64),
    )


@pytest.mark.parametrize(
    "transform",
    [
        [svglab.Rotate(30), svglab.Scale(2, 3)],
        [svglab.Scale(2, 3), svglab.Rotate(30)],
        [svglab.Translate(5, 5), svglab.Rotate(30), svglab.Scale(2, 3)],
    ],
)
def test_unswappable_transformations_do_not_raise_during_reification(
    transform: svglab.Transform,
) -> None:
    original = _svg(
        svglab.Rect(
            x=svglab.Length(40),
            y=svglab.Length(40),
            width=svglab.Length(40),
            height=svglab.Length(20),
            fill=svglab.Color("red"),
            transform=transform,
        )
    )
    reified = copy.deepcopy(original)
    reified.reify()

    conftest.assert_svg_visually_equal(
        original, reified, tolerance=_TOLERANCE
    )
