"""A paint server has to keep describing the shape it paints."""

import copy

import pytest

import svglab
from tests import conftest


L = svglab.Length
C = svglab.Color


def _svg(*children: svglab.Element) -> svglab.Svg:
    return svglab.Svg(
        width=L(240), height=L(240), viewBox=(-40, -40, 240, 240)
    ).add_children(*children)


def _rect(**kwargs: object) -> svglab.Rect:
    kwargs.setdefault("x", L(10))
    kwargs.setdefault("y", L(10))
    kwargs.setdefault("width", L(80))
    kwargs.setdefault("height", L(60))

    return svglab.Rect(**kwargs)  # type: ignore[arg-type]


def _pattern(
    *, viewbox: bool = False, content_units: str | None = None
) -> svglab.Pattern:
    kwargs: dict[str, object] = {
        "id": "p",
        "patternUnits": "objectBoundingBox",
        "x": L(0),
        "y": L(0),
        "width": L(0.25),
        "height": L(0.25),
    }

    if viewbox:
        kwargs["viewBox"] = (0, 0, 20, 20)
    if content_units is not None:
        kwargs["patternContentUnits"] = content_units

    pattern = svglab.Pattern(**kwargs)  # type: ignore[arg-type]
    fraction = content_units == "objectBoundingBox"

    return pattern.add_children(
        svglab.Circle(
            cx=L(0.1) if fraction else L(10),
            cy=L(0.1) if fraction else L(10),
            r=L(0.08) if fraction else L(8),
            fill=C("purple"),
        ),
        svglab.Rect(
            x=L(0),
            y=L(0),
            width=L(0.06) if fraction else L(6),
            height=L(0.06) if fraction else L(6),
            fill=C("orange"),
        ),
    )


_UNIFORM = [svglab.Scale(1.4)]
_NON_UNIFORM = [svglab.Scale(1.3, 0.7)]


@pytest.mark.parametrize(
    ("viewbox", "content_units", "uniform", "non_uniform"),
    [
        # the tile follows the bounding box, but the content inside it is
        # drawn at its natural size in user space and only the tiling changes
        (False, None, False, False),
        # a viewBox maps the content onto the tile, so it is resized with it
        (True, None, True, False),
        # ... and stretched to it, where the aspect ratio is not preserved
        (True, "none", True, True),
        # bounding-box content is a fraction of the box either way
        (False, "objectBoundingBox", True, True),
    ],
    ids=["plain", "viewBox", "viewBox-stretched", "bbox-content"],
)
def test_a_pattern_is_resized_only_as_far_as_its_content_follows(
    *,
    viewbox: bool,
    content_units: str | None,
    uniform: bool,
    non_uniform: bool,
) -> None:
    pattern = _pattern(
        viewbox=viewbox,
        content_units=None if content_units == "none" else content_units,
    )

    if content_units == "none":
        pattern.preserveAspectRatio = "none"

    for transform, expected in (
        (_UNIFORM, uniform),
        (_NON_UNIFORM, non_uniform),
    ):
        original = _svg(
            svglab.Defs().add_child(copy.deepcopy(pattern)),
            _rect(fill=pattern.get_func_iri(), transform=list(transform)),
        )
        reified = copy.deepcopy(original)
        reified.reify()

        absorbed = reified.find(svglab.Rect).transform is None

        assert absorbed == expected, (viewbox, content_units, transform)
        conftest.assert_svg_visually_equal(original, reified)


def _gradient(units: str) -> svglab.LinearGradient:
    user_space = units == "userSpaceOnUse"
    gradient = svglab.LinearGradient(
        id="g",
        gradientUnits=units,  # type: ignore[arg-type]
        x1=L(10) if user_space else L(0),
        y1=L(10) if user_space else L(0),
        x2=L(90) if user_space else L(1),
        y2=L(70) if user_space else L(1),
    )

    return gradient.add_children(
        svglab.Stop(offset=0.0, stop_color=C("red")),
        svglab.Stop(offset=1.0, stop_color=C("blue")),
    )


@pytest.mark.parametrize(
    "transform",
    [
        [svglab.Translate(140, 0), svglab.Scale(-1, 1)],
        [svglab.Rotate(90, 50, 40)],
        [svglab.Rotate(23)],
    ],
    ids=["mirror", "quarter-turn", "rotation"],
)
def test_a_bounding_box_gradient_refuses_to_be_turned_or_flipped(
    transform: svglab.Transform,
) -> None:
    # the gradient is mapped onto the box of the shape as it stands in its
    # own coordinate system, so turning the shape would have turned the
    # gradient with it -- and rewriting a box cannot say that
    gradient = _gradient("objectBoundingBox")
    original = _svg(
        svglab.Defs().add_child(gradient),
        _rect(fill=gradient.get_func_iri(), transform=transform),
    )

    reified = copy.deepcopy(original)
    reified.reify()

    assert reified.find(svglab.Rect).transform
    conftest.assert_svg_visually_equal(original, reified)


@pytest.mark.parametrize(
    "transform",
    [
        [svglab.Translate(12, -7)],
        [svglab.Scale(1.4)],
        [svglab.Scale(1.3, 0.7)],
    ],
    ids=["translate", "uniform", "non-uniform"],
)
def test_a_bounding_box_gradient_is_carried_along_by_a_resize(
    transform: svglab.Transform,
) -> None:
    gradient = _gradient("objectBoundingBox")
    original = _svg(
        svglab.Defs().add_child(gradient),
        _rect(fill=gradient.get_func_iri(), transform=transform),
    )

    reified = copy.deepcopy(original)
    reified.reify()

    assert reified.find(svglab.Rect).transform is None
    conftest.assert_svg_visually_equal(original, reified)


def test_a_gradient_reifies_its_own_transform_whatever_its_units() -> None:
    for units in ("userSpaceOnUse", "objectBoundingBox"):
        gradient = _gradient(units)
        gradient.gradientTransform = [
            svglab.Rotate(20),
            svglab.Translate(0.1, 0.1),
        ]
        original = _svg(
            svglab.Defs().add_child(gradient),
            _rect(fill=gradient.get_func_iri()),
        )

        reified = copy.deepcopy(original)
        reified.reify()

        assert (
            reified.find(svglab.LinearGradient).gradientTransform is None
        ), units
        conftest.assert_svg_visually_equal(original, reified)


@pytest.mark.parametrize(
    ("pattern_transform", "absorbed"),
    [
        (None, True),
        ([svglab.Translate(5, 3)], True),
        ([svglab.Rotate(20)], False),
        ([svglab.Scale(1.5)], False),
        ([svglab.Scale(1.3, 0.7)], False),
        ([svglab.SkewX(15)], False),
    ],
    ids=["none", "translate", "rotate", "uniform", "non-uniform", "skew"],
)
def test_a_pattern_transform_has_to_commute_with_what_is_folded_in(
    pattern_transform: svglab.Transform | None, *, absorbed: bool
) -> None:
    # the tiling is laid out in the box of the shape and the pattern
    # transform is applied to the result, so moving the shape moves the
    # tiling *before* the pattern transform rather than after it -- the two
    # only agree when they commute
    pattern = _pattern()
    pattern.patternTransform = pattern_transform

    original = _svg(
        svglab.Defs().add_child(pattern),
        _rect(
            fill=pattern.get_func_iri(),
            transform=[svglab.Translate(16, 12)],
        ),
    )
    reified = copy.deepcopy(original)
    reified.reify()

    assert (reified.find(svglab.Rect).transform is None) == absorbed
    conftest.assert_svg_visually_equal(original, reified)


def test_a_linear_pattern_transform_still_allows_a_resize() -> None:
    # resizing about the origin leaves the corner of the box where it is, and
    # that does commute with turning or stretching the tiling
    pattern = _pattern(viewbox=True)
    pattern.patternTransform = [svglab.Rotate(20)]

    original = _svg(
        svglab.Defs().add_child(pattern),
        _rect(fill=pattern.get_func_iri(), transform=[svglab.Scale(2)]),
    )
    reified = copy.deepcopy(original)
    reified.reify()

    assert reified.find(svglab.Rect).transform is None
    conftest.assert_svg_visually_equal(original, reified)
