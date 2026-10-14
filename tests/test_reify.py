"""Tests for reification: replacing transformations with geometry.

The visual side of reification is covered by the render-based tests in
`tests/regression`. The tests here check the same thing algebraically, which
is cheap enough to run under hypothesis: a shape's geometry is its coordinates
*plus* its transformation, so reification is correct exactly when the two
together map every point to where it was before.
"""

from __future__ import annotations

import copy
import operator

import hypothesis
import hypothesis.strategies as st
import pytest
from typing_extensions import Final

import svglab
from svglab import (
    Circle,
    Color,
    Defs,
    Element,
    Ellipse,
    G,
    Image,
    Iri,
    Length,
    Line,
    Marker,
    Matrix,
    Path,
    PathData,
    Point,
    Points,
    Polygon,
    Polyline,
    Rect,
    Rotate,
    Scale,
    SkewX,
    SkewY,
    Svg,
    Text,
    TextPath,
    Transform,
    TransformFunction,
    Translate,
    Tref,
    Tspan,
    Use,
    compose,
)
from svglab.attrs.names import ATTR_NAME_TO_NORMALIZED
from svglab.elements.names import ELEMENT_NAME_TO_NORMALIZED
from svglab.entities import element_name
from svglab.reify import (
    AFFINE,
    GEOMETRIC_ATTR_NAMES,
    MAX_CONDITION_NUMBER,
    NOTHING,
    RECTILINEAR,
    SIMILARITY,
    TRANSLATION,
    UNIFORM_SCALING,
    Feature,
    TransformInheritedByChildren,
    features,
    geometry_capability,
    has_own_geometry,
    split,
)


_COORDINATES: Final = st.floats(
    min_value=-100, max_value=100, allow_nan=False, allow_infinity=False
)
_SCALE_FACTORS: Final = st.one_of(
    st.floats(min_value=0.25, max_value=4),
    st.floats(min_value=-4, max_value=-0.25),
)
_ANGLES: Final = st.floats(min_value=-180, max_value=180)
_SKEW_ANGLES: Final = st.floats(min_value=-60, max_value=60)

_TRANSFORM_FUNCTIONS: Final = st.one_of(
    st.tuples(_COORDINATES, _COORDINATES).map(
        lambda args: Translate(*args)
    ),
    st.tuples(_SCALE_FACTORS, _SCALE_FACTORS).map(
        lambda args: Scale(*args)
    ),
    st.tuples(_ANGLES, _COORDINATES, _COORDINATES).map(
        lambda args: Rotate(args[0], args[1], args[2])
    ),
    _SKEW_ANGLES.map(SkewX),
    _SKEW_ANGLES.map(SkewY),
    st.tuples(
        _SCALE_FACTORS,
        _COORDINATES,
        _COORDINATES,
        _SCALE_FACTORS,
        _COORDINATES,
        _COORDINATES,
    ).map(lambda args: Matrix(*args)),
)

# a transformation that nearly collapses the plane is refused outright, and
# the properties below are about the ones that are not
_TRANSFORMS: Final = st.lists(
    _TRANSFORM_FUNCTIONS, min_size=0, max_size=4
).filter(lambda t: compose(t).condition_number() <= MAX_CONDITION_NUMBER)

_POINTS: Final = st.lists(
    st.tuples(_COORDINATES, _COORDINATES).map(lambda args: Point(*args)),
    min_size=2,
    max_size=6,
)

_TOLERANCE: Final = 1e-6


def _assert_close(a: Point, b: Point, *, context: object = None) -> None:
    assert a.x == pytest.approx(b.x, rel=_TOLERANCE, abs=_TOLERANCE), (
        context
    )
    assert a.y == pytest.approx(b.y, rel=_TOLERANCE, abs=_TOLERANCE), (
        context
    )


def _mapped_points(polygon: Polygon) -> list[Point]:
    """Map the polygon's points through its own transformation."""
    matrix = compose(polygon.transform or [])
    points = polygon.points or []

    return [matrix @ point for point in points]


# region The matrix algebra reification is built on


@hypothesis.given(_TRANSFORMS)
def test_split_factors_the_matrix_exactly(transform: Transform) -> None:
    matrix = compose(transform)

    for capability in (
        NOTHING,
        TRANSLATION,
        UNIFORM_SCALING,
        SIMILARITY,
        RECTILINEAR,
        AFFINE,
    ):
        residue, absorbed = split(matrix, capability)

        assert residue @ absorbed == matrix, (capability, matrix)
        assert features(absorbed) <= capability, (capability, absorbed)


@hypothesis.given(_TRANSFORMS)
def test_an_affine_element_absorbs_everything(
    transform: Transform,
) -> None:
    matrix = compose(transform)
    residue, _ = split(matrix, AFFINE)

    assert residue == Matrix.identity()


@hypothesis.given(_TRANSFORMS)
def test_the_translation_is_always_absorbable(
    transform: Transform,
) -> None:
    # whatever else an element can do, it can be moved, so whatever is left
    # behind is never itself a move
    matrix = compose(transform)
    residue, absorbed = split(matrix, TRANSLATION)

    assert residue @ absorbed == matrix
    assert residue.translation() == Translate(0, 0)


@pytest.mark.parametrize(
    ("transformation", "expected"),
    [
        (Translate(1, 2), {Feature.TRANSLATE}),
        (Scale(2), {Feature.SCALE}),
        (Scale(2, 3), {Feature.SCALE, Feature.NON_UNIFORM_SCALE}),
        (Rotate(45), {Feature.ROTATE}),
        (Rotate(90), {Feature.QUARTER_TURN}),
        (Rotate(180), {Feature.QUARTER_TURN}),
        (Scale(-1, 1), {Feature.QUARTER_TURN, Feature.MIRROR}),
        (Scale(-1), {Feature.QUARTER_TURN}),
        (SkewX(20), {Feature.SKEW}),
        (Matrix.identity(), set()),
    ],
)
def test_features_names_what_a_transformation_does(
    transformation: TransformFunction, expected: set[Feature]
) -> None:
    assert features(transformation.to_matrix()) == expected


def test_a_skew_along_y_is_still_a_skew() -> None:
    # the classification pulls a rotation off the front of the matrix, and a
    # skew along y only becomes triangular after one; what matters is that
    # the shear is reported, since that is what rules out every element whose
    # geometry is not a plain list of coordinates
    found = features(SkewY(20).to_matrix())

    assert Feature.SKEW in found
    assert not found <= RECTILINEAR
    assert not found <= SIMILARITY


# endregion
# region The invariant that makes reification correct


@hypothesis.given(_TRANSFORMS, _POINTS)
def test_reify_preserves_the_position_of_every_point(
    transform: Transform, points: Points
) -> None:
    polygon = Polygon(points=points, transform=transform)
    before = _mapped_points(polygon)

    polygon.reify()

    for expected, actual in zip(
        before, _mapped_points(polygon), strict=True
    ):
        _assert_close(expected, actual, context=polygon.transform)


@hypothesis.given(_TRANSFORMS, _POINTS)
def test_reify_absorbs_everything_a_polygon_can_express(
    transform: Transform, points: Points
) -> None:
    # a polygon is nothing but a list of points, so there is no affine
    # transformation it cannot take on
    polygon = Polygon(points=points, transform=transform)
    polygon.reify()

    assert polygon.transform is None


@hypothesis.given(_TRANSFORMS, _POINTS)
def test_reify_is_idempotent(transform: Transform, points: Points) -> None:
    once = Polygon(points=points, transform=transform)
    once.reify()

    twice = copy.deepcopy(once)
    twice.reify()

    assert twice.transform == once.transform

    for expected, actual in zip(
        once.points or [], twice.points or [], strict=True
    ):
        _assert_close(expected, actual)


@hypothesis.given(_TRANSFORMS, _POINTS)
def test_what_is_left_over_could_not_have_been_absorbed(
    transform: Transform, points: Points
) -> None:
    # a rectangle keeps whatever it cannot express; reification is only done
    # when nothing more can be taken out of what remains
    rect = Rect(
        x=Length(points[0].x),
        y=Length(points[0].y),
        width=Length(abs(points[1].x) + 1),
        height=Length(abs(points[1].y) + 1),
        transform=transform,
    )
    rect.reify()

    if rect.transform is None:
        return

    leftover = compose(rect.transform)
    _, absorbed = split(leftover, geometry_capability(rect))

    assert absorbed == Matrix.identity(), rect.transform


@hypothesis.given(_TRANSFORMS, _POINTS)
def test_reify_pushes_a_group_transform_down_to_its_children(
    transform: Transform, points: Points
) -> None:
    polygon = Polygon(points=points)
    group = G(transform=transform).add_child(polygon)

    expected = [compose(transform) @ point for point in points]

    group.reify()

    assert group.transform is None

    for want, got in zip(expected, _mapped_points(polygon), strict=True):
        _assert_close(want, got)


# endregion
# region What each kind of element is able to take on


def _rect(**kwargs: object) -> Rect:
    kwargs.setdefault("x", Length(10))
    kwargs.setdefault("y", Length(20))
    kwargs.setdefault("width", Length(30))
    kwargs.setdefault("height", Length(40))

    return Rect(**kwargs)  # type: ignore[arg-type]


def _shapes() -> dict[str, Element]:
    return {
        "rect": _rect(),
        "circle": Circle(cx=Length(10), cy=Length(20), r=Length(5)),
        "ellipse": Ellipse(
            cx=Length(10), cy=Length(20), rx=Length(5), ry=Length(8)
        ),
        "line": Line(
            x1=Length(0), y1=Length(0), x2=Length(10), y2=Length(10)
        ),
        "polygon": Polygon(points=[Point(0, 0), Point(10, 10)]),
        "path": Path(d=PathData.from_str("M 0,0 L 10,10")),
        "text": Text(x=[Length(10)], y=[Length(20)], font_size=Length(12)),
        "image": Image(
            x=Length(10), y=Length(20), width=Length(30), height=Length(40)
        ),
        "use": Use(x=Length(10), y=Length(20)),
    }


# what each element is expected to be able to absorb, given no stroke and no
# references to complicate matters
_ABSORBS: Final = {
    "rect": RECTILINEAR,
    "circle": SIMILARITY,
    "ellipse": RECTILINEAR,
    "line": AFFINE,
    "polygon": AFFINE,
    "path": AFFINE,
    "text": UNIFORM_SCALING,
    "image": UNIFORM_SCALING,
    "use": TRANSLATION,
}

_PROBES: Final = {
    Feature.TRANSLATE: Translate(3, 4),
    Feature.SCALE: Scale(2),
    Feature.NON_UNIFORM_SCALE: Scale(2, 3),
    Feature.QUARTER_TURN: Rotate(90),
    Feature.ROTATE: Rotate(37),
    Feature.MIRROR: Scale(-1, 1),
    Feature.SKEW: SkewX(20),
}


@pytest.mark.parametrize("name", sorted(_ABSORBS))
@pytest.mark.parametrize(
    "feature", sorted(_PROBES, key=operator.attrgetter("name"))
)
def test_each_element_absorbs_exactly_what_it_can_express(
    name: str, feature: Feature
) -> None:
    element = _shapes()[name]
    probe = _PROBES[feature]
    element.transform = [probe]

    element.reify()

    absorbed = not element.transform

    assert absorbed == (feature in _ABSORBS[name]), (
        f"{name} {'absorbed' if absorbed else 'refused'} {probe}"
    )


def test_a_stroked_shape_refuses_to_be_distorted() -> None:
    # a stroke of uniform width has no non-uniformly scaled counterpart
    path = Path(
        d=PathData.from_str("M 0,0 L 10,10"),
        stroke=Color("black"),
        transform=[Scale(2, 3)],
    )
    path.reify()

    assert path.transform == [Scale(2, 3)]


def test_a_shape_with_a_non_scaling_stroke_may_be_distorted() -> None:
    path = Path(
        d=PathData.from_str("M 0,0 L 10,10"),
        stroke=Color("black"),
        stroke_width=Length(4),
        vector_effect="non-scaling-stroke",
        transform=[Scale(2, 3)],
    )
    path.reify()

    assert path.transform is None
    assert path.stroke_width == Length(4)


def test_a_dashed_rect_refuses_to_be_turned() -> None:
    # the dash pattern starts at a corner the specification fixes, and a
    # quarter turn moves that corner somewhere else
    rect = _rect(
        stroke=Color("black"),
        stroke_dasharray=[Length(4), Length(2)],
        transform=[Rotate(90)],
    )
    rect.reify()

    assert rect.transform == [Rotate(90)]


def test_a_shape_with_markers_may_only_be_moved() -> None:
    marker = Marker(id="m")
    polyline = Polyline(
        points=[Point(0, 0), Point(10, 10)],
        marker_end=marker.get_func_iri(),
        transform=[Scale(2)],
    )
    Svg().add_children(Defs().add_child(marker), polyline)

    polyline.reify()

    assert polyline.transform == [Scale(2)]


def test_a_percentage_length_blocks_reification() -> None:
    rect = Rect(
        x=Length(10),
        y=Length(10),
        width=Length(50, "%"),
        height=Length(20),
        transform=[Scale(2)],
    )
    rect.reify()

    assert rect.transform == [Scale(2)]
    assert rect.width == Length(50, "%")


def test_a_singular_transformation_is_left_alone() -> None:
    # a shape scaled to nothing cannot be recovered from its geometry
    polygon = Polygon(
        points=[Point(0, 0), Point(10, 10)], transform=[Scale(0)]
    )
    polygon.reify()

    assert polygon.transform == [Scale(0)]


# endregion


def test_a_non_scaling_stroke_keeps_its_dash_pattern() -> None:
    # the whole stroke, dashes included, is laid out in a coordinate system
    # the element's own transformation is no part of
    path = Path(
        d=PathData.from_str("M 0,0 L 10,10"),
        stroke=Color("black"),
        stroke_width=Length(4),
        stroke_dasharray=[Length(6), Length(3)],
        stroke_dashoffset=Length(2),
        vector_effect="non-scaling-stroke",
        transform=[Scale(2)],
    )
    path.reify()

    assert path.transform is None
    assert path.stroke_width == Length(4)
    assert path.stroke_dasharray == [Length(6), Length(3)]
    assert path.stroke_dashoffset == Length(2)


def test_a_text_path_is_left_to_the_path_it_follows() -> None:
    # `startOffset` is a distance along a path defined somewhere else, so
    # resizing the one without the other would pull them apart
    text_path = TextPath(
        startOffset=Length(20), font_size=Length(12), transform=[Scale(2)]
    )
    text_path.reify()

    assert text_path.transform == [Scale(2)]
    assert text_path.startOffset == Length(20)


def test_a_group_hands_a_uniform_scale_to_a_text_subtree() -> None:
    tspan = Tspan(x=[Length(5)], y=[Length(6)], font_size=Length(8))
    text = Text(
        x=[Length(10)],
        y=[Length(20)],
        font_size=Length(12),
        transform=[Scale(2)],
    ).add_child(tspan)

    text.reify()

    assert text.transform is None
    assert text.x == [Length(20)]
    assert text.font_size == Length(24)
    assert tspan.x == [Length(10)]
    assert tspan.font_size == Length(16)


def test_a_text_element_refuses_to_be_mirrored() -> None:
    # flipping a glyph run means flipping the glyphs, which no attribute says
    text = Text(x=[Length(10)], y=[Length(20)], transform=[Scale(-1, 1)])
    text.reify()

    assert text.transform == [Scale(-1, 1)]


# the only elements with no geometry of their own whose transformation is
# nothing but their children's; `svg` joins them, but only when it is the
# outermost one, which is a fact about the tree rather than the class
_DELEGATES: Final = {"a", "clipPath", "g", "switch"}

_ELEMENT_CLASSES: Final = sorted(set(ELEMENT_NAME_TO_NORMALIZED.values()))


@pytest.mark.parametrize("class_name", _ELEMENT_CLASSES)
def test_only_geometryless_containers_delegate_their_transform(
    class_name: str,
) -> None:
    # an element that renders content of its own must not be counted as a
    # mere container: handing its transformation to children it does not
    # have would lose it silently
    element: Element = getattr(svglab, class_name)()

    delegates = isinstance(
        element, TransformInheritedByChildren
    ) and not has_own_geometry(element)

    assert delegates == (element_name(element) in _DELEGATES)


@pytest.mark.parametrize("class_name", _ELEMENT_CLASSES)
def test_an_element_that_can_absorb_nothing_keeps_its_transform(
    class_name: str,
) -> None:
    element: Element = getattr(svglab, class_name)()

    if geometry_capability(element) or isinstance(
        element, TransformInheritedByChildren
    ):
        return

    element.transform = [Scale(2)]
    element.reify()

    assert element.transform == [Scale(2)], element_name(element)


def test_a_transformation_that_nearly_collapses_the_plane_is_refused() -> (
    None
):
    # undoing it would need coordinates far larger than the ones it acts on,
    # and the precision lost on the way back is precision the shape needed
    polygon = Polygon(
        points=[Point(0, 0), Point(10, 10)], transform=[Scale(1e6, 1e-6)]
    )
    polygon.reify()

    assert polygon.transform == [Scale(1e6, 1e-6)]


def test_a_percentage_coordinate_blocks_reification() -> None:
    # a position given as a fraction of a viewport reification cannot see is
    # one that cannot be rewritten at all, not even by a move
    rect = _rect(x=Length(25, "%"), transform=[Translate(5, 5)])
    rect.reify()

    assert rect.transform == [Translate(5, 5)]
    assert rect.x == Length(25, "%")


def test_text_with_no_resolvable_font_size_is_only_moved() -> None:
    # the glyphs are drawn at whatever size the renderer picks, which no
    # attribute records and reification therefore cannot resize
    text = Text(x=[Length(10)], y=[Length(20)], transform=[Scale(2)])
    text.reify()

    assert text.transform == [Scale(2)]


def test_an_inherited_font_size_is_resized_on_the_element_using_it() -> (
    None
):
    # the group is shared with elements this transformation does not reach,
    # so the resized value belongs on the text
    text = Text(x=[Length(10)], y=[Length(20)])
    group = G(transform=[Scale(2)], font_size=Length(20)).add_child(text)

    group.reify()

    assert group.font_size == Length(20)
    assert text.font_size == Length(40)


def test_an_inherited_dash_pattern_is_resized_on_the_shape_using_it() -> (
    None
):
    path = Path(d=PathData.from_str("M 0,0 L 10,10"))
    group = G(
        transform=[Scale(2)],
        stroke=Color("black"),
        stroke_dasharray=[Length(8), Length(4)],
        stroke_dashoffset=Length(3),
    ).add_child(path)

    group.reify()

    assert group.stroke_dasharray == [Length(8), Length(4)]
    assert path.stroke_dasharray == [Length(16), Length(8)]
    assert path.stroke_dashoffset == Length(6)


def test_a_text_element_waits_for_a_child_that_cannot_follow() -> None:
    # `font-size` is inherited, so folding the scale into the text while the
    # textPath kept it as a transformation would apply it to the glyphs twice
    text_path = TextPath(startOffset=Length(5))
    text = Text(
        x=[Length(0)],
        y=[Length(0)],
        font_size=Length(14),
        transform=[Scale(2)],
    ).add_child(text_path)

    text.reify()

    assert text.transform == [Scale(2)]
    assert text.font_size == Length(14)
    assert text_path.transform is None


def test_an_unstroked_shape_does_not_gain_a_stroke_width() -> None:
    path = Path(
        d=PathData.from_str("M 0,0 L 10,10"),
        fill=Color("red"),
        transform=[Scale(2)],
    )
    path.reify()

    assert path.transform is None
    assert path.stroke_width is None


def test_an_unusable_transform_origin_leaves_the_element_alone() -> None:
    # `center` and percentages are resolved against a box reification cannot
    # see, so there is nothing to decompose the origin into
    for origin in ("center", (Length(50, "%"), Length(50, "%"))):
        rect = _rect(transform=[Scale(2)], transform_origin=origin)
        rect.reify()

        assert rect.transform == [Scale(2)]
        assert rect.transform_origin == origin


def test_a_deeply_nested_document_does_not_exhaust_the_stack() -> None:
    svg = Svg(width=Length(100), height=Length(100))
    node: Element = svg

    for _ in range(5000):
        group = G(transform=[Translate(0.01, 0.01)])
        node.add_child(group)
        node = group

    node.add_child(
        Rect(x=Length(1), y=Length(1), width=Length(2), height=Length(2))
    )

    svg.reify()

    x = svg.find(Rect).x

    assert x is not None
    assert float(x) == pytest.approx(51)


def test_a_reference_cycle_does_not_hang() -> None:
    first = Use(
        id="a", href=Iri(fragment="b"), transform=[Translate(1, 1)]
    )
    second = Use(id="b", href=Iri(fragment="a"))
    svg = Svg(width=Length(100), height=Length(100)).add_children(
        first, second
    )

    svg.reify()


@pytest.mark.parametrize(
    "shape",
    [
        Rect(x=Length(1), y=Length(1)),
        Circle(r=Length(0)),
        Path(d=PathData()),
        Path(),
        Polygon(points=[]),
        Polyline(points=[Point(1, 1)]),
        Path(d=PathData.from_str("M 0,0 A 0 0 0 0 1 10,10")),
    ],
    ids=element_name,
)
@pytest.mark.parametrize(
    "transformation",
    [
        Scale(0),
        Scale(2, 3),
        SkewX(40),
        Matrix(0, 0, 0, 0, 0, 0),
        Translate(1e9, 1e9),
    ],
    ids=["singular", "non-uniform", "skew", "zero-matrix", "huge"],
)
def test_degenerate_geometry_produces_no_nonsense(
    shape: Element, transformation: TransformFunction
) -> None:
    element = copy.deepcopy(shape)
    element.transform = [transformation]
    svg = Svg(width=Length(100), height=Length(100)).add_child(element)

    svg.reify()

    xml = svg.to_xml(pretty=False).lower()

    assert "nan" not in xml
    assert "inf" not in xml


# region Every element, every attribute SVG gives a geometric type


_POSITIONS: Final = frozenset(
    {
        "x",
        "y",
        "cx",
        "cy",
        "fx",
        "fy",
        "x1",
        "y1",
        "x2",
        "y2",
        "d",
        "points",
    }
)
"""Geometric attributes that say where the element is."""

_MAGNITUDES: Final = (
    GEOMETRIC_ATTR_NAMES
    - _POSITIONS
    - {"transform", "gradientTransform", "patternTransform"}
)
"""Geometric attributes that say how big it is."""

_SAMPLES: Final = [
    Length(7),
    7.0,
    [Length(7)],
    [Length(7), Length(3)],
    Point(7, 3),
    [Point(7, 3), Point(1, 2)],
    PathData.from_str("M 7,3 L 11,5"),
]

# (the transformation moves every point, it resizes every extent)
_DEMANDS: Final[dict[str, tuple[Transform, bool, bool]]] = {
    "translate": ([Translate(11, 13)], True, False),
    "scale": ([Scale(2)], True, True),
    "scale-nonuniform": ([Scale(2, 3)], True, True),
    "rotate": ([Rotate(37)], True, False),
    "matrix": ([Matrix(1.3, 0.4, -0.25, 1.1, 6, 4)], True, True),
}


def _fill_geometry(element: Element) -> dict[str, object]:
    """Give every geometric attribute the element has a distinctive value."""
    filled: dict[str, object] = {}

    for name in sorted(GEOMETRIC_ATTR_NAMES):
        field = ATTR_NAME_TO_NORMALIZED.get(name)

        if field is None or field not in type(element).model_fields:
            continue
        if name in {"transform", "gradientTransform", "patternTransform"}:
            continue

        for sample in _SAMPLES:
            try:
                setattr(element, field, copy.deepcopy(sample))
            except (ValueError, TypeError):
                continue

            filled[field] = getattr(element, field, None)
            break

    return filled


@pytest.mark.parametrize("class_name", _ELEMENT_CLASSES)
@pytest.mark.parametrize("kind", sorted(_DEMANDS))
def test_absorbed_geometry_never_goes_stale(
    class_name: str, kind: str
) -> None:
    # whatever an element takes on, every attribute that says where it is or
    # how big it is has to have moved with it
    transformation, moves, resizes = _DEMANDS[kind]

    element: Element = getattr(svglab, class_name)(
        **({"element_name": "x"} if class_name == "UnknownElement" else {})
    )
    before = _fill_geometry(element)

    if not before:
        return

    element.main_transform = copy.deepcopy(transformation)
    Svg(width=Length(100), height=Length(100)).add_child(element)

    element.reify()

    if element.main_transform:
        return  # nothing was taken on, so nothing had to keep up

    for field, was in before.items():
        name = ATTR_NAME_TO_NORMALIZED.inverse[field]
        expected_to_change = (moves and name in _POSITIONS) or (
            resizes and name in _MAGNITUDES
        )

        if expected_to_change:
            assert getattr(element, field, None) != was, (
                f"{element_name(element)}.{name} was left behind"
            )


def test_geometry_the_library_cannot_read_stops_reification() -> None:
    # an attribute svglab does not model for this element survives as a
    # string; reification would rewrite everything around it and leave it
    rect = _rect(transform=[Scale(2)])
    rect["rx"] = "2"

    rect.reify()

    assert rect.transform == [Scale(2)]
    assert rect["rx"] == "2"


def test_the_marker_shorthand_counts_as_a_marker() -> None:
    marker = Marker(id="m")
    polyline = Polyline(
        points=[Point(0, 0), Point(9, 9)], transform=[Scale(2)]
    )
    polyline["marker"] = "url(#m)"
    Svg().add_children(Defs().add_child(marker), polyline)

    polyline.reify()

    assert polyline.transform == [Scale(2)]


def test_a_tref_carries_the_text_positioning_attributes() -> None:
    tref = Tref(
        x=[Length(10)],
        y=[Length(20)],
        font_size=Length(12),
        transform=[Scale(2)],
    )
    Text().add_child(tref)

    tref.reify()

    assert tref.transform is None
    assert tref.x == [Length(20)]
    assert tref.font_size == Length(24)


# endregion
