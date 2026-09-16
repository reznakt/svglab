"""Reification must not disturb anything the document points at."""

import copy

import pytest

import svglab
from tests import conftest


def _svg(*children: svglab.Element) -> svglab.Svg:
    return svglab.Svg(
        width=svglab.Length(200), height=svglab.Length(200)
    ).add_children(*children)


def _rect(**kwargs: object) -> svglab.Rect:
    return svglab.Rect(
        x=svglab.Length(20),
        y=svglab.Length(20),
        width=svglab.Length(60),
        height=svglab.Length(40),
        **kwargs,  # type: ignore[arg-type]
    )


def _gradient(*, user_space: bool) -> svglab.LinearGradient:
    gradient = svglab.LinearGradient(
        id="g",
        gradientUnits=(
            "userSpaceOnUse" if user_space else "objectBoundingBox"
        ),
        x1=svglab.Length(20) if user_space else None,
        y1=svglab.Length(20) if user_space else None,
        x2=svglab.Length(80) if user_space else None,
        y2=svglab.Length(60) if user_space else None,
    )

    return gradient.add_children(
        svglab.Stop(offset=0.0, stop_color=svglab.Color("red")),
        svglab.Stop(offset=1.0, stop_color=svglab.Color("blue")),
    )


_TRANSFORMS = [
    [svglab.Translate(15, 25)],
    [svglab.Scale(1.4)],
    [svglab.Rotate(20, 50, 40)],
]


@pytest.mark.parametrize("transform", _TRANSFORMS)
def test_a_user_space_gradient_keeps_the_shape_it_paints_in_place(
    transform: svglab.Transform,
) -> None:
    gradient = _gradient(user_space=True)
    painted = _rect(fill=gradient.get_func_iri(), transform=transform)
    original = _svg(svglab.Defs().add_child(gradient), painted)

    reified = copy.deepcopy(original)
    reified.reify()

    assert reified.find(svglab.Rect).transform
    conftest.assert_svg_visually_equal(original, reified)


@pytest.mark.parametrize("transform", _TRANSFORMS)
def test_a_bounding_box_gradient_travels_with_the_shape(
    transform: svglab.Transform,
) -> None:
    # the gradient is a fraction of the shape's own box, so it goes wherever
    # the shape goes
    gradient = _gradient(user_space=False)
    painted = _rect(fill=gradient.get_func_iri(), transform=transform)
    original = _svg(svglab.Defs().add_child(gradient), painted)

    reified = copy.deepcopy(original)
    reified.reify()

    conftest.assert_svg_visually_equal(original, reified)


@pytest.mark.parametrize("transform", _TRANSFORMS)
def test_a_gradient_with_a_sibling_that_uses_it_stays_consistent(
    transform: svglab.Transform,
) -> None:
    gradient = _gradient(user_space=True)
    original = _svg(
        svglab.G(transform=transform).add_children(
            gradient, _rect(fill=svglab.Iri(fragment="g").to_func_iri())
        )
    )

    reified = copy.deepcopy(original)
    reified.reify()

    conftest.assert_svg_visually_equal(original, reified)


@pytest.mark.parametrize("transform", _TRANSFORMS)
def test_a_use_target_is_not_moved_out_from_under_the_reference(
    transform: svglab.Transform,
) -> None:
    # `use` clones the element it points at, not the group around it, so
    # pushing the group's transformation into it would change what the clone
    # renders as
    original = _svg(
        svglab.G(transform=transform).add_child(
            _rect(id="src", fill=svglab.Color("green"))
        ),
        svglab.Use(
            href=svglab.Iri(fragment="src"),
            x=svglab.Length(10),
            y=svglab.Length(100),
        ),
    )

    reified = copy.deepcopy(original)
    reified.reify()

    conftest.assert_svg_visually_equal(original, reified)


@pytest.mark.parametrize("transform", _TRANSFORMS)
def test_a_user_space_clip_path_keeps_the_shape_in_place(
    transform: svglab.Transform,
) -> None:
    clip = svglab.ClipPath(id="c").add_child(
        svglab.Circle(
            cx=svglab.Length(50), cy=svglab.Length(40), r=svglab.Length(25)
        )
    )
    original = _svg(
        svglab.Defs().add_child(clip),
        _rect(
            fill=svglab.Color("purple"),
            clip_path=svglab.Iri(fragment="c").to_func_iri(),
            transform=transform,
        ),
    )

    reified = copy.deepcopy(original)
    reified.reify()

    assert reified.find(svglab.Rect).transform
    conftest.assert_svg_visually_equal(original, reified)


def test_a_use_element_absorbs_a_translation_into_its_position() -> None:
    use = svglab.Use(
        href=svglab.Iri(fragment="src"),
        x=svglab.Length(10),
        y=svglab.Length(20),
        transform=[svglab.Translate(5, 7)],
    )
    original = _svg(
        svglab.Defs().add_child(
            _rect(id="src", fill=svglab.Color("teal"))
        ),
        use,
    )

    reified = copy.deepcopy(original)
    reified.reify()

    reified_use = reified.find(svglab.Use)

    assert reified_use.transform is None
    assert reified_use.x == svglab.Length(15)
    assert reified_use.y == svglab.Length(27)

    conftest.assert_svg_visually_equal(original, reified)


@pytest.mark.parametrize(
    "units", ["userSpaceOnUse", "objectBoundingBox"], ids=lambda u: u
)
@pytest.mark.parametrize(
    "transform",
    [
        [svglab.Translate(15, 25)],
        [svglab.Scale(1.4)],
        [svglab.Rotate(90, 50, 40)],
    ],
    ids=["translate", "scale", "quarter-turn"],
)
def test_a_filter_keeps_the_shape_inside_its_region(
    units: str, transform: svglab.Transform
) -> None:
    # a filter region given in user space is resolved where the element
    # renders, so moving the element would leave the region behind
    filter_ = svglab.Filter(
        id="f",
        filterUnits=units,  # type: ignore[arg-type]
        x=svglab.Length(-0.2 if units == "objectBoundingBox" else 0),
        y=svglab.Length(-0.2 if units == "objectBoundingBox" else 0),
        width=svglab.Length(1.4 if units == "objectBoundingBox" else 140),
        height=svglab.Length(1.4 if units == "objectBoundingBox" else 120),
    )
    filter_.add_child(svglab.FeGaussianBlur(stdDeviation=3.0))

    original = _svg(
        svglab.Defs().add_child(filter_),
        _rect(fill=svglab.Color("navy"), filter=filter_.get_func_iri()),
    )
    original.find(svglab.Rect).transform = transform

    reified = copy.deepcopy(original)
    reified.reify()

    conftest.assert_svg_visually_equal(original, reified)
