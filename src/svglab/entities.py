"""Abstract base classes for representing common XML entities."""

from __future__ import annotations

import abc
import collections
import itertools
import reprlib
import sys
import warnings
from collections.abc import Generator, Mapping

import bs4
import pydantic
from typing_extensions import (
    ClassVar,
    Final,
    Literal,
    Self,
    SupportsIndex,
    TypeVar,
    cast,
    final,
    overload,
    override,
)

from svglab.attrparse.iri import FuncIri, Iri
from svglab.attrparse.length import Length
from svglab.attrparse.transform import (
    Reifiable,
    Rotate,
    Scale,
    SkewX,
    SkewY,
    Transform,
    TransformFunction,
    Translate,
    decompose_matrices,
)
from svglab.attrs.attrdefs import (
    CxAttr,
    CyAttr,
    DAttr,
    DxListOfLengthsAttr,
    DyListOfLengthsAttr,
    FontSizeAttr,
    FxAttr,
    FyAttr,
    GradientUnitsAttr,
    HeightAttr,
    OffsetNumberPercentageAttr,
    PathLengthAttr,
    PatternUnitsAttr,
    PointsAttr,
    RAttr,
    RxAttr,
    RyAttr,
    StrokeDasharrayAttr,
    StrokeDashoffsetAttr,
    StrokeWidthAttr,
    TextLengthAttr,
    VectorEffectAttr,
    WidthAttr,
    X1Attr,
    X2Attr,
    XCoordinateAttr,
    XListOfCoordinatesAttr,
    XNumberAttr,
    Y1Attr,
    Y2Attr,
    YCoordinateAttr,
    YListOfCoordinatesAttr,
    YNumberAttr,
)
from svglab.attrs.attrgroups import CoreAttrs, PresentationAttrs
from svglab.attrs.names import ATTR_NAME_TO_NORMALIZED, AttributeName
from svglab.constants import SVG_XMLNS
from svglab.elements.names import ELEMENT_NAME_TO_NORMALIZED, ElementName
from svglab.errors import (
    SvgElementNotFoundError,
    SvgTransformOriginError,
    SvgTransformSwapError,
)
from svglab.models import BaseModel
from svglab.serialize import (
    Formatter,
    get_current_formatter,
    serialize_attr,
)
from svglab.utils.bsutils import beautifulsoup_to_str
from svglab.utils.iterutils import search_by_reference, take_last
from svglab.utils.mathutils import arctan, is_close, tan
from svglab.utils.miscutils import basic_compare


_T = TypeVar("_T")
_ElementT = TypeVar("_ElementT", bound="Element")
_TransformT1 = TypeVar("_TransformT1", bound=TransformFunction)
_TransformT2 = TypeVar("_TransformT2", bound=TransformFunction)

_EMPTY_PARAM: Final = object()
"""A sentinel value for an empty parameter."""

_REFERENCE_ATTR_NAMES: Final[tuple[AttributeName, ...]] = (
    "xlink:href",
    "href",
    "fill",
    "stroke",
    "mask",
    "clip-path",
)
"""Attributes that may hold an IRI reference to another element."""


class StrokeWidthScaled:
    """The element's `stroke-width` attribute should be scaled."""


def _match_element(
    element: Element, /, *, search: type[Element] | ElementName | str
) -> bool:
    """Check if an element matches the given search criteria.

    Args:
        element: The element to check.
        search: The search criteria. Can be an element name or an element
            class.

    Returns:
        `True` if the element matches the search criteria, `False` otherwise.

    Examples:
        >>> from svglab import Rect
        >>> rect = Rect()
        >>> _match_element(rect, search="rect")
        True
        >>> _match_element(rect, search=Rect)
        True
        >>> _match_element(rect, search="circle")
        False

    """
    if isinstance(search, type):
        return isinstance(element, search)

    return element_name(element) == search


def _scale_attr(attr: _T, /, by: float) -> _T:
    """Scale an attribute by the given factor.

    This is a helper function for scaling attributes. If the attribute is a
    number or a non-percentage length, it is scaled by the given factor.
    Otherwise, the attribute is left unchanged. If the attribute is a list or
    tuple, the function is applied recursively to each element.

    Args:
        attr: The attribute to scale.
        by: The factor by which to scale the attribute.

    Returns:
        The scaled attribute.

    Examples:
        >>> from svglab import Length
        >>> _scale_attr(Length(10), 2)
        Length(value=20.0, unit=None)
        >>> _scale_attr(None, 2) is None
        True
        >>> _scale_attr(Length(10, "%"), 2)
        Length(value=10.0, unit='%')

    """
    match attr:
        case Length(_, "%"):
            return attr
        case int() | float() | Length():
            return cast(_T, attr * by)
        case list() | tuple():
            items = cast(list[object] | tuple[object, ...], attr)
            return cast(
                _T, type(items)(_scale_attr(item, by) for item in items)
            )
        case _:
            return attr


def _inherited_stroke_width(element: StrokeWidthAttr, /) -> Length:
    """Resolve the `stroke-width` that the element inherits.

    `stroke-width` is an inherited property. An element that does not
    specify its own `stroke-width` uses the value of the nearest ancestor
    that specifies one. If no ancestor specifies one, the initial value
    (`1`) is used.

    Args:
        element: The element whose inherited `stroke-width` to resolve.

    Returns:
        The inherited `stroke-width`.

    Examples:
        >>> from svglab import G, Length, Path
        >>> path = Path()
        >>> g = G(stroke_width=Length(5)).add_child(path)
        >>> _inherited_stroke_width(path)
        Length(value=5.0, unit=None)
        >>> nested = Path()
        >>> g = G(stroke_width=Length(5)).add_child(
        ...     G(stroke_width=Length(3)).add_child(nested)
        ... )
        >>> _inherited_stroke_width(nested)
        Length(value=3.0, unit=None)
        >>> _inherited_stroke_width(Path())
        Length(value=1.0, unit=None)

    """
    if isinstance(element, Element):
        for ancestor in element.ancestors:
            stroke_width = ancestor.stroke_width

            if stroke_width is not None and stroke_width != "inherit":
                return stroke_width

    return Length(1)


def _scale_stroke_width(element: StrokeWidthAttr, by: float) -> None:
    if (
        isinstance(element, VectorEffectAttr)
        and element.vector_effect == "non-scaling-stroke"
    ):
        return

    # only elements that actually stroke something scale their stroke-width.
    # on a container, the transformation is pushed down to the children, each
    # of which scales its own (possibly inherited) stroke-width, so scaling
    # the container's value as well would apply the factor twice
    if not isinstance(element, StrokeWidthScaled):
        return

    sw_set = element.stroke_width is not None
    inherited = None if sw_set else _inherited_stroke_width(element)

    if inherited is not None:
        element.stroke_width = inherited

    element.stroke_width = _scale_attr(element.stroke_width, by)

    # if stroke-width was not set and the scaled value is equal to the value
    # the element inherits anyway, remove the attribute
    if (
        isinstance(inherited, Length)
        and isinstance(element.stroke_width, Length)
        and element.stroke_width.unit == inherited.unit
        and is_close(float(element.stroke_width), float(inherited))
    ):
        element.stroke_width = None


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
        element.stroke_dasharray = [
            _scale_attr(dash, by) for dash in element.stroke_dasharray
        ]
    if isinstance(element, StrokeDashoffsetAttr):
        element.stroke_dashoffset = _scale_attr(
            element.stroke_dashoffset, by
        )


def _scale(element: object, scale: Scale) -> None:  # noqa: PLR0915
    if not is_close(scale.sx, scale.sy):
        raise ValueError("Non-uniform scaling is not supported.")

    factor = scale.sx

    if is_close(factor, 1):
        return

    if isinstance(element, WidthAttr):
        element.width = _scale_attr(element.width, factor)
    if isinstance(element, HeightAttr):
        element.height = _scale_attr(element.height, factor)
    if isinstance(element, RAttr):
        element.r = _scale_attr(element.r, factor)
    if isinstance(element, X1Attr):
        element.x1 = _scale_attr(element.x1, factor)
    if isinstance(element, Y1Attr):
        element.y1 = _scale_attr(element.y1, factor)
    if isinstance(element, X2Attr):
        element.x2 = _scale_attr(element.x2, factor)
    if isinstance(element, Y2Attr):
        element.y2 = _scale_attr(element.y2, factor)
    if isinstance(element, RxAttr):
        element.rx = _scale_attr(element.rx, factor)
    if isinstance(element, RyAttr):
        element.ry = _scale_attr(element.ry, factor)
    if isinstance(element, CxAttr):
        element.cx = _scale_attr(element.cx, factor)
    if isinstance(element, CyAttr):
        element.cy = _scale_attr(element.cy, factor)
    if isinstance(element, FxAttr):
        element.fx = _scale_attr(element.fx, factor)
    if isinstance(element, FyAttr):
        element.fy = _scale_attr(element.fy, factor)
    if isinstance(element, FontSizeAttr):
        element.font_size = _scale_attr(element.font_size, factor)
    if isinstance(element, DxListOfLengthsAttr):
        element.dx = _scale_attr(element.dx, factor)
    if isinstance(element, DyListOfLengthsAttr):
        element.dy = _scale_attr(element.dy, factor)
    if isinstance(element, TextLengthAttr):
        element.textLength = _scale_attr(element.textLength, factor)
    if isinstance(element, PointsAttr) and element.points is not None:
        element.points = [scale @ point for point in element.points]
    if isinstance(element, DAttr) and element.d is not None:
        element.d = scale @ element.d

    # these assignments have to be mutually exclusive, because the
    # type checker doesn't know that x being a <number> implies that x is
    # not a <coordinate> and vice versa
    if isinstance(element, XNumberAttr):  # noqa: SIM114
        element.x = _scale_attr(element.x, factor)
    elif isinstance(element, XCoordinateAttr):  # noqa: SIM114
        element.x = _scale_attr(element.x, factor)
    elif isinstance(element, XListOfCoordinatesAttr):
        element.x = _scale_attr(element.x, factor)

    if isinstance(element, YNumberAttr):  # noqa: SIM114
        element.y = _scale_attr(element.y, factor)
    elif isinstance(element, YCoordinateAttr):  # noqa: SIM114
        element.y = _scale_attr(element.y, factor)
    elif isinstance(element, YListOfCoordinatesAttr):
        element.y = _scale_attr(element.y, factor)

    if isinstance(element, StrokeWidthAttr):
        _scale_stroke_width(element, factor)

    # no need to scale distance-along-a-path attributes if a custom path
    # length is provided because those attributes and pathLength are
    # proportional
    if (
        not isinstance(element, PathLengthAttr)
        or element.pathLength is None
    ):
        scale_distance_along_a_path_attrs(element, factor)

    if isinstance(element, OffsetNumberPercentageAttr):
        element.offset = _scale_attr(element.offset, factor)


def _translate_attr(attr: _T, /, by: float) -> _T:
    """Translate an attribute by the given amount.

    This is a helper function for translating attributes. If the attribute is
    a number or a non-percentage length, it is translated by the given amount.
    Otherwise, the attribute is left unchanged. If the attribute is a list or
    tuple, the function is applied recursively to each element.

    Args:
        attr: The attribute to translate.
        by: The amount by which to translate the attribute.

    Returns:
        The translated attribute.

    Examples:
        >>> from svglab import Length
        >>> _translate_attr(Length(10), 5)
        Length(value=15.0, unit=None)
        >>> _translate_attr(None, 5) is None
        True
        >>> _translate_attr(Length(10, "%"), 5)
        Length(value=10.0, unit='%')

    """
    match attr:
        case Length(_, "%"):
            return attr
        case int() | float():
            return cast(_T, attr + by)
        case Length():
            return attr + Length(by)
        case list() | tuple():
            items = cast(list[object] | tuple[object, ...], attr)
            return cast(
                _T,
                type(items)(_translate_attr(item, by) for item in items),
            )
        case _:
            return attr


# pyright goes nuts if `element` is annotated as `Element`... seems like a bug
# luckily we don't really care
def _translate(element: object, translate: Translate) -> None:
    tx, ty = translate.tx, translate.ty

    if is_close(tx, 0) and is_close(ty, 0):
        return

    zero = Length.zero()

    # these attributes are mandatory for the respective elements
    if isinstance(element, X1Attr):
        element.x1 = _translate_attr(element.x1, tx)
    if isinstance(element, Y1Attr):
        element.y1 = _translate_attr(element.y1, ty)
    if isinstance(element, X2Attr):
        element.x2 = _translate_attr(element.x2, tx)
    if isinstance(element, Y2Attr):
        element.y2 = _translate_attr(element.y2, ty)

    # but these are not, so if they are not present, we initialize them
    # to 0
    if isinstance(element, CxAttr):
        element.cx = _translate_attr(element.cx or zero, tx)
    if isinstance(element, CyAttr):
        element.cy = _translate_attr(element.cy or zero, ty)

    # an unset focal point follows the already translated center
    if isinstance(element, FxAttr):
        element.fx = _translate_attr(element.fx, tx)
    if isinstance(element, FyAttr):
        element.fy = _translate_attr(element.fy, ty)

    if isinstance(element, XNumberAttr):
        element.x = _translate_attr(element.x or 0, tx)
    elif isinstance(element, XCoordinateAttr):
        element.x = _translate_attr(element.x or zero, tx)
    elif isinstance(element, XListOfCoordinatesAttr):
        element.x = _translate_attr(element.x, tx)

    if isinstance(element, YNumberAttr):
        element.y = _translate_attr(element.y or 0, ty)
    elif isinstance(element, YCoordinateAttr):
        element.y = _translate_attr(element.y or zero, ty)
    elif isinstance(element, YListOfCoordinatesAttr):
        element.y = _translate_attr(element.y, ty)

    if isinstance(element, PointsAttr) and element.points is not None:
        element.points = [translate @ point for point in element.points]

    if isinstance(element, DAttr) and element.d is not None:
        element.d = translate @ element.d

    if isinstance(element, OffsetNumberPercentageAttr):
        element.offset = _translate_attr(element.offset, tx)


def swap_transforms(
    a: _TransformT1, b: _TransformT2, /
) -> tuple[_TransformT2, _TransformT1]:
    """Swap transforms, adjusting parameters so that the result is equal.

    Args:
        a: The first transform.
        b: The second transform.

    Returns:
        A 2-tuple (b', a') where b' and a' are the adjusted transforms.

    Raises:
        SvgTransformSwapError: If the transforms cannot be swapped.

    Examples:
        >>> from svglab.attrparse.transform import Scale, Translate, SkewX
        >>> swap_transforms(Translate(10, 20), Scale(2, 3))
        (Scale(sx=2.0, sy=3.0), Translate(tx=5.0, ty=6.666666666666667))
        >>> swap_transforms(Scale(2, 3), SkewX(45))
        (SkewX(angle=33.690067525979785), Scale(sx=2.0, sy=3.0))
        >>> swap_transforms(SkewX(45), Translate(10, 20))
        (Translate(tx=30.0, ty=20.0), SkewX(angle=45.0))

    """
    match a, b:
        # transformations of the same type
        case (Translate(), Translate()) | (Scale(), Scale()):
            return b, a

        # translate <-> scale
        case Translate(tx, ty), Scale(sx, sy) as scale:
            return scale, type(a)(tx / sx, ty / sy)

        case Scale(sx, sy) as scale, Translate(tx, ty):
            return type(b)(sx * tx, sy * ty), scale

        # translate <-> rotate
        case Rotate(angle, cx, cy), Translate(tx, ty):
            return type(b)(tx, ty), type(a)(angle, cx - tx, cy - ty)
        case Translate(tx, ty), Rotate(angle, cx, cy):
            return type(b)(angle, cx + tx, cy + ty), type(a)(tx, ty)

        # scale <-> rotate
        case Rotate(angle, cx, cy), Scale(sx, sy) as scale:
            return scale, type(a)(angle, cx / sx, cy / sy)
        case Scale(sx, sy) as scale, Rotate(angle, cx, cy):
            return type(b)(angle, cx * sx, cy * sy), scale

        # translate <-> skew
        case SkewX(angle) as skew_x, Translate(tx, ty):
            return type(b)(tx + ty * tan(angle), ty), skew_x

        case Translate(tx, ty), SkewX(angle) as skew_x:
            return skew_x, type(a)(tx - ty * tan(angle), ty)

        case SkewY(angle) as skew_y, Translate(tx, ty):
            return type(b)(tx, ty + tx * tan(angle)), skew_y

        case Translate(tx, ty), SkewY(angle) as skew_y:
            return skew_y, type(a)(tx, ty - tx * tan(angle))

        # scale <-> skew
        case Scale(sx, sy) as scale, SkewX(angle):
            if is_close(sx, sy):
                return b, a

            angle = arctan(sx / sy * tan(angle))
            return type(b)(angle), scale

        case SkewX(angle), Scale(sx, sy) as scale:
            if is_close(sx, sy):
                return b, a

            angle = arctan(sy / sx * tan(angle))
            return scale, type(a)(angle)

        case Scale(sx, sy) as scale, SkewY(angle):
            if is_close(sx, sy):
                return b, a

            angle = arctan(sy / sx * tan(angle))
            return type(b)(angle), scale

        case SkewY(angle), Scale(sx, sy) as scale:
            if is_close(sx, sy):
                return b, a

            angle = arctan(sx / sy * tan(angle))

            return scale, type(a)(angle)
        case _:
            raise SvgTransformSwapError(a, b)


def _move_transformation_to_end(
    transformations: Transform, index: int
) -> None:
    """Move a transformation to the end of the transform list.

    This function moves a transformation from the given index to the end of
    the list, swapping it with each transformation that follows it.
    The transformations in the list are adjusted so that the result is the
    same. The transformation itself may have its parameters adjusted as well.

    Args:
        transformations: A list of transformations.
        index: The index of the transformation to move.

    Raises:
        ValueError: If the index is out of range.
        SvgTransformSwapError: If two transformations cannot be swapped.

    Examples:
        >>> from svglab.attrparse.transform import Translate, Scale
        >>> transform = [Translate(10, 20), Scale(2, 3)]
        >>> _move_transformation_to_end(transform, 0)
        >>> transform
        [Scale(sx=2.0, sy=3.0), Translate(tx=5.0, ty=6.666666666666667)]

    """
    if not (0 <= index < len(transformations)):
        msg = f"Index {index=} out of range"
        raise ValueError(msg)

    for i in range(index, len(transformations) - 1):
        transformations[i], transformations[i + 1] = swap_transforms(
            transformations[i], transformations[i + 1]
        )


def element_name(element: Element, /) -> str:
    """Get the SVG element name of the given element.

    Args:
        element: The element.

    Returns:
        The SVG element name.

    Examples:
        >>> from svglab import Rect
        >>> element_name(Rect())
        'rect'

    """
    if isinstance(element, UnknownElement):
        return element.element_name

    return ELEMENT_NAME_TO_NORMALIZED.inverse[type(element).__name__]


class Entity(BaseModel, metaclass=abc.ABCMeta):
    """The base class of the SVG element hierarchy."""

    parent: Element | None = pydantic.Field(default=None, init=False)

    def to_xml(
        self, *, pretty: bool = True, formatter: Formatter | None = None
    ) -> str:
        """Convert the element to XML.

        Args:
            pretty: Whether to produce pretty-printed XML.
            formatter: The formatter to use for serialization.

        Returns:
            The XML representation of the element.

        Examples:
            >>> from svglab import Rect, Length
            >>> rect = Rect(id="foo", stroke_linecap="round")
            >>> rect.to_xml()
            '<rect id="foo" stroke-linecap="round"/>'

        """
        with formatter or get_current_formatter():
            soup = self.to_beautifulsoup_object()
            return beautifulsoup_to_str(soup, pretty=pretty)

    @abc.abstractmethod
    def to_beautifulsoup_object(self) -> bs4.PageElement:
        """Convert the element to a corresponding `BeautifulSoup` object."""

    @abc.abstractmethod
    def _eq(self, other: Entity, /) -> bool: ...

    @abc.abstractmethod
    def _hash(self) -> int: ...

    @property
    def ancestors(self) -> Generator[Element]:
        """Iterate over the ancestors of the element.

        The ancestors are the element's parent, grandparent, and so on, up to
        the root ancestor. The root ancestor is the first ancestor that has no
        parent.

        The ancestors are returned in the order from the closest ancestor
        to the root ancestor.

        Yields:
            The ancestors of the element.

        """
        curr = self.parent

        while curr is not None:
            yield curr
            curr = curr.parent

    @override
    def __eq__(self, other: object) -> bool:
        if not basic_compare(other, self=self):
            return False

        return self._eq(other)

    @override
    def __hash__(self) -> int:
        return self._hash()

    # an attribute set to `None` or deleted is no longer set, so it must not
    # linger in `model_fields_set` either
    @override
    def __setattr__(self, name: str, value: object) -> None:
        super().__setattr__(name, value)

        if value is None:
            self.__pydantic_fields_set__.discard(name)

    @override
    def __delattr__(self, name: str) -> None:
        if name in type(self).model_fields:
            setattr(self, name, None)
            return

        super().__delattr__(name)
        self.__pydantic_fields_set__.discard(name)


class Element(Entity, CoreAttrs, PresentationAttrs, metaclass=abc.ABCMeta):
    """An element.

    An element is an entity that has a name, a set of attributes,
    and (optionally) one or more elements as children.

    Elements can have standard attributes (for example, `id`, `class`,
    `color`) and non-standard user-defined attributes.

    Example: `<rect id="foo" class="bar" color="red" />`
    """

    model_config: ClassVar[pydantic.ConfigDict] = pydantic.ConfigDict(
        extra="allow",
        alias_generator=pydantic.AliasGenerator(
            validation_alias=lambda name: pydantic.AliasChoices(
                name, ATTR_NAME_TO_NORMALIZED.inverse.get(name, name)
            ),
            serialization_alias=(
                lambda name: ATTR_NAME_TO_NORMALIZED.inverse.get(
                    name, name
                )
            ),
        ),
    )

    prefix: str | None = None

    # a lambda is faster with pydantic than `list`
    _children: list[Entity] = pydantic.PrivateAttr(
        default_factory=lambda: []  # noqa: PIE807
    )

    @property
    def __children(self) -> list[Entity]:
        # `BaseModel.__getattr__` is an order of magnitude slower than reading
        # the private attribute from its storage
        assert self.__pydantic_private__ is not None, "private attrs unset"
        return self.__pydantic_private__["_children"]

    # region Attribute Handling

    @pydantic.model_validator(mode="after")
    def __validate_extra(self) -> Element:
        # model_extra cannot be None because extra is set to "allow"
        assert self.model_extra is not None, "model_extra is None"

        for key, value in self.model_extra.items():
            if not isinstance(value, str):
                msg = (
                    f"Non-standard attribute {key!r} must be of type str,"
                    f" got {type(value)}"
                )
                raise TypeError(msg)

        return self

    def extra_attrs(self) -> Mapping[str, str]:
        """Get the extra attributes of the element.

        Extra attributes are user-defined attributes that are not part of the
        SVG standard.

        Returns:
            A mapping of extra attribute names to their values. The mapping
            should be considered immutable.

        """
        assert self.model_extra is not None, "model_extra is None"
        return self.model_extra

    def standard_attrs(self) -> Mapping[AttributeName, object]:
        """Get the standard attributes of the element.

        Standard attributes are attributes that are part of the SVG standard.

        Returns:
            A mapping of standard attribute names to their values. The mapping
            should be considered immutable.

        """
        # `model_dump()` would walk the ancestor chain via `parent`
        extra = self.model_extra or {}
        fields = type(self).model_fields
        normalized = ATTR_NAME_TO_NORMALIZED
        result: dict[AttributeName, object] = {}

        # only fields that were set can hold a non-`None` value
        for name in sorted(self.__pydantic_fields_set__):
            if name in extra or name not in fields:
                continue

            attr = normalized.inverse.get(name, name)

            if attr not in normalized:
                continue

            # the attribute may have been deleted
            value = getattr(self, name, None)

            if value is not None:
                result[cast(AttributeName, attr)] = value

        return result

    def all_attrs(self) -> Mapping[str, object]:
        """Get all attributes of the element.

        This includes both standard and extra attributes.

        Returns:
            A mapping of attribute names to their values. The mapping should
            be considered immutable.

        """
        standard = cast(Mapping[str, object], self.standard_attrs())
        extra = self.extra_attrs()

        return {**standard, **extra}

    def __get_attr_or_default(self, attr_name: AttributeName) -> object:
        name = ATTR_NAME_TO_NORMALIZED[attr_name]

        if name in type(self).model_fields:
            value = getattr(self, name, None)

            if value is not None:
                return value

        match attr_name:
            case "gradientUnits" | "patternUnits":
                return "objectBoundingBox"
            case "patternContentUnits":
                return "userSpaceOnUse"
            case _:
                return None

    def __getitem__(self, key: str) -> str:
        assert self.model_extra is not None, "model_extra is None"
        value: str = self.model_extra[key]
        return value

    def __setitem__(self, key: str, value: str) -> None:
        assert self.model_extra is not None, "model_extra is None"
        self.model_extra[key] = value

    def __delitem__(self, key: str) -> None:
        assert self.model_extra is not None, "model_extra is None"
        del self.model_extra[key]

    # endregion
    # region Equality and Representation

    @override
    def _eq(self, other: Entity) -> bool:
        return (
            isinstance(other, Element)
            and element_name(self) == element_name(other)
            and self.prefix == other.prefix
            and self.all_attrs() == other.all_attrs()
            and self.num_children == other.num_children
            and all(
                c1 == c2
                for c1, c2 in zip(
                    self.children, other.children, strict=True
                )
            )
        )

    @override
    def _hash(self) -> int:
        return hash(
            (
                type(self),
                self.prefix,
                frozenset(self.all_attrs().items()),
                tuple(hash(child) for child in self.children),
            )
        )

    @reprlib.recursive_repr()
    @override
    def __repr__(self) -> str:
        name = type(self).__name__
        attrs = dict(self.all_attrs())

        if self.__children:
            attrs["children"] = list(self.children)

        if self.prefix:
            attrs["prefix"] = self.prefix

        if isinstance(self, UnknownElement):
            attrs["element_name"] = self.element_name

        attr_repr = ", ".join(
            f"{key}={value!r}" for key, value in attrs.items()
        )

        return f"{name}({attr_repr})"

    # endregion
    # region Tree Access and Traversal

    @property
    def children(self) -> Generator[Entity]:
        """Iterate over the children of the element.

        The children are returned in the order they were added to the
        element.

        Yields:
            The children of the element.

        """
        yield from self.__children

    @property
    def num_children(self) -> int:
        """The number of children of the element."""
        return len(self.__children)

    def has_children(self) -> bool:
        """Check if the element has any children.

        Returns:
            `True` if the element has children, `False` otherwise.

        """
        return self.num_children > 0

    @property
    def descendants(self) -> Generator[Entity]:
        """Iterate over the descendants of the element.

        The descendants of the element are the children and their children,
        and so on. The descendants are returned in document order (the order
        of their start tags in the markup: an element before its descendants,
        siblings in the order written).

        Yields:
            The descendants of the element.

        """
        queue = collections.deque(self.children)

        while queue:
            child = queue.popleft()
            yield child

            if isinstance(child, Element):
                queue.extendleft(reversed(list(child.children)))

    @property
    def next_siblings(self) -> Generator[Entity]:
        """Iterate over the next siblings of the element.

        The next siblings are the siblings that come after the element in
        the parent's children list.

        Yields:
            The next siblings of the element.

        """
        if self.parent is None:
            return

        siblings = iter(self.parent.children)

        for sibling in siblings:
            if sibling is self:
                yield from siblings
                return

    @property
    def prev_siblings(self) -> Generator[Entity]:
        """Iterate over the previous siblings of the element.

        The previous siblings are the siblings that come before the element
        in the parent's children list.

        Yields:
            The previous siblings of the element.

        """
        if self.parent is None:
            return

        yield from itertools.takewhile(
            lambda sibling: sibling is not self, self.parent.children
        )

    @property
    def siblings(self) -> Generator[Entity]:
        """Iterate over the siblings of the element.

        The siblings are the children of the element's parent, excluding
        the element itself.

        If you wish to include the element itself, use `self.parent.children`

        Yields:
            The siblings of the element.

        """
        yield from self.prev_siblings
        yield from self.next_siblings

    def get_root(self) -> Element:
        """Get the top-level ancestor of the element.

        The root ancestor is the first ancestor that has no parent. If the
        element has no parent, it is considered the root ancestor.

        Returns:
            The root ancestor of the element.

        """
        return take_last(self.ancestors) or self

    # endregion
    # region Tree Mutation

    def add_child(
        self, child: Entity, /, *, index: int | None = None
    ) -> Self:
        """Add a child to the element.

        Args:
            child: The child to add.
            index: The index at which to add the child. If `None`, the child
                is added at the end of the children list.

        Returns:
            The element itself.

        Raises:
            ValueError: If the child is the same as the element itself or
                its ancestor, or if the child already has a parent.

        """
        if child is self:
            raise ValueError("Cannot add an element as a child of itself.")

        if child.parent is not None:
            raise ValueError(
                "Cannot add a child that already has a parent."
            )

        # only an element with children can be an ancestor of this one
        if (
            isinstance(child, Element)
            and child.has_children()
            and self.get_root() is child
        ):
            raise ValueError("Cannot add an ancestor as a child.")

        if index is None:
            self.__children.append(child)
        else:
            self.__children.insert(index, child)

        # the parent is always valid, so skip pydantic's slow validation
        object.__setattr__(child, "parent", self)

        return self

    def add_children(self, *children: Entity) -> Self:
        """Add multiple children to the element.

        Args:
            children: The children to add.

        Returns:
            The element itself.

        Raises:
            ValueError: If any child is the same as the element itself or
                if any child already has a parent.

        """
        for child in children:
            self.add_child(child)

        return self

    def remove_child(self, child: Entity, /) -> Entity:
        """Remove a child from the element.

        The child is compared with the children of the element based on
        identity (reference), not equality. This means that the child must be
        the same object as the one that was added to the element.

        Args:
            child: The child to remove.

        Returns:
            The removed child.

        Raises:
            ValueError: If the child is not a child of the element.

        """
        try:
            index = search_by_reference(self.__children, child)
        except ValueError as e:
            raise ValueError("Child not found") from e

        return self.pop_child(index)

    def pop_child(self, index: SupportsIndex = -1, /) -> Entity:
        """Remove a child from the element based on its index.

        Args:
            index: The index of the child to remove. If unspecified, the last
                child is removed.

        Returns:
            The removed child.

        Raises:
            IndexError: If the index is out of range.

        """
        child = self.__children.pop(index)
        object.__setattr__(child, "parent", None)

        return child

    def clear_children(self) -> None:
        """Remove all children from the element."""
        for child in self.__children:
            object.__setattr__(child, "parent", None)

        self.__children.clear()

    def get_child(self, index: SupportsIndex = -1, /) -> Entity:
        """Get a child of the element based on its index.

        Args:
            index: The index of the child to get. If unspecified, the last
                child is returned.

        Returns:
            The child at the specified index.

        Raises:
            IndexError: If the index is out of range.

        """
        return self.__children[index]

    def get_child_index(
        self,
        child: Entity,
        /,
        start: SupportsIndex = 0,
        stop: SupportsIndex = sys.maxsize,
    ) -> int:
        """Get the index of a child in the element's children list.

        The child is compared with the children of the element based on
        identity (reference), not equality. This means that the child must be
        the same object as the one that was added to the element.

        Args:
            child: The child to find.
            start: The starting index for the search. Defaults to 0.
            stop: The ending index for the search. Defaults to the end of the
                list.

        Returns:
            The index of the child in the children list.

        Raises:
            ValueError: If the child is not found in the list.

        """
        for i in range(*slice(start, stop).indices(len(self.__children))):
            if self.__children[i] is child:
                return i

        msg = f"Item not found in sequence: {child!r}"
        raise ValueError(msg)

    # endregion
    # region Search and References

    @overload
    def find_all(
        self, /, *, recursive: bool = True
    ) -> Generator[Element]: ...

    @overload
    def find_all(
        self, *elements: type[_ElementT], recursive: bool = True
    ) -> Generator[_ElementT]: ...

    @overload
    def find_all(
        self,
        *elements: type[Element] | ElementName | str,
        recursive: bool = True,
    ) -> Generator[Element]: ...

    def find_all(
        self,
        *elements: type[Element] | ElementName | str,
        recursive: bool = True,
    ) -> Generator[Element]:
        """Find all elements that match the given search criteria.

        Args:
            elements: The elements to search for. Can be element names or
                element classes.  If no search criteria are provided, all
                elements are returned.
            recursive: If `False`, only search the direct children of the
                element, otherwise search all descendants.

        Yields:
            The elements that match the search criteria.

        Examples:
            >>> from svglab import G, Rect
            >>> g = G().add_children(Rect(), G().add_child(Rect()))
            >>> list(g.find_all("rect"))
            [Rect(), Rect()]
            >>> list(g.find_all(G))
            [G(children=[Rect()])]
            >>> list(g.find_all(Rect, recursive=False))
            [Rect()]
            >>> list(g.find_all(G, "rect"))
            [Rect(), G(children=[Rect()]), Rect()]

        """
        for child in self.descendants if recursive else self.children:
            if isinstance(child, Element) and (
                not elements
                or any(
                    _match_element(child, search=element)
                    for element in elements
                )
            ):
                yield child

    @overload
    def find(
        self, *elements: type[_ElementT], recursive: bool = True
    ) -> _ElementT: ...

    @overload
    def find(
        self,
        *elements: type[Element] | ElementName | str,
        recursive: bool = True,
    ) -> Element: ...

    @overload
    def find(
        self,
        *elements: type[_ElementT],
        recursive: bool = True,
        default: _T = _EMPTY_PARAM,
    ) -> _ElementT | _T: ...

    @overload
    def find(
        self,
        *elements: type[Element] | ElementName | str,
        recursive: bool = True,
        default: _T = _EMPTY_PARAM,
    ) -> Element | _T: ...

    def find(
        self,
        *elements: type[Element] | ElementName | str,
        recursive: bool = True,
        default: _T = _EMPTY_PARAM,
    ) -> Element | _T:
        """Find the first element that matches the given search criteria.

        Args:
            elements: The elements to search for. Can be element names or
                element classes.
            recursive: If `False`, only search the direct children of the
                element, otherwise search all descendants.
            default: The default value to return if no element matches the
                search criteria.

        Returns:
            The first element that matches the search criteria.

        Raises:
            SvgElementNotFoundError: If no element matches the search criteria
                and no default value is provided.

        Examples:
            >>> from svglab import G, Rect
            >>> g = G().add_children(
            ...     Rect(id="foo"), G().add_child(Rect(id="bar"))
            ... )
            >>> g.find("rect")
            Rect(id='foo')
            >>> g.find(G)
            G(children=[Rect(id='bar')])
            >>> g.find("circle", default=None) is None
            True

        """
        try:
            return next(self.find_all(*elements, recursive=recursive))
        except StopIteration as e:
            if default is not _EMPTY_PARAM:
                return default

            msg = f"Unable to find element by search criteria: {elements}"
            raise SvgElementNotFoundError(msg) from e

    def resolve_iri(self, iri_: Iri, /) -> Element:
        """Resolve a local IRI reference to an element in the document.

        This method attempts to resolve an IRI reference to an element in the
        descendants of this element. The IRI reference must be local.

        Args:
            iri_: The IRI reference to resolve. Must be local.

        Returns:
            The element that the IRI reference points to.

        Raises:
            ValueError: If the IRI reference is not local or if the element
                cannot be found in the document.

        """
        if not iri_.is_local:
            raise ValueError(
                "Unable to resolve a non-local IRI reference in this document."
            )

        try:
            return next(
                tag for tag in self.find_all() if tag.id == iri_.fragment
            )
        except StopIteration as e:
            msg = (
                "Unable to find element by IRI "
                f"{iri_.serialize()} in the document."
            )
            raise ValueError(msg) from e

    def references_other_element(self) -> bool:
        """Check if the element contains IRI reference to another element.

        This method checks if the element contains any attributes that
        reference another element in the document. The reference must be
        local and valid, meaning that if the IRI cannot be resolved to an
        element in the document, the method returns `False`. The entire
        document is searched (not just the descendants of this element).

        A warning is emitted if a dangling IRI reference is found.

        Returns:
            `True` if the element contains a local IRI reference to another
            element in the document, `False` otherwise.

        """
        return self.__references_element_in(self.__document_ids())

    def __document_ids(self) -> frozenset[str]:
        return frozenset(
            element.id
            for element in self.get_root().find_all()
            if element.id is not None
        )

    def __references_element_in(self, ids: frozenset[str]) -> bool:
        for attr_name in _REFERENCE_ATTR_NAMES:
            attr = self.__get_attr_or_default(attr_name)

            if not (isinstance(attr, Iri) and attr.is_local):
                continue

            if attr.fragment in ids:
                return True

            warnings.warn(
                f"Dangling IRI reference {attr_name}={attr.serialize()!r}",
                stacklevel=3,
            )

        return False

    def get_iri(self) -> Iri:
        """Obtain a local IRI reference to this element.

        The reference is constructed based on the element's id. If the element
        has no id, an exception is raised.

        Returns:
            A local IRI reference to this element.

        Raises:
            RuntimeError: If the element has no id.

        """
        if self.id is None:
            msg = "Unable to create local IRI reference to element with no id"
            raise RuntimeError(msg)

        return Iri(fragment=self.id)

    def get_func_iri(self) -> FuncIri:
        """Obtain a local FuncIRI reference to this element.

        The reference is constructed based on the element's id. If the element
        has no id, an exception is raised.

        Returns:
            A local FuncIRI reference to this element.

        Raises:
            RuntimeError: If the element has no id.

        """
        return self.get_iri().to_func_iri()

    # endregion
    # region Serialization

    @override
    def to_beautifulsoup_object(self) -> bs4.Tag:
        element = bs4.Tag(
            name=element_name(self),
            can_be_empty_element=True,
            prefix=self.prefix,
            is_xml=True,
        )

        element.can_be_empty_element = len(self.__children) == 0

        for key, value in self.all_attrs().items():
            element[key] = serialize_attr(key, value)

        for child in self.children:
            element.append(child.to_beautifulsoup_object())

        if element_name(self) == "svg":
            formatter = get_current_formatter()

            if formatter.xmlns == "always":
                element["xmlns"] = SVG_XMLNS
            elif formatter.xmlns == "never":
                del element["xmlns"]

        return element

    # endregion
    # region Transforms and Reification

    def __get_main_transform_attribute(
        self,
    ) -> Literal["transform", "gradientTransform", "patternTransform"]:
        match element_name(self):
            case "linearGradient" | "radialGradient":
                return "gradientTransform"
            case "pattern":
                return "patternTransform"
            case _:
                return "transform"

    @property
    def main_transform(self) -> Transform | None:
        """The main transform attribute of the element.

        For most elements, this is the `transform` attribute. However, certain
        elements such as `linearGradient` have their own specialized
        transform attribute, in which case the `transform` attribute is
        ignored.

        This attribute is an alias to the "main" or "active" transform
        attribute of the element.

        The main transform attributes for the elements are:
        - `gradientTransform` for `linearGradient` and `radialGradient`
        - `patternTransform` for `pattern`
        - `transform` for all other elements
        """
        transform_attr_name = self.__get_main_transform_attribute()

        return cast(
            Transform | None,
            self.__get_attr_or_default(transform_attr_name),
        )

    @main_transform.setter
    def main_transform(self, value: Transform | None) -> None:
        transform_attr_name = self.__get_main_transform_attribute()

        setattr(self, transform_attr_name, value)

    def decompose_transform_origin(self) -> None:
        """Decompose the `transform-origin` attribute into `transform`.

        This function replaces the `transform-origin` attribute with a pair of
        `Translate` transformations in the `transform` attribute. The resulting
        `transform` attribute looks like this:

        ```
        self.transform = [
            Translate(tx, ty),
            *self.transform,
            Translate(-tx, -ty),
        ]
        ```

        If the `transform-origin` attribute is not set, this function does
        nothing.

        Raises:
            SvgTransformOriginError: If the value of the `transform-origin`
                attribute cannot be decomposed.

        """
        if self.transform_origin is None:
            return

        if not (
            isinstance(self.transform_origin, tuple)
            and isinstance(self.transform_origin[0], Length)
            and isinstance(self.transform_origin[1], Length)
        ):
            raise SvgTransformOriginError(self.transform_origin)

        if not self.main_transform:
            self.main_transform = []

        tx = float(self.transform_origin[0])
        ty = float(self.transform_origin[1])

        self.main_transform.insert(0, Translate(tx, ty))
        self.main_transform.append(Translate(-tx, -ty))

        self.transform_origin = None

    def apply_transformation(
        self, transformation: TransformFunction, /
    ) -> None:
        """Apply a transformation to the attributes of the element.

        Args:
            transformation: The transformation to apply.

        Raises:
            ValueError: If the transformation is not supported.
            SvgLengthConversionError: If a length attribute is not convertible
                to user units.

        """
        match transformation:
            case Translate():
                _translate(self, transformation)
            case Scale():
                _scale(self, transformation)
            case _:
                msg = f"Unsupported transformation: {transformation}"
                raise ValueError(msg)

    def __reify_this(self, *, limit: int, ids: frozenset[str]) -> None:
        if limit < 0:
            raise ValueError("Limit must be a positive integer")

        self.decompose_transform_origin()

        if not self.main_transform:
            return

        decompose_matrices(transform=self.main_transform)

        reified = 0
        i = 0

        while reified < limit and i < len(self.main_transform):
            if not isinstance(self.main_transform[i], Reifiable):
                i += 1
                continue

            # move the transformation to the end of the list where it can
            # be directly applied to the element
            _move_transformation_to_end(self.main_transform, i)
            transformation = self.main_transform[-1]

            try:
                self.apply_transformation(transformation)
            except ValueError:
                break

            self.main_transform.pop()

            for child in self.find_all(recursive=False):
                if element_name(child) == "stop":
                    continue

                # bounding box paint servers are relative to the referencing
                # element, so they are transformed along with it
                if isinstance(
                    child, GradientUnitsAttr
                ) and child.gradientUnits in {None, "objectBoundingBox"}:
                    continue

                if isinstance(
                    child, PatternUnitsAttr
                ) and child.patternUnits in {None, "objectBoundingBox"}:
                    continue

                if child.main_transform is None:
                    child.main_transform = []

                # decompose transform-origin before we prepend
                child.decompose_transform_origin()
                child.main_transform.insert(0, transformation)

                child.__reify(  # noqa: SLF001
                    limit=1,
                    recursive=False,
                    remove_transform_list_if_empty=False,
                    ids=ids,
                )

            reified += 1

    def __can_reify(self, ids: frozenset[str]) -> bool:
        # transformations on <use> elements cannot be reified.
        # reification would only work if all usages of the referenced element
        # via <use> have equal transform attributes (f.e. if the referenced
        # element is only used once), in which case we would continue with
        # reification on the referenced element (probably not worth the hassle)
        # patternTransforms also cannot be reified (no clue why)
        if element_name(self) in {"use", "pattern"}:
            return False

        main_transform_attr_name = self.__get_main_transform_attribute()

        if main_transform_attr_name != "transform" and self.transform:
            warnings.warn(
                (
                    f"Attribute 'transform' on element {type(self)} has "
                    f"no effect. Use {main_transform_attr_name!r} instead."
                ),
                stacklevel=2,
            )

        if (
            main_transform_attr_name == "gradientTransform"
            and self.__get_attr_or_default("gradientUnits")
            == "objectBoundingBox"
        ):
            return False

        # reification of elements that reference other elements (f.e. paint
        # servers or clipping paths) is problematic. there is a lot of stuff
        # that can go wrong here, so we just disable this for now

        # TODO: this is overly general; find out in which cases this is
        # actually needed
        return not self.__references_element_in(ids)

    def reify(
        self,
        *,
        limit: int = sys.maxsize,
        recursive: bool = True,
        remove_transform_list_if_empty: bool = True,
    ) -> None:
        """Apply transformations defined by the `transform` attribute.

        This method takes the transformations defined by the `transform`
        attribute and applies them directly to the coordinate, length, and
        other attributes of the element. The transformations are applied in
        the order in which they are defined. The result of this operation
        should be a visually identical element with the `transform` attribute
        reduced or removed (depending on the `limit` parameter).

        Only `Translate` and `Scale` transformations can be reified. If
        the `transform` attribute contains other transformations, their
        parameters are adjusted so that `Translate` and `Scale` transformations
        can be applied. Unsupported transformations are ignored.

        Reification stops at the first transformation that cannot be applied
        to the element, such as a non-uniform `Scale`. That transformation and
        everything preceding it are left in the `transform` attribute.

        If all transformations are successfully applied, the `transform`
        attribute is removed from the element.

        All length values in the element must be convertible to user units.

        Args:
            limit: The maximum number of transformations to apply. If the
                `transform` attribute contains more transformations than the
                limit, the remaining transformations are kept in the attribute
                and not applied. The limit must be a positive integer and is
                applied on a per-element basis.
            recursive: If `True`, the method is called recursively on all
                child elements that support reification.
            remove_transform_list_if_empty: If `True`, the `transform`
                attribute is set to `None` if the list is empty after
                reification.

        Raises:
            ValueError: If the limit is not a positive integer.
            SvgUnitConversionError: If a length value cannot be converted to
                user units.
            SvgTransformOriginError: If the value of the `transform-origin`
                attribute is unsupported.
            SvgLengthConversionError: If a length value cannot be
                converted to user units.

        Examples:
            >>> from svglab import Rect, Length, Scale, Translate
            >>> rect = Rect(
            ...     x=Length(10),
            ...     y=Length(20),
            ...     width=Length(20),
            ...     height=Length(40),
            ...     transform=[Translate(5, 5)],
            ... )
            >>> rect.reify()
            >>> rect.x
            Length(value=15.0, unit=None)
            >>> rect.y
            Length(value=25.0, unit=None)
            >>> rect.width
            Length(value=20.0, unit=None)
            >>> rect.height
            Length(value=40.0, unit=None)
            >>> rect.transform is None
            True

            A transformation that cannot be applied is left in place:

            >>> rect = Rect(width=Length(20), transform=[Scale(2, 3)])
            >>> rect.reify()
            >>> rect.transform
            [Scale(sx=2.0, sy=3.0)]
            >>> rect.width
            Length(value=20.0, unit=None)

        """
        self.__reify(
            limit=limit,
            recursive=recursive,
            remove_transform_list_if_empty=remove_transform_list_if_empty,
            ids=self.__document_ids(),
        )

    def __reify(
        self,
        *,
        limit: int,
        recursive: bool,
        remove_transform_list_if_empty: bool,
        ids: frozenset[str],
    ) -> None:
        if not self.__can_reify(ids):
            return

        self.__reify_this(limit=limit, ids=ids)

        if remove_transform_list_if_empty and not self.main_transform:
            self.main_transform = None

        if recursive:
            for child in self.find_all(recursive=False):
                child.__reify(  # noqa: SLF001
                    limit=limit,
                    recursive=True,
                    remove_transform_list_if_empty=remove_transform_list_if_empty,
                    ids=ids,
                )

    # endregion


# Models defer their build, so the forward reference in `Entity.parent` would
# otherwise stay unresolved in every subclass and fail to resolve later in the
# subclass's own module, where `Element` is not in scope.
Entity.model_rebuild()
Element.model_rebuild()


@final
class UnknownElement(Element):
    """Represents an unknown element that is not part of the SVG specification.

    This element has no standard parsed attributes. All attributes are treated
    as extra attributes.

    If you need to parse custom elements including their attributes, it is
    recommended to subclass the `Element` class instead; this class is only
    intended as a last-resort fallback so we don't lose information about
    elements the library does not know about.

    """

    element_name: str = pydantic.Field(frozen=True, min_length=1)
    """The name of the element."""


class CharacterData(Entity, metaclass=abc.ABCMeta):
    """The base class of text-based elements.

    Text-based elements are elements that are represented by a single string.

    Common examples of text-based elements in XML are:
    - `CDATA` sections (`CData`)
    - comments (`Comment`)
    - text (`Text`)
    - processing instructions (for example, `<?xml version="1.0"?>`)
    - Document Type Definitions (DTDs; for example, `<!DOCTYPE html>`)
    """

    content: str = pydantic.Field(frozen=True, min_length=1)

    @override
    def _eq(self, other: Entity) -> bool:
        return (
            isinstance(other, CharacterData)
            and self.content == other.content
        )

    @override
    def _hash(self) -> int:
        return hash((type(self), self.content))

    @override
    def __repr__(self) -> str:
        name = type(self).__name__
        return f"{name}({self.content!r})"


@final
class CData(CharacterData):
    """A `CDATA` section.

    A `CDATA` section is a block of text that is not parsed by the XML parser,
    but is interpreted verbatim.

    `CDATA` sections are used to include text that contains characters
    that would otherwise be interpreted as XML markup.

    Example: `<![CDATA[<g id="foo"></g>]]>`
    """

    def __init__(self, content: str, /) -> None:
        """Initialize a CDATA section.

        Args:
            content: The text content of the CDATA section (excluding the
                `<![CDATA[` and `]]>` markers).

        """
        super().__init__(content=content)

    @override
    def to_beautifulsoup_object(self) -> bs4.CData:
        return bs4.CData(self.content)


@final
class Comment(CharacterData):
    """A comment.

    A comment is a block of text that is not parsed by the XML parser,
    but is ignored.

    Comments are used to include notes and other information that is not
    intended to be displayed to the user.

    Example: `<!-- This is a comment -->`
    """

    def __init__(self, content: str, /) -> None:
        """Initialize a comment.

        Args:
            content: The text content of the comment (excluding the `<!--` and
                `-->` markers).

        """
        super().__init__(content=content)

    @override
    def to_beautifulsoup_object(self) -> bs4.Comment:
        return bs4.Comment(self.content)


@final
class RawText(CharacterData):
    """A text node.

    A text node is a block of text that is parsed by the XML parser.

    Text nodes are used to include text that is intended to be displayed
    to the user.

    Example: `Hello, world!`
    """

    def __init__(self, content: str, /) -> None:
        """Initialize a text node.

        Args:
            content: The text content of the node.

        """
        super().__init__(content=content)

    @override
    def to_beautifulsoup_object(self) -> bs4.NavigableString:
        return bs4.NavigableString(self.content)
