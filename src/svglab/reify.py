"""Turning transformations into geometry.

Reification removes a transformation from an element by folding it into the
element's own geometry: its coordinates, lengths, path data, and so on. The
result is an element that looks the same but no longer carries a `transform`
attribute.

Not every element can absorb every transformation. A `<rect>` has no attribute
that could express a rotation, and a `<text>` cannot be mirrored by rewriting
attributes at all -- the glyphs themselves would have to be flipped. This
module describes what an element can absorb as a set of `Feature`s, splits a
transformation matrix into the part an element can take and the part that has
to stay behind, and applies the former.

The traits in this module (`AffineGeometry` and friends) declare what an
element class is able to absorb. They are combined with facts that can only be
known at runtime -- whether the element is stroked, whether its lengths are
expressed in percentages -- by `geometry_capability`.
"""

from __future__ import annotations

import enum
import math
from collections.abc import Iterator, Mapping

from typing_extensions import Final, TypeAlias, cast

from svglab import errors
from svglab.attrparse import length, point, transform
from svglab.attrs import attrdefs
from svglab.utils import mathutils


@enum.unique
class Feature(enum.Enum):
    """An elementary thing a transformation can do to a shape.

    Every affine transformation is a combination of these. They are the
    vocabulary in which an element states what it is able to express using
    its own attributes.
    """

    TRANSLATE = "translation"
    """Moving the shape."""

    SCALE = "uniform scaling"
    """Resizing the shape by the same factor along both axes."""

    NON_UNIFORM_SCALE = "non-uniform scaling"
    """Resizing the shape by differing factors along the two axes."""

    QUARTER_TURN = "quarter turn"
    """Rotating the shape by a multiple of 90 degrees."""

    ROTATE = "rotation"
    """Rotating the shape by an arbitrary angle."""

    MIRROR = "mirroring"
    """Flipping the shape over, reversing its orientation."""

    SKEW = "skewing"
    """Slanting the shape, so that its right angles stop being right."""


Capability: TypeAlias = frozenset[Feature]
"""The set of features an element is able to express using its attributes."""

NOTHING: Final[Capability] = frozenset()
"""An element that cannot absorb any transformation at all."""

TRANSLATION: Final[Capability] = frozenset({Feature.TRANSLATE})
"""An element that can only be moved."""

UNIFORM_SCALING: Final[Capability] = TRANSLATION | {Feature.SCALE}
"""An element that can be moved and resized by one factor along both axes."""

UPRIGHT: Final[Capability] = UNIFORM_SCALING | {Feature.NON_UNIFORM_SCALE}
"""An element that can be moved and resized, but never turned or flipped."""

SIMILARITY: Final[Capability] = UNIFORM_SCALING | {
    Feature.QUARTER_TURN,
    Feature.ROTATE,
    Feature.MIRROR,
}
"""An element that survives anything that preserves angles."""

RECTILINEAR: Final[Capability] = UNIFORM_SCALING | {
    Feature.QUARTER_TURN,
    Feature.NON_UNIFORM_SCALE,
    Feature.MIRROR,
}
"""An element that survives anything that keeps the axes axis-aligned."""

AFFINE: Final[Capability] = SIMILARITY | RECTILINEAR | {Feature.SKEW}
"""An element that survives any transformation whatsoever."""

MAX_CONDITION_NUMBER: Final = 1e6
"""How lopsided a transformation may be and still be worth reifying.

A transformation close to collapsing the plane onto a line cannot be undone
accurately, and folding one into an element's geometry produces enormous
coordinates that lose the very precision that was meant to be preserved.
"""


# region Traits


class AffineGeometry:
    """The element's geometry is a set of points, so nothing distorts it.

    Applies to elements whose shape is given by explicit coordinates -- path
    data, a list of points, a pair of end points. Any affine transformation
    can be applied to those coordinates one by one.
    """


class RectilinearGeometry:
    """The element's geometry is an axis-aligned box.

    Applies to elements described by a position and a pair of extents, such
    as `rect` and `ellipse`. Such an element survives anything that maps the
    axes onto the axes, but a rotation or a skew would turn it into a shape
    it cannot describe.
    """


class SimilarityGeometry:
    """The element's geometry is described by a single radius.

    Applies to `circle` and to the gradients, whose defining geometry is a
    circle or a direction. Scaling the two axes differently would turn the
    circle into an ellipse and tilt the gradient's iso-lines.
    """


class UniformlyScalableGeometry:
    """The element's content can only be moved and resized.

    Applies to elements whose appearance is not determined by their
    attributes alone -- glyph runs and bitmaps. Turning or flipping those
    means turning or flipping the content, which rewriting attributes cannot
    do.
    """


class TranslatableGeometry:
    """The element's geometry can only be moved.

    Applies to elements that establish a viewport or a reference to other
    content, where resizing the element does not resize what is inside it.
    """


class ViewportEstablishing:
    """The element's attributes describe a viewport its content lives in.

    The transformation of such an element applies to the viewport as a whole,
    so it must not also be handed to the content -- that would apply it
    twice. The one exception is the outermost `svg`, whose viewport is the
    canvas itself and whose transformation therefore applies to its content.
    """


class DocumentFragmentRoot:
    """The element can stand as the root of an SVG document fragment.

    Only `svg` can. When it does, its `x`, `y`, `width` and `height` describe
    the canvas rather than a box placed on one, so a transformation on it
    applies to its content -- exactly as it would on a `g`.
    """


class Animation:
    """The element animates an attribute of another element over time.

    An animation records values in the coordinate system the document was
    written in, so reification has to leave the element it targets alone.
    """


class Stylesheet:
    """The element carries CSS that can restyle anything in the document.

    Reification cannot tell which elements a selector picks out, so a rule
    that sets a property it depends on puts that property out of reach
    everywhere.
    """


class RenderedIndirectly:
    """The element is not painted where it sits in the tree.

    It takes effect only through a reference from somewhere else, in the
    coordinate system of whatever refers to it. A transformation on an
    ancestor therefore does not reach it, and must not be pushed into it.
    """


class TransformInheritedByChildren:
    """The element's children live in the coordinate system it establishes.

    A transformation on such an element is equivalent to the same
    transformation on every one of its children, which is what lets
    reification push a transformation down the tree until it reaches elements
    that can absorb it.

    This is *not* true of elements that establish a new viewport, such as a
    nested `svg`: there, the transformation applies to the viewport as a
    whole, and pushing it down as well would apply it twice.
    """


class PositionedByReference:
    """The element is laid out along another element it refers to.

    A `textPath` takes its position, and the meaning of its `startOffset`,
    from the path it is attached to. Changing its own attributes without
    changing that path's would pull the two apart.
    """


class PercentageDefaults:
    """The element's unset geometry attributes default to percentages.

    A gradient whose coordinates are left out is not at the origin: it spans
    the box it is painted onto. Until every coordinate is spelled out there
    is nothing to fold a transformation into.
    """


class ImplicitlyOrientedShape:
    """The element's outline is traversed in a direction fixed by the spec.

    A `rect` is always stroked from its top-left corner clockwise. Mirroring
    or turning such a shape moves the corner the stroke starts from, which
    shifts the phase of a dash pattern -- something no attribute can correct.
    Shapes given by explicit coordinates do not have this problem, because
    mirroring their coordinates leaves the order of the coordinates alone.
    """


class FontSizeScaled:
    """The element renders glyphs, so its `font-size` should be resized.

    `font-size` is inherited, so only the elements that actually draw text
    resolve and resize it. Resizing it on a container as well would apply the
    factor twice to any descendant that keeps a transformation of its own.
    """


class StrokeWidthScaled:
    """The element's `stroke-width` attribute should be scaled.

    Only elements that actually stroke something scale their `stroke-width`.
    On a container, the transformation is pushed down to the children, each
    of which scales its own (possibly inherited) `stroke-width`, so scaling
    the container's value as well would apply the factor twice.
    """


# endregion
# region Classifying a matrix


def _is_quarter_turn(angle: float, /) -> bool:
    remainder = angle % 90

    return mathutils.is_close(remainder, 0) or mathutils.is_close(
        remainder, 90
    )


def features(matrix: transform.Matrix, /) -> Capability:
    """Determine what a transformation matrix actually does.

    Args:
        matrix: The matrix to classify.

    Returns:
        The set of features needed to express the transformation. An element
        can absorb the matrix exactly when this set is a subset of what the
        element is capable of.

    Raises:
        SvgSingularMatrixError: If the matrix is singular. A singular
            transformation collapses the shape onto a line or a point and
            cannot be expressed as geometry.

    Examples:
        >>> from svglab.attrparse.transform import Rotate, Scale, Translate
        >>> features(Translate(10, 20).to_matrix()) == TRANSLATION
        True
        >>> sorted(f.value for f in features(Scale(2, 3).to_matrix()))
        ['non-uniform scaling', 'uniform scaling']
        >>> features(Rotate(45).to_matrix()) == {Feature.ROTATE}
        True

    """
    result: set[Feature] = set()

    if not mathutils.is_close(matrix.e, 0) or not mathutils.is_close(
        matrix.f, 0
    ):
        result.add(Feature.TRANSLATE)

    rotation, rest = matrix.qr_decompose()
    angle = rotation.rotation_angle()

    if not mathutils.is_close(angle, 0):
        result.add(
            Feature.QUARTER_TURN
            if _is_quarter_turn(angle)
            else Feature.ROTATE
        )

    # `rest` is upper triangular: its diagonal holds the scale factors along
    # the two axes and its off-diagonal entry is the shear
    if not mathutils.is_close(rest.c, 0):
        result.add(Feature.SKEW)

    if rest.d < 0:
        result.add(Feature.MIRROR)

    if not mathutils.is_close(rest.a, abs(rest.d)):
        result.add(Feature.NON_UNIFORM_SCALE)

    if not mathutils.is_close(rest.a, 1) or not mathutils.is_close(
        abs(rest.d), 1
    ):
        result.add(Feature.SCALE)

    return frozenset(result)


def is_similarity(matrix: transform.Matrix, /) -> bool:
    """Check whether a transformation preserves angles.

    A similarity is the most a stroked shape can absorb: anything more turns
    a stroke of uniform width into one that varies along the outline.

    Examples:
        >>> from svglab.attrparse.transform import Rotate, Scale
        >>> is_similarity(Rotate(45).to_matrix())
        True
        >>> is_similarity(Scale(2, 3).to_matrix())
        False

    """
    return not matrix.is_singular() and features(matrix) <= SIMILARITY


def uniform_scale_factor(matrix: transform.Matrix, /) -> float:
    """Compute the factor by which a similarity resizes lengths.

    Examples:
        >>> from svglab.attrparse.transform import Rotate, Scale
        >>> uniform_scale_factor(Scale(3).to_matrix())
        3.0
        >>> uniform_scale_factor(Rotate(45).to_matrix())
        1.0

    """
    return math.sqrt(abs(matrix.determinant()))


def split(
    matrix: transform.Matrix, capability: Capability, /
) -> tuple[transform.Matrix, transform.Matrix]:
    """Split a transformation into a part to keep and a part to absorb.

    The matrix is factored as `residue @ absorbed`, with `absorbed` the
    largest right-hand factor that fits within `capability`. Taking the
    *right*-hand factor is what makes the split sound: the absorbed part acts
    on the element's own coordinates first, so everything preceding it is
    left undisturbed.

    Three factorizations are tried, in decreasing order of how much they
    remove: the whole matrix, the shape change that survives the rotation
    (which lets a `rect` take `scale(2 3)` out of `rotate(30) scale(2 3)`),
    and the trailing translation.

    Args:
        matrix: The transformation to split.
        capability: What the element can absorb.

    Returns:
        A 2-tuple `(residue, absorbed)` whose composition equals `matrix`.
        `absorbed` is the identity if nothing can be absorbed.

    Examples:
        >>> from svglab.attrparse.transform import Rotate, Translate
        >>> m = Rotate(90) @ Translate(10, 20)
        >>> residue, absorbed = split(m, TRANSLATION)
        >>> residue == Rotate(90).to_matrix()
        True
        >>> absorbed == Translate(10, 20).to_matrix()
        True

    """
    identity = transform.Matrix.identity()

    if matrix.condition_number() > MAX_CONDITION_NUMBER:
        # a transformation this lopsided cannot be factored accurately, and
        # the coordinates it would produce would not survive serialization
        return matrix, identity

    rotation, _ = matrix.qr_decompose()

    for residue in (identity, rotation, matrix.linear()):
        absorbed = residue.inverse() @ matrix

        if features(absorbed) <= capability:
            return residue, absorbed

    return matrix, identity


# endregion
# region Reading and writing attributes


def _is_convertible(attr: object, /) -> bool:
    """Check whether an attribute can take part in geometric arithmetic.

    Percentages and physical units are resolved against things reification
    knows nothing about -- the viewport, the font -- so a value expressed in
    them cannot be rewritten.
    """
    match attr:
        case length.Length():
            try:
                float(attr)
            except errors.SvgUnitConversionError:
                return False
            else:
                return True
        case list() | tuple():
            return all(_is_convertible(item) for item in attr)
        case _:
            return True


def _is_scalable(attr: object, /) -> bool:
    """Check whether an attribute holds a magnitude that can be resized.

    Keywords such as `medium` or `inherit` hold a magnitude that reification
    cannot resolve, so an element using one cannot be resized.
    """
    match attr:
        case None:
            return True
        case length.Length():
            return _is_convertible(attr)
        case int() | float():
            return True
        case list() | tuple():
            return all(_is_scalable(item) for item in attr)
        case _:
            return False


def _is_resizable(attr: object, /) -> bool:
    """Check whether an attribute holds a magnitude that is there to resize.

    Unlike `_is_scalable`, an absent value counts as unresizable: there is a
    magnitude in play, it just is not one reification can see.
    """
    return attr is not None and _is_scalable(attr)


def _get(element: object, name: str, /) -> object:
    # elements permit `del element.foo` on declared fields, so a default is
    # required even for attributes the element is known to have
    return getattr(element, name, None)


def _scaled(attr: object, /, by: float) -> object:
    """Resize a magnitude-valued attribute, leaving anything else alone."""
    match attr:
        case length.Length(_, "%"):
            return attr
        case int() | float() | length.Length():
            return attr * by
        case list() | tuple():
            return type(attr)(_scaled(item, by) for item in attr)
        case _:
            return attr


def _transform_point(
    matrix: transform.Matrix, x: object, y: object, /
) -> point.Point:
    return matrix @ point.Point(_number(x), _number(y))


def _number(attr: object, /) -> float:
    match attr:
        case None:
            return 0.0
        case length.Length():
            return float(attr)
        case int() | float():
            return float(attr)
        case _:
            msg = f"Expected a number, got {attr!r}"
            raise TypeError(msg)


def _coordinate(value: float, like: object, /) -> object:
    """Produce a value of the same flavour as an existing attribute."""
    return value if isinstance(like, int | float) else length.Length(value)


# endregion
# region Applying a matrix to attributes


def _swaps_axes(matrix: transform.Matrix, /) -> bool:
    return mathutils.is_close(matrix.a, 0) and mathutils.is_close(
        matrix.d, 0
    )


def is_box(element: object, /) -> bool:
    """Check whether the element's geometry is a position and two extents."""
    return (
        isinstance(element, attrdefs.WidthAttr)
        and isinstance(element, attrdefs.HeightAttr)
        and isinstance(element, attrdefs.XCoordinateAttr)
        and isinstance(element, attrdefs.YCoordinateAttr)
    )


def _apply_box(element: object, matrix: transform.Matrix, /) -> None:
    assert isinstance(element, attrdefs.WidthAttr)
    assert isinstance(element, attrdefs.HeightAttr)
    assert isinstance(element, attrdefs.XCoordinateAttr)
    assert isinstance(element, attrdefs.YCoordinateAttr)

    if features(matrix) <= TRANSLATION:
        # moving a box leaves its extents alone, which is the only thing that
        # can be done to one whose extents are a percentage of a viewport
        x = _translated(element.x or length.Length(0), matrix.e)
        y = _translated(element.y or length.Length(0), matrix.f)

        element.x = x  # type: ignore[assignment]
        element.y = y  # type: ignore[assignment]

        return

    x_value, y_value = _number(element.x), _number(element.y)
    width, height = _number(element.width), _number(element.height)

    # the image of an axis-aligned box under an axis-preserving matrix is
    # another axis-aligned box, which the two opposite corners pin down --
    # mirroring and quarter turns included, since taking the minimum moves
    # the anchor to whichever corner ended up at the top left
    start_corner = _transform_point(matrix, x_value, y_value)
    end_corner = _transform_point(
        matrix, x_value + width, y_value + height
    )

    element.x = length.Length(min(start_corner.x, end_corner.x))
    element.y = length.Length(min(start_corner.y, end_corner.y))

    if element.width is not None:
        element.width = length.Length(abs(end_corner.x - start_corner.x))
    if element.height is not None:
        element.height = length.Length(abs(end_corner.y - start_corner.y))

    _apply_radii(element, matrix)


def _apply_radii(element: object, matrix: transform.Matrix, /) -> None:
    """Resize the pair of radii an element carries.

    These are the corner radii of a `rect` and the semi-axes of an `ellipse`;
    both are extents along the two axes and both travel with them.
    """
    if not isinstance(element, attrdefs.RxAttr | attrdefs.RyAttr):
        return

    rx = _get(element, "rx")
    ry = _get(element, "ry")

    if rx is None and ry is None:
        return

    # an unset radius follows the one that is set, so it has to be spelled
    # out before the two axes go their separate ways
    rx = rx if rx is not None else ry
    ry = ry if ry is not None else rx

    if _swaps_axes(matrix):
        rx, ry = _scaled(ry, abs(matrix.c)), _scaled(rx, abs(matrix.b))
    else:
        rx, ry = _scaled(rx, abs(matrix.a)), _scaled(ry, abs(matrix.d))

    element.rx = rx  # type: ignore[reportAttributeAccessIssue]
    element.ry = ry  # type: ignore[reportAttributeAccessIssue]


def _apply_centre(element: object, matrix: transform.Matrix, /) -> None:
    assert isinstance(element, attrdefs.CxAttr)
    assert isinstance(element, attrdefs.CyAttr)

    centre = _transform_point(matrix, element.cx, element.cy)

    element.cx = length.Length(centre.x)
    element.cy = length.Length(centre.y)

    if isinstance(element, attrdefs.FxAttr | attrdefs.FyAttr):
        fx = _get(element, "fx")
        fy = _get(element, "fy")

        # an unset focal point sits at the centre, where it stays
        if fx is not None or fy is not None:
            focus = _transform_point(
                matrix,
                fx if fx is not None else element.cx,
                fy if fy is not None else element.cy,
            )

            element.fx = length.Length(focus.x)  # type: ignore[reportAttributeAccessIssue]
            element.fy = length.Length(focus.y)  # type: ignore[reportAttributeAccessIssue]

    factor = uniform_scale_factor(matrix)

    if isinstance(element, attrdefs.RAttr):
        element.r = _scaled(element.r, factor)  # type: ignore[reportAttributeAccessIssue]
    if isinstance(element, attrdefs.FrAttr):
        element.fr = _scaled(element.fr, factor)  # type: ignore[reportAttributeAccessIssue]
    _apply_radii(element, matrix)


def _apply_end_points(
    element: object, matrix: transform.Matrix, /
) -> None:
    assert isinstance(element, attrdefs.X1Attr)
    assert isinstance(element, attrdefs.Y1Attr)
    assert isinstance(element, attrdefs.X2Attr)
    assert isinstance(element, attrdefs.Y2Attr)

    start = _transform_point(matrix, element.x1, element.y1)
    end = _transform_point(matrix, element.x2, element.y2)

    element.x1 = _coordinate(start.x, element.x1)  # type: ignore[reportAttributeAccessIssue]
    element.y1 = _coordinate(start.y, element.y1)  # type: ignore[reportAttributeAccessIssue]
    element.x2 = _coordinate(end.x, element.x2)  # type: ignore[reportAttributeAccessIssue]
    element.y2 = _coordinate(end.y, element.y2)  # type: ignore[reportAttributeAccessIssue]


def _apply_text(element: object, matrix: transform.Matrix, /) -> None:
    """Move and resize the layout attributes of a text content element.

    Only translations and uniform scalings reach this, so every coordinate
    can be handled on its own axis.
    """
    factor = uniform_scale_factor(matrix)

    if isinstance(element, attrdefs.XListOfCoordinatesAttr):
        x = _translated(_scaled(element.x, factor), matrix.e)
        element.x = x  # type: ignore[assignment]
    if isinstance(element, attrdefs.YListOfCoordinatesAttr):
        y = _translated(_scaled(element.y, factor), matrix.f)
        element.y = y  # type: ignore[assignment]

    # a delta is a distance, so it is resized but never moved
    if isinstance(element, attrdefs.DxListOfLengthsAttr):
        element.dx = _scaled(element.dx, factor)  # type: ignore[reportAttributeAccessIssue]
    if isinstance(element, attrdefs.DyListOfLengthsAttr):
        element.dy = _scaled(element.dy, factor)  # type: ignore[reportAttributeAccessIssue]
    if isinstance(element, attrdefs.TextLengthAttr):
        element.textLength = _scaled(element.textLength, factor)  # type: ignore[reportAttributeAccessIssue]


def _translated(attr: object, /, by: float) -> object:
    match attr:
        case length.Length(_, "%"):
            return attr
        case int() | float():
            return attr + by
        case length.Length():
            return attr + length.Length(by)
        case list() | tuple():
            return type(attr)(_translated(item, by) for item in attr)
        case _:
            return attr


def _apply_magnitudes(
    element: object, matrix: transform.Matrix, /
) -> None:
    """Resize the lengths that describe how a shape is painted, not placed.

    These only make sense under a transformation that preserves angles: a
    stroke of uniform width has no non-uniformly scaled counterpart.

    They are also inherited, so each is resolved and written onto the element
    that actually uses it. Scaling a container's own value instead would
    double up on any descendant that keeps a transformation of its own, and
    would miss the descendants that spell out none of their own.
    """
    if not is_similarity(matrix):
        return

    factor = uniform_scale_factor(matrix)

    if mathutils.is_close(factor, 1):
        return

    if isinstance(element, FontSizeScaled):
        _scale_inherited(element, "font_size", factor)

    if _strokes_in_host_space(element) or not (
        isinstance(element, StrokeWidthScaled) and _is_stroked(element)
    ):
        # the whole stroke -- its width and its dash pattern alike -- is
        # either laid out in a coordinate system this transformation is no
        # part of, or not drawn at all
        return

    _scale_inherited(
        element, "stroke_width", factor, initial=length.Length(1)
    )

    # distance-along-a-path attributes and `pathLength` are proportional, so
    # a shape that declares its own path length needs no adjustment
    if (
        not isinstance(element, attrdefs.PathLengthAttr)
        or element.pathLength is None
    ):
        _scale_inherited(element, "stroke_dasharray", factor)
        _scale_inherited(element, "stroke_dashoffset", factor)


def inherited_value(element: object, name: str, /) -> object:
    """Resolve the value an element inherits for a property.

    An element that does not specify an inherited property uses the value of
    the nearest ancestor that specifies one.

    Args:
        element: The element whose inherited value to resolve.
        name: The name of the property, as a Python attribute name.

    Returns:
        The inherited value, or `None` if no ancestor specifies one.

    Examples:
        >>> from svglab import G, Length, Path
        >>> path = Path()
        >>> g = G(stroke_width=Length(5)).add_child(path)
        >>> inherited_value(path, "stroke_width")
        Length(value=5.0, unit=None)
        >>> inherited_value(Path(), "stroke_width") is None
        True

    """
    for ancestor in _ancestors(element):
        value = _get(ancestor, name)

        if value is not None and value != "inherit":
            return value

    return None


def resolved_value(
    element: object, name: str, /, *, initial: object = None
) -> object:
    """Resolve the value an inherited property has for an element.

    Args:
        element: The element to resolve the property for.
        name: The name of the property, as a Python attribute name.
        initial: The value the property takes when nothing specifies one.

    Returns:
        The element's own value, the one it inherits, or `initial`.

    Examples:
        >>> from svglab import G, Length, Path
        >>> path = Path(stroke_width=Length(2))
        >>> g = G(stroke_width=Length(5)).add_child(path)
        >>> resolved_value(path, "stroke_width")
        Length(value=2.0, unit=None)
        >>> resolved_value(Path(), "stroke_width", initial=Length(1))
        Length(value=1.0, unit=None)

    """
    own = _get(element, name)

    if own is not None and own != "inherit":
        return own

    inherited = inherited_value(element, name)

    return initial if inherited is None else inherited


def _scale_inherited(
    element: object, name: str, factor: float, /, *, initial: object = None
) -> None:
    """Resize an inherited magnitude, spelling it out if it was inherited.

    A value that came from an ancestor has to be written onto the element
    that uses it, because the ancestor is shared with elements this
    transformation does not reach.
    """
    own = _get(element, name)
    spelled_out = own is not None and own != "inherit"
    inherited = (
        None
        if spelled_out
        else resolved_value(element, name, initial=initial)
    )
    value = own if spelled_out else inherited

    if not isinstance(value, length.Length | list | int | float):
        # a keyword, or nothing at all; there is no magnitude to resize
        return

    scaled = _scaled(value, factor)
    setattr(element, name, scaled)

    # if the value was not spelled out and the scaled one is what the element
    # inherits anyway, there is no need to start spelling it out now
    if (
        isinstance(inherited, length.Length)
        and isinstance(scaled, length.Length)
        and scaled.unit == inherited.unit
        and mathutils.is_close(float(scaled), float(inherited))
    ):
        setattr(element, name, own)


def _strokes_in_host_space(element: object, /) -> bool:
    """Check whether the element's stroke ignores its coordinate system.

    `vector-effect: non-scaling-stroke` pins the stroke to the coordinate
    system of the nearest viewport, so folding a transformation into the
    geometry leaves the stroke exactly as it was.
    """
    return (
        isinstance(element, attrdefs.VectorEffectAttr)
        and element.vector_effect == "non-scaling-stroke"
    )


def scale_distance_along_a_path_attrs(element: object, by: float) -> None:
    """Scale distance-along-a-path attributes of the element.

    The attributes are:
    - `stroke-dasharray`
    - `stroke-dashoffset`

    Args:
        element: The element to scale.
        by: The factor by which to scale the attributes.

    """
    if isinstance(element, attrdefs.StrokeDasharrayAttr) and isinstance(
        element.stroke_dasharray, list
    ):
        dashes = [_scaled(dash, by) for dash in element.stroke_dasharray]
        element.stroke_dasharray = cast("list[length.Length]", dashes)
    if isinstance(element, attrdefs.StrokeDashoffsetAttr):
        element.stroke_dashoffset = _scaled(  # type: ignore[reportAttributeAccessIssue]
            element.stroke_dashoffset, by
        )


def apply(element: object, matrix: transform.Matrix, /) -> None:
    """Fold a transformation into the element's geometry attributes.

    The caller is responsible for checking that the element can absorb the
    matrix; see `split` and `geometry_capability`.

    Args:
        element: The element to transform.
        matrix: The transformation to apply.

    """
    if is_box(element):
        _apply_box(element, matrix)
    elif isinstance(element, attrdefs.CxAttr | attrdefs.CyAttr):
        _apply_centre(element, matrix)

    if isinstance(element, attrdefs.X1Attr):
        _apply_end_points(element, matrix)

    if (
        isinstance(element, attrdefs.PointsAttr)
        and element.points is not None
    ):
        element.points = [matrix @ p for p in element.points]

    if isinstance(element, attrdefs.DAttr) and element.d is not None:
        element.d = matrix @ element.d

    if isinstance(
        element, attrdefs.XListOfCoordinatesAttr | attrdefs.StartOffsetAttr
    ):
        _apply_text(element, matrix)

    _apply_magnitudes(element, matrix)


# endregion
# region Working out what an element can absorb


_POSITION_ATTRS: Final = (
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
    "dx",
    "dy",
)
"""Attributes that say where the element is."""

_MAGNITUDE_ATTRS: Final = (
    "width",
    "height",
    "r",
    "rx",
    "ry",
    "fr",
    "font_size",
    "textLength",
    "stroke_width",
    "stroke_dasharray",
    "stroke_dashoffset",
)
"""Attributes that say how big the element is."""


def _ancestors(element: object, /) -> Iterator[object]:
    ancestors = getattr(element, "ancestors", None)

    if ancestors is None:
        return

    yield from ancestors


def stretches_content(element: object, /) -> bool:
    """Check whether a viewport lets its content be distorted to fill it.

    A `preserveAspectRatio` of `none` stretches the content to the viewport
    instead of fitting it, which is what makes a non-uniform scaling of the
    viewport survive being folded into its attributes.

    Examples:
        >>> from svglab import Svg
        >>> stretches_content(Svg(preserveAspectRatio="none"))
        True
        >>> stretches_content(Svg())
        False

    """
    align, *_ = str(
        _get(element, "preserveAspectRatio") or "xMidYMid"
    ).split()

    return align == "none"


def _structural_capability(element: object, /) -> Capability:
    if isinstance(element, AffineGeometry):
        return AFFINE
    if isinstance(element, RectilinearGeometry):
        return RECTILINEAR
    if isinstance(element, SimilarityGeometry):
        return SIMILARITY
    if isinstance(element, UniformlyScalableGeometry):
        # a bitmap is mapped onto the box the same way a viewport maps its
        # content, so it stretches under exactly the same condition
        return (
            UPRIGHT
            if isinstance(element, ViewportEstablishing)
            and stretches_content(element)
            else UNIFORM_SCALING
        )

    if isinstance(element, TranslatableGeometry):
        if (
            isinstance(element, ViewportEstablishing)
            and _get(element, "viewBox") is not None
        ):
            # the content is mapped onto the viewport, so resizing the
            # viewport resizes the content along with it -- and stretches it
            # too, where the aspect ratio is not preserved
            return (
                UPRIGHT if stretches_content(element) else UNIFORM_SCALING
            )

        return TRANSLATION

    return NOTHING


def has_own_geometry(element: object, /) -> bool:
    """Check whether the element has geometry of its own to fold a matrix into.

    A `g` does not: a transformation on it belongs entirely to its children.
    """
    return _structural_capability(element) is not NOTHING


_STYLE_OPAQUE: Final = frozenset(
    {
        "transform",
        "transform-origin",
        "transform-box",
        "clip-path",
        "mask",
        "filter",
        "d",
    }
)
"""Properties that decide the geometry and that reification cannot rewrite."""

_STYLE_MAGNITUDES: Final = frozenset(
    {
        "stroke-width",
        "font-size",
        "stroke-dasharray",
        "stroke-dashoffset",
        "marker",
        "marker-start",
        "marker-mid",
        "marker-end",
        "vector-effect",
    }
)
"""Properties reification would have to resize but cannot reach in a style."""


def style_capability(element: object, /) -> Capability:
    """Work out what the element's `style` attribute leaves reifiable.

    A declaration in a `style` attribute overrides the presentation attribute
    of the same name, and reification rewrites attributes. Anything it would
    have had to rewrite, or would have had to read to decide what is safe, is
    out of reach there -- so the element keeps as much of its transformation
    as that costs.
    """
    declarations = style_declarations(element)

    if not declarations:
        return AFFINE

    if _STYLE_OPAQUE & declarations.keys():
        return NOTHING

    if any(
        "url(" in declarations.get(name, "") for name in ("fill", "stroke")
    ):
        # a paint server reification cannot resolve, so it cannot tell
        # whether the paint travels with the shape
        return NOTHING

    if _STYLE_MAGNITUDES & declarations.keys():
        return TRANSLATION

    return AFFINE


def stylesheet_capability(css: str, /) -> Capability:
    """Work out what a stylesheet leaves reifiable anywhere in the document.

    Which elements a selector picks out is not something reification can
    work out, so a rule mentioning a property it would have to rewrite costs
    that property everywhere.

    Args:
        css: The text of a stylesheet.

    Returns:
        The capability every element in the document is held to.

    Examples:
        >>> stylesheet_capability(".a { fill: red }") == AFFINE
        True
        >>> stylesheet_capability(
        ...     ".a { transform: rotate(3deg) }"
        ... ) == NOTHING
        True

    """
    # a property name is only interesting where it is declared, which is
    # after a brace and before a colon
    declared = {
        name.strip().lower()
        for block in css.split("{")[1:]
        for declaration in block.split("}")[0].split(";")
        for name, separator, _ in [declaration.partition(":")]
        if separator
    }

    if _STYLE_OPAQUE & declared:
        return NOTHING

    if _STYLE_MAGNITUDES & declared:
        return TRANSLATION

    return AFFINE


def geometry_capability(element: object, /) -> Capability:
    """Determine what transformations an element's attributes can express.

    This combines what the element's class is able to describe with facts
    that only hold for this particular element: whether its lengths can be
    resolved to user units, whether it is stroked, and whether it has the
    attributes a given transformation would have to be written into.

    Args:
        element: The element to inspect.

    Returns:
        The set of features the element can absorb.

    """
    capability = _structural_capability(element) & style_capability(
        element
    )

    if (
        not capability
        or isinstance(element, PositionedByReference)
        or _has_unreadable_geometry(element)
    ):
        return NOTHING

    if isinstance(
        element, PercentageDefaults
    ) and not _geometry_is_explicit(element):
        return NOTHING

    # a coordinate expressed as a percentage of something reification cannot
    # see is one that cannot be rewritten at all
    if not all(
        _is_convertible(_get(element, name)) for name in _POSITION_ATTRS
    ):
        return NOTHING

    if not all(
        _is_scalable(_get(element, name)) for name in _MAGNITUDE_ATTRS
    ):
        capability &= TRANSLATION

    if is_box(element) and (
        _get(element, "width") is None or _get(element, "height") is None
    ):
        # without both extents there is no box to map the corners of, so the
        # anchor cannot be moved to a different corner
        capability -= {Feature.MIRROR, Feature.QUARTER_TURN}

    if isinstance(element, FontSizeScaled) and not _is_resizable(
        resolved_value(element, "font_size")
    ):
        # the glyphs are drawn at a size reification cannot resolve -- a
        # keyword, or whatever the renderer picks by default -- so the
        # element may be moved but not resized
        capability &= TRANSLATION

    if _is_stroked(element):
        capability &= SIMILARITY

        if isinstance(element, ImplicitlyOrientedShape) and _is_dashed(
            element
        ):
            # the dash pattern starts at a corner the spec fixes, so moving
            # that corner somewhere else shifts the pattern
            capability &= UNIFORM_SCALING

    if _has_marker(element):
        # a marker is placed in user space and oriented along the path, so
        # anything but a move changes its size or its angle
        capability &= TRANSLATION

    return capability


def _geometry_is_explicit(element: object, /) -> bool:
    """Check that none of the element's defining coordinates are left out."""
    if isinstance(element, attrdefs.X1Attr):
        names = ("x1", "y1", "x2", "y2")
    elif isinstance(element, attrdefs.CxAttr):
        names = ("cx", "cy", "r")
    else:
        return True

    return all(_get(element, name) is not None for name in names)


def style_declarations(element: object, /) -> Mapping[str, str]:
    """Read the declarations of the element's `style` attribute.

    The `style` attribute is not parsed into typed attributes, but it decides
    what the element actually looks like: a declaration there beats the
    presentation attribute of the same name. Reification has to at least know
    what is in it, even where it cannot rewrite it.

    Args:
        element: The element to read.

    Returns:
        A mapping of property name to value, both stripped of whitespace and
        of any `!important`.

    Examples:
        >>> from svglab import Rect
        >>> rect = Rect(style="fill: red; stroke-width: 4 !important")
        >>> dict(style_declarations(rect))
        {'fill': 'red', 'stroke-width': '4'}

    """
    style = _get(element, "style")

    if not isinstance(style, str):
        return {}

    declarations: dict[str, str] = {}

    for declaration in style.split(";"):
        name, separator, value = declaration.partition(":")

        if not separator:
            continue

        declarations[name.strip().lower()] = value.replace(
            "!important", ""
        ).strip()

    return declarations


def _property(element: object, name: str, /) -> object:
    """Read a property, preferring the `style` declaration overriding it."""
    declared = style_declarations(element).get(name.replace("_", "-"))

    return _get(element, name) if declared is None else declared


def _own_or_inherited(element: object, name: str, /) -> object:
    value = _property(element, name)

    if value is not None and value != "inherit":
        return value

    for ancestor in _ancestors(element):
        value = _property(ancestor, name)

        if value is not None and value != "inherit":
            return value

    return None


def _is_stroked(element: object, /) -> bool:
    if _strokes_in_host_space(element):
        # the stroke ignores the coordinate system, so it constrains nothing
        return False

    stroke = _own_or_inherited(element, "stroke")

    return stroke is not None and stroke != "none"


def _is_dashed(element: object, /) -> bool:
    dasharray = _own_or_inherited(element, "stroke_dasharray")

    return isinstance(dasharray, list) and len(dasharray) > 0


_MARKER_ATTRS: Final = (
    "marker",
    "marker_start",
    "marker_mid",
    "marker_end",
)
"""The marker properties, shorthand included."""

GEOMETRIC_ATTR_NAMES: Final[frozenset[str]] = frozenset(
    {
        "cx",
        "cy",
        "d",
        "dx",
        "dy",
        "fx",
        "fy",
        "gradientTransform",
        "height",
        "markerHeight",
        "markerWidth",
        "patternTransform",
        "points",
        "r",
        "refX",
        "refY",
        "rx",
        "ry",
        "startOffset",
        "textLength",
        "transform",
        "width",
        "x",
        "x1",
        "x2",
        "y",
        "y1",
        "y2",
    }
)
"""Every attribute SVG 1.1 gives a coordinate, length or transform type.

Taken from the datatypes of the SVG 1.1 DTD. An element carrying one of
these as an *unparsed* extra attribute has geometry reification cannot see,
which is reason enough to leave it alone.
"""


def _has_unreadable_geometry(element: object, /) -> bool:
    """Check for geometry the element holds but the library has not parsed.

    An attribute svglab does not model for this element survives as a plain
    string. Reification would rewrite everything around it and leave it
    behind, so an element carrying one keeps its transformation.
    """
    extra = getattr(element, "extra_attrs", None)

    if extra is None:
        return False

    return bool(GEOMETRIC_ATTR_NAMES & extra().keys())


def _has_marker(element: object, /) -> bool:
    return any(
        _own_or_inherited(element, name) is not None
        for name in _MARKER_ATTRS
    )


# endregion
