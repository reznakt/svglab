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
import re
from collections.abc import Container, Iterator, Mapping

from typing_extensions import Final, NamedTuple, TypeAlias, cast, override

from svglab.attrparse.length import Length
from svglab.attrparse.point import Point
from svglab.attrparse.transform import Matrix
from svglab.attrs.attrdefs import (
    CxAttr,
    CyAttr,
    DAttr,
    DxListOfLengthsAttr,
    DyListOfLengthsAttr,
    FrAttr,
    FxAttr,
    FyAttr,
    HeightAttr,
    PathLengthAttr,
    PointsAttr,
    RAttr,
    RxAttr,
    RyAttr,
    StrokeDasharrayAttr,
    StrokeDashoffsetAttr,
    TextLengthAttr,
    WidthAttr,
    X1Attr,
    X2Attr,
    XCoordinateAttr,
    XListOfCoordinatesAttr,
    Y1Attr,
    Y2Attr,
    YCoordinateAttr,
    YListOfCoordinatesAttr,
)
from svglab.attrs.names import AttributeName
from svglab.errors import SvgUnitConversionError
from svglab.utils.mathutils import is_close


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


class _Everything:
    """A container that holds every value."""

    def __contains__(self, item: object, /) -> bool:
        return True


class Scope(NamedTuple):
    """How far an element's inherited properties can be seen.

    An element that something refers to with `use` is rendered twice over:
    where it sits, with the properties its ancestors pass down, and wherever
    the `use` is, with the properties the `use` passes down instead. A
    property that neither the element nor an ancestor up to the referenced
    one spells out may therefore differ between the two, and reification
    cannot rely on it.
    """

    boundary: object | None = None
    """The referenced ancestor-or-self past which inheritance is unknown."""

    declared: Container[str] = _Everything()
    """The properties, by their SVG names, declared anywhere in the document.

    A property nothing in the document declares takes its initial value
    everywhere, so it is known even past the boundary.
    """

    styled: Container[str] = frozenset()
    """The properties, by their SVG names, declared in a stylesheet.

    A stylesheet rule beats a presentation attribute, and which elements it
    picks out cannot be told, so such a property is unknown on every element
    whose own `style` attribute does not settle it.
    """

    animated: Container[str] = frozenset()
    """The properties, by their SVG names, an animation changes over time.

    An element inheriting one of them inherits a value that changes, which
    no number written onto the element could stand in for.
    """


class _Unknown:
    """The value of a property reification cannot determine."""

    @override
    def __repr__(self) -> str:
        return "UNKNOWN"


UNKNOWN: Final = _Unknown()
"""The value of an inherited property that lies beyond a `Scope`."""

WHOLE_DOCUMENT: Final = Scope()
"""The scope of an element nothing refers to: every ancestor can be seen."""


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


class Grouping:
    """The element does nothing but group its children.

    Stripped of its attributes, it no longer affects how its children are
    rendered, so they can take its place in the tree.
    """


class SelectsAChild:
    """The element renders only one of its direct children.

    Which one depends on its children themselves, so lifting the children of
    a group among them would change the choice.
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


class TransformIgnored:
    """The element has no `transform` attribute of its own to speak of.

    A `tspan` is laid out by the text it belongs to, and renderers ignore a
    `transform` written on it. Reification only ever hands it one the text
    absorbed, which is then folded into its coordinates.
    """


class PositionedByReference:
    """The element is laid out along another element it refers to.

    A `textPath` takes its position, and the meaning of its `startOffset`,
    from the path it is attached to. Changing its own attributes without
    changing that path's would pull the two apart.
    """


class PositionDefaultsToOrigin:
    """The element's unset `x` and `y` put it at the origin.

    A `text` without a position starts at `(0, 0)`, so moving it means
    spelling that position out. A `tspan` or `tref` without one carries on
    from wherever the text before it ended instead, which already follows
    the text it belongs to.
    """


class PercentageDefaults:
    """The element's unset geometry attributes default to percentages.

    A gradient whose coordinates are left out is not at the origin: it spans
    the box it is painted onto. Until every coordinate is spelled out there
    is nothing to fold a transformation into; see `spell_out_gradient`.
    """


class Markable:
    """The element's vertices can carry markers.

    Every shape can in SVG 2, not only the ones made of explicit points. A
    marker is placed in user space and oriented along the outline, so what
    a shape with markers can absorb depends on the marker.
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

    The spacing between the glyphs -- `letter-spacing`, `word-spacing` and
    `kerning` -- is a length in the same coordinate system, so it is resized
    along with it.

    These are inherited, so only the elements that actually draw text resolve
    and resize them. Resizing them on a container as well would apply the
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

    return is_close(remainder, 0) or is_close(remainder, 90)


def features(matrix: Matrix, /) -> Capability:
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

    if not is_close(matrix.e, 0) or not is_close(matrix.f, 0):
        result.add(Feature.TRANSLATE)

    rotation, rest = matrix.qr_decompose()
    angle = rotation.rotation_angle()

    if not is_close(angle, 0):
        result.add(
            Feature.QUARTER_TURN
            if _is_quarter_turn(angle)
            else Feature.ROTATE
        )

    # `rest` is upper triangular: its diagonal holds the scale factors along
    # the two axes and its off-diagonal entry is the shear
    if not is_close(rest.c, 0):
        result.add(Feature.SKEW)

    if rest.d < 0:
        result.add(Feature.MIRROR)

    if not is_close(rest.a, abs(rest.d)):
        result.add(Feature.NON_UNIFORM_SCALE)

    if not is_close(rest.a, 1) or not is_close(abs(rest.d), 1):
        result.add(Feature.SCALE)

    return frozenset(result)


def is_similarity(matrix: Matrix, /) -> bool:
    """Check whether a transformation preserves angles.

    A similarity is the most a stroked shape can absorb: anything more turns
    a stroke of uniform width into one that varies along the outline.

    Returns:
        `True` if the matrix is a similarity.

    Examples:
        >>> from svglab.attrparse.transform import Rotate, Scale
        >>> is_similarity(Rotate(45).to_matrix())
        True
        >>> is_similarity(Scale(2, 3).to_matrix())
        False

    """
    return not matrix.is_singular() and features(matrix) <= SIMILARITY


def uniform_scale_factor(matrix: Matrix, /) -> float:
    """Compute the factor by which a similarity resizes lengths.

    Returns:
        The factor.

    Examples:
        >>> from svglab.attrparse.transform import Rotate, Scale
        >>> uniform_scale_factor(Scale(3).to_matrix())
        3.0
        >>> uniform_scale_factor(Rotate(45).to_matrix())
        1.0

    """
    return math.sqrt(abs(matrix.determinant()))


def split(
    matrix: Matrix, capability: Capability, /
) -> tuple[Matrix, Matrix]:
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
    identity = Matrix.identity()

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

    Returns:
        `True` if the attribute can be converted to user units.

    """
    match attr:
        case Length():
            try:
                float(attr)
            except SvgUnitConversionError:
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

    Returns:
        `True` if the attribute is unset or holds a magnitude in user
        units.

    """
    match attr:
        case None:
            return True
        case Length():
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

    Returns:
        `True` if the attribute holds a magnitude in user units.

    """
    return attr is not None and _is_scalable(attr)


def _is_spacing_scalable(attr: object, /) -> bool:
    """Check whether a glyph spacing can be resized.

    `normal` and `auto` leave the spacing to the font, which is resized with
    the `font-size` already; any other keyword cannot be resolved.

    Returns:
        `True` if the spacing is left to the font or can be resized.

    """
    return attr in {"normal", "auto"} or _is_scalable(attr)


def _get(element: object, name: str, /) -> object:
    # elements permit `del element.foo` on declared fields, so a default is
    # required even for attributes the element is known to have
    return getattr(element, name, None)


def _scaled(attr: object, /, by: float) -> object:
    """Resize a magnitude-valued attribute, leaving anything else alone."""
    match attr:
        case Length(_, "%"):
            return attr
        case int() | float() | Length():
            return attr * by
        case list() | tuple():
            return type(attr)(_scaled(item, by) for item in attr)
        case _:
            return attr


def _transform_point(matrix: Matrix, x: object, y: object, /) -> Point:
    return matrix @ Point(_number(x), _number(y))


def _number(attr: object, /) -> float:
    match attr:
        case None:
            return 0.0
        case Length():
            return float(attr)
        case int() | float():
            return float(attr)
        case _:
            msg = f"Expected a number, got {attr!r}"
            raise TypeError(msg)


def _coordinate(value: float, like: object, /) -> object:
    """Produce a value of the same flavour as an existing attribute."""
    return value if isinstance(like, int | float) else Length(value)


def _set_coordinate(
    element: object, name: str, value: float, like: object, /
) -> None:
    """Write a coordinate, unless it was left out and stays at zero.

    Every coordinate this is used for defaults to zero, so an unset one that
    ends up at the origin already says what it has to.
    """
    if like is None and is_close(value, 0):
        return

    setattr(element, name, _coordinate(value, like))


_GRADIENT_DEFAULTS: Final = {
    "x1": 0.0,
    "y1": 0.0,
    "x2": 100.0,
    "y2": 0.0,
    "cx": 50.0,
    "cy": 50.0,
    "r": 50.0,
}
"""The percentage a gradient's unset coordinates default to."""

_VERTICAL: Final = frozenset({"y1", "y2", "cy", "fy"})
_RADIAL: Final = frozenset({"r", "fr"})


def spell_out_gradient(
    element: object, /, *, viewport: tuple[float, float] | None = None
) -> None:
    """Write out a gradient's geometry in numbers, defaults included.

    A gradient's coordinates default to percentages and may be written as
    such. In bounding box units a percentage is a fraction of the box, so it
    is written as that fraction. In user space it is a fraction of the
    viewport, so it can only be written out when the viewport's size is
    known; otherwise the percentages are left as they are.

    Args:
        element: The gradient.
        viewport: The width and height of the nearest viewport, in user
            units, if known.

    Examples:
        >>> from svglab import Length, LinearGradient, RadialGradient
        >>> gradient = LinearGradient(x1=Length(25, "%"))
        >>> spell_out_gradient(gradient)
        >>> gradient.x1, gradient.x2
        (Length(value=0.25, unit=None), Length(value=1.0, unit=None))
        >>> gradient = RadialGradient(gradientUnits="userSpaceOnUse")
        >>> spell_out_gradient(gradient, viewport=(200, 100))
        >>> gradient.cx, gradient.r
        (Length(value=100.0, unit=None), Length(value=79.056941504, unit=None))

    """
    in_user_space = _get(element, "gradientUnits") == "userSpaceOnUse"

    if in_user_space and viewport is None:
        return

    for name in (*_GRADIENT_DEFAULTS, "fx", "fy", "fr"):
        if not hasattr(element, name):
            continue

        match _get(element, name):
            case None if name in _GRADIENT_DEFAULTS:
                percentage = _GRADIENT_DEFAULTS[name]
            case Length(value, "%"):
                percentage = value
            case _:
                continue

        if in_user_space:
            assert viewport is not None
            width, height = viewport
            extent = (
                height
                if name in _VERTICAL
                else math.hypot(width, height) / math.sqrt(2)
                if name in _RADIAL
                else width
            )
        else:
            extent = 1.0

        setattr(element, name, Length(round(percentage / 100 * extent, 9)))


# endregion
# region Applying a matrix to attributes


def _swaps_axes(matrix: Matrix, /) -> bool:
    return is_close(matrix.a, 0) and is_close(matrix.d, 0)


def is_box(element: object, /) -> bool:
    """Check whether the element's geometry is a position and two extents."""
    return (
        isinstance(element, WidthAttr)
        and isinstance(element, HeightAttr)
        and isinstance(element, XCoordinateAttr)
        and isinstance(element, YCoordinateAttr)
    )


def _apply_box(element: object, matrix: Matrix, /) -> None:
    assert isinstance(element, WidthAttr)
    assert isinstance(element, HeightAttr)
    assert isinstance(element, XCoordinateAttr)
    assert isinstance(element, YCoordinateAttr)

    if features(matrix) <= TRANSLATION:
        # moving a box leaves its extents alone, which is the only thing that
        # can be done to one whose extents are a percentage of a viewport
        if element.x is not None or not is_close(matrix.e, 0):
            element.x = _translated(element.x or Length(0), matrix.e)  # type: ignore[assignment]
        if element.y is not None or not is_close(matrix.f, 0):
            element.y = _translated(element.y or Length(0), matrix.f)  # type: ignore[assignment]

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

    _set_coordinate(
        element, "x", min(start_corner.x, end_corner.x), element.x
    )
    _set_coordinate(
        element, "y", min(start_corner.y, end_corner.y), element.y
    )

    if element.width is not None:
        element.width = Length(abs(end_corner.x - start_corner.x))
    if element.height is not None:
        element.height = Length(abs(end_corner.y - start_corner.y))

    _apply_radii(element, matrix)


def _apply_radii(element: object, matrix: Matrix, /) -> None:
    """Resize the pair of radii an element carries.

    These are the corner radii of a `rect` and the semi-axes of an `ellipse`;
    both are extents along the two axes and both travel with them.
    """
    if not isinstance(element, RxAttr | RyAttr):
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


def _apply_centre(element: object, matrix: Matrix, /) -> None:
    assert isinstance(element, CxAttr)
    assert isinstance(element, CyAttr)

    cx, cy = element.cx, element.cy
    centre = _transform_point(matrix, cx, cy)

    _set_coordinate(element, "cx", centre.x, cx)
    _set_coordinate(element, "cy", centre.y, cy)

    if isinstance(element, FxAttr | FyAttr):
        fx = _get(element, "fx")
        fy = _get(element, "fy")

        # an unset focal point sits at the centre, where it stays; a half-set
        # one takes the other coordinate from the centre as it was written
        if fx is not None or fy is not None:
            focus = _transform_point(
                matrix,
                fx if fx is not None else cx,
                fy if fy is not None else cy,
            )

            element.fx = Length(focus.x)  # type: ignore[reportAttributeAccessIssue]
            element.fy = Length(focus.y)  # type: ignore[reportAttributeAccessIssue]

    factor = uniform_scale_factor(matrix)

    if isinstance(element, RAttr):
        element.r = _scaled(element.r, factor)  # type: ignore[reportAttributeAccessIssue]
    if isinstance(element, FrAttr):
        element.fr = _scaled(element.fr, factor)  # type: ignore[reportAttributeAccessIssue]
    _apply_radii(element, matrix)


def _apply_end_points(element: object, matrix: Matrix, /) -> None:
    assert isinstance(element, X1Attr)
    assert isinstance(element, Y1Attr)
    assert isinstance(element, X2Attr)
    assert isinstance(element, Y2Attr)

    start = _transform_point(matrix, element.x1, element.y1)
    end = _transform_point(matrix, element.x2, element.y2)

    _set_coordinate(element, "x1", start.x, element.x1)
    _set_coordinate(element, "y1", start.y, element.y1)
    _set_coordinate(element, "x2", end.x, element.x2)
    _set_coordinate(element, "y2", end.y, element.y2)


def _apply_text(element: object, matrix: Matrix, /) -> None:
    """Move and resize the layout attributes of a text content element.

    Only translations and uniform scalings reach this, so every coordinate
    can be handled on its own axis.
    """
    factor = uniform_scale_factor(matrix)

    if isinstance(element, XListOfCoordinatesAttr):
        x = _text_position(element, element.x, matrix.e)
        element.x = _translated(_scaled(x, factor), matrix.e)  # type: ignore[assignment]
    if isinstance(element, YListOfCoordinatesAttr):
        y = _text_position(element, element.y, matrix.f)
        element.y = _translated(_scaled(y, factor), matrix.f)  # type: ignore[assignment]

    # a delta is a distance, so it is resized but never moved
    if isinstance(element, DxListOfLengthsAttr):
        element.dx = _scaled(element.dx, factor)  # type: ignore[reportAttributeAccessIssue]
    if isinstance(element, DyListOfLengthsAttr):
        element.dy = _scaled(element.dy, factor)  # type: ignore[reportAttributeAccessIssue]
    if isinstance(element, TextLengthAttr):
        element.textLength = _scaled(element.textLength, factor)  # type: ignore[reportAttributeAccessIssue]


def _text_position(element: object, attr: object, by: float, /) -> object:
    """Spell out the origin an unset position stands for, if it moves."""
    if (
        attr is None
        and isinstance(element, PositionDefaultsToOrigin)
        and not is_close(by, 0)
    ):
        return [Length(0)]

    return attr


def _translated(attr: object, /, by: float) -> object:
    match attr:
        case Length(_, "%"):
            return attr
        case int() | float():
            return attr + by
        case Length():
            return attr + Length(by)
        case list() | tuple():
            return type(attr)(_translated(item, by) for item in attr)
        case _:
            return attr


def _apply_magnitudes(
    element: object,
    matrix: Matrix,
    scope: Scope,
    /,
    *,
    inherited_resized: bool,
) -> None:
    """Resize the lengths that describe how a shape is painted, not placed.

    These only make sense under a transformation that preserves angles: a
    stroke of uniform width has no non-uniformly scaled counterpart.

    They are also inherited, so each is resolved and written onto the element
    that actually uses it. Scaling a container's own value instead would
    double up on any descendant that keeps a transformation of its own, and
    would miss the descendants that spell out none of their own. The one
    container that does resize them is a text element handing the
    transformation to its spans: it draws glyphs itself, and what it writes
    onto itself its spans inherit already resized.
    """
    if not is_similarity(matrix):
        return

    factor = uniform_scale_factor(matrix)

    if is_close(factor, 1):
        return

    def resize(name: str, initial: object = None) -> None:
        if inherited_resized and not _is_specified(_get(element, name)):
            return

        _scale_inherited(element, name, factor, scope, initial=initial)

    if isinstance(element, FontSizeScaled):
        for name in _FONT_MAGNITUDES:
            resize(name)

    if not (
        isinstance(element, StrokeWidthScaled)
        and _is_stroked(element, scope)
    ):
        # the whole stroke -- its width and its dash pattern alike -- is
        # either laid out in a coordinate system this transformation is no
        # part of, or not drawn at all
        return

    resize("stroke_width", Length(1))

    # distance-along-a-path attributes and `pathLength` are proportional, so
    # a shape that declares its own path length needs no adjustment
    if (
        not isinstance(element, PathLengthAttr)
        or element.pathLength is None
    ):
        resize("stroke_dasharray")
        resize("stroke_dashoffset")


def _is_specified(value: object, /) -> bool:
    return value is not None and value != "inherit"


def _unknown_unless_initial(name: str, scope: Scope, /) -> object:
    """Say what a property is where it cannot be followed any further.

    Returns:
        `UNKNOWN`, or `None` for a property nothing in the document
        declares, which is at its initial value everywhere.

    """
    return UNKNOWN if name in scope.declared else None


def property_value(
    element: object,
    name: str,
    /,
    *,
    initial: object = None,
    scope: Scope = WHOLE_DOCUMENT,
) -> object:
    """Resolve a property the way the element is rendered with it.

    The element's own value wins, then the nearest ancestor's, then
    `initial`. A declaration in a `style` attribute beats the presentation
    attribute of the same name, on the element itself and on every ancestor,
    and is returned as the string it was written as.

    The scope says where that stops being certain: past the element a `use`
    refers to, under a stylesheet rule that may set the property on any
    element, and for a value an animation changes over time.

    Args:
        element: The element to resolve the property for.
        name: The name of the property, as a Python attribute name.
        initial: The value the property takes when nothing specifies one.
        scope: How far up the tree inheritance can be seen.

    Returns:
        The value, `initial` if nothing specifies one, or `UNKNOWN` if it
        cannot be told.

    Examples:
        >>> from svglab import Color, G, Length, Path
        >>> own, inheriting = Path(fill=Color("red")), Path()
        >>> g = G(style="fill: url(#p)").add_children(own, inheriting)
        >>> property_value(own, "fill")
        Color('red')
        >>> property_value(inheriting, "fill")
        'url(#p)'
        >>> property_value(Path(), "stroke_width", initial=Length(1))
        Length(value=1.0, unit=None)
        >>> property_value(
        ...     inheriting, "fill", scope=Scope(boundary=inheriting)
        ... )
        UNKNOWN

    """
    svg_name = name.replace("_", "-")
    own = _property(element, name, scope)

    if _is_specified(own):
        return own

    if element is scope.boundary:
        return _unknown_unless_initial(svg_name, scope)

    for ancestor in _ancestors(element):
        value = _property(ancestor, name, scope)

        if _is_specified(value):
            # an animation of the ancestor's value changes what the element
            # inherits over time
            return UNKNOWN if svg_name in scope.animated else value

        if ancestor is scope.boundary:
            return _unknown_unless_initial(svg_name, scope)

    return initial


def _scale_inherited(
    element: object,
    name: str,
    factor: float,
    scope: Scope,
    /,
    *,
    initial: object = None,
) -> None:
    """Resize an inherited magnitude, spelling it out if it was inherited.

    A value that came from an ancestor has to be written onto the element
    that uses it, because the ancestor is shared with elements this
    transformation does not reach.
    """
    value = property_value(element, name, initial=initial, scope=scope)

    if isinstance(value, Length | list | int | float):
        setattr(element, name, _scaled(value, factor))


def _strokes_in_host_space(element: object, scope: Scope, /) -> bool:
    """Check whether the element's stroke ignores its coordinate system.

    `vector-effect: non-scaling-stroke` pins the stroke to the coordinate
    system of the nearest viewport, so folding a transformation into the
    geometry leaves the stroke exactly as it was.

    Returns:
        `True` if the stroke is not scaled with the element.

    """
    return (
        property_value(element, "vector_effect", scope=scope)
        == "non-scaling-stroke"
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
    if isinstance(element, StrokeDasharrayAttr) and isinstance(
        element.stroke_dasharray, list
    ):
        dashes = [_scaled(dash, by) for dash in element.stroke_dasharray]
        element.stroke_dasharray = cast("list[Length]", dashes)
    if isinstance(element, StrokeDashoffsetAttr):
        element.stroke_dashoffset = _scaled(  # type: ignore[reportAttributeAccessIssue]
            element.stroke_dashoffset, by
        )


def apply(
    element: object,
    matrix: Matrix,
    /,
    *,
    scope: Scope = WHOLE_DOCUMENT,
    inherited_resized: bool = False,
) -> None:
    """Fold a transformation into the element's geometry attributes.

    The caller is responsible for checking that the element can absorb the
    matrix; see `split` and `geometry_capability`.

    Args:
        element: The element to transform.
        matrix: The transformation to apply.
        scope: How far up the tree inheritance can be seen.
        inherited_resized: Whether the element inherits its magnitudes from
            a parent that absorbed the same matrix and resized them already,
            so that only the magnitudes it spells out itself are resized.

    """
    if is_box(element):
        _apply_box(element, matrix)
    elif isinstance(element, CxAttr | CyAttr):
        _apply_centre(element, matrix)

    if isinstance(element, X1Attr):
        _apply_end_points(element, matrix)

    if isinstance(element, PointsAttr) and element.points is not None:
        element.points = [matrix @ p for p in element.points]

    if isinstance(element, DAttr) and element.d is not None:
        element.d = matrix @ element.d

    if isinstance(element, XListOfCoordinatesAttr):
        _apply_text(element, matrix)

    _apply_magnitudes(
        element, matrix, scope, inherited_resized=inherited_resized
    )


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

_GLYPH_SPACING_ATTRS: Final = ("letter_spacing", "word_spacing", "kerning")
"""Properties that space out the glyphs of a text content element."""

_FONT_MAGNITUDES: Final = ("font_size", *_GLYPH_SPACING_ATTRS)
"""Properties that size the glyphs of a text content element."""

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


def stretches_content(preserve_aspect_ratio: object, /) -> bool:
    """Check whether a `preserveAspectRatio` lets content be distorted.

    A value of `none` stretches the content to the viewport instead of
    fitting it, which is what makes a non-uniform scaling of the viewport
    survive being folded into its attributes.

    Returns:
        `True` if the content is stretched to fill the viewport.

    Examples:
        >>> stretches_content("none")
        True
        >>> stretches_content("xMidYMid meet")
        False
        >>> stretches_content(None)
        False

    """
    align, *_ = str(preserve_aspect_ratio or "xMidYMid").split()

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
            and stretches_content(_get(element, "preserveAspectRatio"))
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
                UPRIGHT
                if stretches_content(_get(element, "preserveAspectRatio"))
                else UNIFORM_SCALING
            )

        return TRANSLATION

    return NOTHING


def has_own_geometry(element: object, /) -> bool:
    """Check whether the element has geometry of its own to fold a matrix into.

    A `g` does not: a transformation on it belongs entirely to its children.

    Returns:
        `True` if the element has geometry of its own.

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
        "x",
        "y",
        "cx",
        "cy",
        "r",
        "rx",
        "ry",
        "width",
        "height",
    }
)
"""Properties that decide the geometry and that reification cannot rewrite.

A magnitude declared in a style -- a stroke width, a font size -- is not
listed: it resolves to the string it was written as, which cannot be resized
and so holds the element to a move by itself.
"""

_SHORTHANDS: Final = {"font-size": ("font",)}
"""Shorthand properties that set a property reification reads."""


def style_capability(element: object, /) -> Capability:
    """Work out what the element's `style` attribute leaves reifiable.

    A declaration in a `style` attribute overrides the presentation attribute
    of the same name, and reification rewrites attributes. A geometric
    property declared there is out of reach, so the element keeps its
    transformation.

    Returns:
        What the element's `style` attribute leaves it able to absorb.

    """
    return (
        NOTHING
        if _STYLE_OPAQUE & style_declarations(element).keys()
        else AFFINE
    )


def stylesheet_declarations(css: str, /) -> Iterator[tuple[str, str]]:
    """Read the declarations of a stylesheet, whatever they are declared on.

    Yields:
        Pairs of a property name, in lower case, and the value it is given,
        stripped of whitespace and of any `!important`.

    Examples:
        >>> list(
        ...     stylesheet_declarations(".a { fill: red } .b{stroke:blue}")
        ... )
        [('fill', 'red'), ('stroke', 'blue')]

    """
    # a declaration is only interesting inside a block, which is after a
    # brace and before the closing one
    for block in css.split("{")[1:]:
        for declaration in block.split("}")[0].split(";"):
            name, separator, value = declaration.partition(":")

            if separator:
                yield (
                    name.strip().lower(),
                    value.replace("!important", "").strip(),
                )


def declared_properties(css: str, /) -> frozenset[str]:
    """List the properties a stylesheet declares, whatever it declares them on.

    Returns:
        The names of the properties, in lower case.

    Examples:
        >>> sorted(declared_properties(".a { fill: red; stroke: blue }"))
        ['fill', 'stroke']

    """
    return frozenset(name for name, _ in stylesheet_declarations(css))


_ATTRIBUTE_SELECTOR: Final = re.compile(r"\[\s*([\w:-]+)")


def stylesheet_capability(css: str, /) -> Capability:
    """Work out what a stylesheet leaves reifiable anywhere in the document.

    Which elements a selector picks out is not something reification can
    work out, so a rule mentioning a property it would have to rewrite costs
    that property everywhere. A selector that picks elements out by a
    geometric attribute would stop matching once that attribute is
    rewritten, so it costs everything.

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
        >>> stylesheet_capability('[transform="scale(2)"] {}') == NOTHING
        True

    """
    # a selector is everything before a brace that is not inside a block
    selectors = " ".join(
        part.rsplit("}", 1)[-1] for part in css.split("{")[:-1]
    )

    if GEOMETRIC_ATTR_NAMES & set(_ATTRIBUTE_SELECTOR.findall(selectors)):
        return NOTHING

    return NOTHING if _STYLE_OPAQUE & declared_properties(css) else AFFINE


def geometry_capability(
    element: object,
    /,
    *,
    scope: Scope = WHOLE_DOCUMENT,
    as_path: bool = False,
) -> Capability:
    """Determine what transformations an element's attributes can express.

    This combines what the element's class is able to describe with facts
    that only hold for this particular element: whether its lengths can be
    resolved to user units, whether it is stroked, and whether it has the
    attributes a given transformation would have to be written into.

    Args:
        element: The element to inspect.
        scope: How far up the tree inheritance can be seen.
        as_path: Whether to judge a basic shape as the `path` it can be
            converted into, whose geometry survives anything.

    Returns:
        The set of features the element can absorb.

    """
    structural = AFFINE if as_path else _structural_capability(element)
    capability = structural & style_capability(element)

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
        # an extent left out is a percentage of the viewport, or whatever
        # the content measures, which no number written here could resize
        capability &= TRANSLATION

    if isinstance(element, FontSizeScaled) and not _is_resizable(
        property_value(element, "font_size", scope=scope)
    ):
        # the glyphs are drawn at a size reification cannot resolve -- a
        # keyword, or whatever the renderer picks by default -- so the
        # element may be moved but not resized
        capability &= TRANSLATION

    if isinstance(element, FontSizeScaled) and not all(
        _is_spacing_scalable(property_value(element, name, scope=scope))
        for name in _GLYPH_SPACING_ATTRS
    ):
        # a spacing relative to the font or the viewport cannot be resized
        # by a factor reification knows
        capability &= TRANSLATION

    if isinstance(element, StrokeWidthScaled) and _is_stroked(
        element, scope
    ):
        capability &= SIMILARITY

        if (
            property_value(element, "vector_effect", scope=scope)
            is UNKNOWN
            or not _is_resizable(
                property_value(
                    element, "stroke_width", initial=Length(1), scope=scope
                )
            )
            or (
                _is_dashed(element, scope)
                and not all(
                    _is_scalable(
                        property_value(element, name, scope=scope)
                    )
                    for name in ("stroke_dasharray", "stroke_dashoffset")
                )
            )
        ):
            # the stroke is drawn at a width reification cannot resolve, or
            # may not be scaled with the shape at all, so the element may
            # be moved but not resized
            capability &= TRANSLATION

        if (
            isinstance(element, ImplicitlyOrientedShape)
            and not as_path
            and _is_dashed(element, scope)
        ):
            # the dash pattern starts at a corner the spec fixes, so moving
            # that corner somewhere else shifts the pattern; the path the
            # shape converts into spells its corners out in order
            capability &= UNIFORM_SCALING

    return capability


def _geometry_is_explicit(element: object, /) -> bool:
    """Check that none of the element's defining coordinates are left out."""
    if isinstance(element, X1Attr):
        names = ("x1", "y1", "x2", "y2")
    elif isinstance(element, CxAttr):
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


def _property(element: object, name: str, scope: Scope, /) -> object:
    """Read the element's own value of a property, as it is rendered.

    A `style` declaration beats the presentation attribute, and a stylesheet
    rule may beat both without saying on which elements, so a property a
    stylesheet declares is unknown unless the element's own `style` settles
    it.

    Returns:
        The value, `None` if the element does not specify one, or `UNKNOWN`.

    """
    svg_name = name.replace("_", "-")
    declarations = style_declarations(element)

    for declared in (svg_name, *_SHORTHANDS.get(svg_name, ())):
        if declared in declarations:
            # a shorthand such as `font` sets the property to something
            # reification does not read out of it
            return (
                declarations[declared] if declared == svg_name else UNKNOWN
            )

        if declared in scope.styled:
            return UNKNOWN

    return _get(element, name)


def _is_stroked(element: object, scope: Scope, /) -> bool:
    """Check whether the element is stroked, or might be."""
    if _strokes_in_host_space(element, scope):
        # the stroke ignores the coordinate system, so it constrains nothing
        return False

    stroke = property_value(element, "stroke", scope=scope)

    return stroke is not None and stroke != "none"


def _is_dashed(element: object, scope: Scope, /) -> bool:
    """Check whether the element's stroke is dashed, or might be."""
    dasharray = property_value(element, "stroke_dasharray", scope=scope)

    match dasharray:
        case None | "none" | []:
            return False
        case _:
            return True


GEOMETRIC_ATTR_NAMES: Final[frozenset[AttributeName]] = frozenset(
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

    Returns:
        `True` if the element carries geometry the library did not parse.

    """
    extra = getattr(element, "extra_attrs", None)

    if extra is None:
        return False

    return bool(GEOMETRIC_ATTR_NAMES & extra().keys())


# endregion
