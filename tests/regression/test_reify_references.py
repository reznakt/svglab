"""Reification must not disturb anything the document points at."""

import copy

import pytest

from svglab import (
    Circle,
    ClipPath,
    Color,
    Defs,
    Element,
    FeGaussianBlur,
    Filter,
    G,
    Iri,
    Length,
    LinearGradient,
    Rect,
    Rotate,
    Scale,
    Stop,
    Svg,
    Transform,
    Translate,
    Use,
)
from tests.conftest import assert_svg_visually_equal


def _svg(*children: Element) -> Svg:
    return Svg(width=Length(200), height=Length(200)).add_children(
        *children
    )


def _rect(**kwargs: object) -> Rect:
    return Rect(
        x=Length(20),
        y=Length(20),
        width=Length(60),
        height=Length(40),
        **kwargs,  # type: ignore[arg-type]
    )


def _gradient(*, user_space: bool) -> LinearGradient:
    gradient = LinearGradient(
        id="g",
        gradientUnits=(
            "userSpaceOnUse" if user_space else "objectBoundingBox"
        ),
        x1=Length(20) if user_space else None,
        y1=Length(20) if user_space else None,
        x2=Length(80) if user_space else None,
        y2=Length(60) if user_space else None,
    )

    return gradient.add_children(
        Stop(offset=0.0, stop_color=Color("red")),
        Stop(offset=1.0, stop_color=Color("blue")),
    )


_TRANSFORMS = [[Translate(15, 25)], [Scale(1.4)], [Rotate(20, 50, 40)]]


@pytest.mark.parametrize("transform", _TRANSFORMS)
def test_a_user_space_gradient_keeps_the_shape_it_paints_in_place(
    transform: Transform,
) -> None:
    gradient = _gradient(user_space=True)
    painted = _rect(fill=gradient.get_func_iri(), transform=transform)
    original = _svg(Defs().add_child(gradient), painted)

    reified = copy.deepcopy(original)
    reified.reify()

    assert reified.find(Rect).transform
    assert_svg_visually_equal(original, reified)


@pytest.mark.parametrize("transform", _TRANSFORMS)
def test_a_bounding_box_gradient_travels_with_the_shape(
    transform: Transform,
) -> None:
    # the gradient is a fraction of the shape's own box, so it goes wherever
    # the shape goes
    gradient = _gradient(user_space=False)
    painted = _rect(fill=gradient.get_func_iri(), transform=transform)
    original = _svg(Defs().add_child(gradient), painted)

    reified = copy.deepcopy(original)
    reified.reify()

    assert_svg_visually_equal(original, reified)


@pytest.mark.parametrize("transform", _TRANSFORMS)
def test_a_gradient_with_a_sibling_that_uses_it_stays_consistent(
    transform: Transform,
) -> None:
    gradient = _gradient(user_space=True)
    original = _svg(
        G(transform=transform).add_children(
            gradient, _rect(fill=Iri(fragment="g").to_func_iri())
        )
    )

    reified = copy.deepcopy(original)
    reified.reify()

    assert_svg_visually_equal(original, reified)


@pytest.mark.parametrize("transform", _TRANSFORMS)
def test_a_use_target_is_not_moved_out_from_under_the_reference(
    transform: Transform,
) -> None:
    # `use` clones the element it points at, not the group around it, so
    # pushing the group's transformation into it would change what the clone
    # renders as
    original = _svg(
        G(transform=transform).add_child(
            _rect(id="src", fill=Color("green"))
        ),
        Use(href=Iri(fragment="src"), x=Length(10), y=Length(100)),
    )

    reified = copy.deepcopy(original)
    reified.reify()

    assert_svg_visually_equal(original, reified)


@pytest.mark.parametrize("transform", _TRANSFORMS)
def test_a_user_space_clip_path_keeps_the_shape_in_place(
    transform: Transform,
) -> None:
    clip = ClipPath(id="c").add_child(
        Circle(cx=Length(50), cy=Length(40), r=Length(25))
    )
    original = _svg(
        Defs().add_child(clip),
        _rect(
            fill=Color("purple"),
            clip_path=Iri(fragment="c").to_func_iri(),
            transform=transform,
        ),
    )

    reified = copy.deepcopy(original)
    reified.reify()

    assert reified.find(Rect).transform
    assert_svg_visually_equal(original, reified)


def test_a_use_element_absorbs_a_translation_into_its_position() -> None:
    use = Use(
        href=Iri(fragment="src"),
        x=Length(10),
        y=Length(20),
        transform=[Translate(5, 7)],
    )
    original = _svg(
        Defs().add_child(_rect(id="src", fill=Color("teal"))), use
    )

    reified = copy.deepcopy(original)
    reified.reify()

    reified_use = reified.find(Use)

    assert reified_use.transform is None
    assert reified_use.x == Length(15)
    assert reified_use.y == Length(27)

    assert_svg_visually_equal(original, reified)


@pytest.mark.parametrize(
    "units", ["userSpaceOnUse", "objectBoundingBox"], ids=lambda u: u
)
@pytest.mark.parametrize(
    "transform",
    [[Translate(15, 25)], [Scale(1.4)], [Rotate(90, 50, 40)]],
    ids=["translate", "scale", "quarter-turn"],
)
def test_a_filter_keeps_the_shape_inside_its_region(
    units: str, transform: Transform
) -> None:
    # a filter region given in user space is resolved where the element
    # renders, so moving the element would leave the region behind
    filter_ = Filter(
        id="f",
        filterUnits=units,  # type: ignore[arg-type]
        x=Length(-0.2 if units == "objectBoundingBox" else 0),
        y=Length(-0.2 if units == "objectBoundingBox" else 0),
        width=Length(1.4 if units == "objectBoundingBox" else 140),
        height=Length(1.4 if units == "objectBoundingBox" else 120),
    )
    filter_.add_child(FeGaussianBlur(stdDeviation=3.0))

    original = _svg(
        Defs().add_child(filter_),
        _rect(fill=Color("navy"), filter=filter_.get_func_iri()),
    )
    original.find(Rect).transform = transform

    reified = copy.deepcopy(original)
    reified.reify()

    assert_svg_visually_equal(original, reified)
