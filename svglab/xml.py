"""Abstract base classes for representing common XML entities.

This module defines the following classes:
- `Entity`: The base class for all XML entities.
- `Element`: A subclass of `Entity` that represents an XML element.
- `CharacterData`: A subclass of `Entity` that represents a textual entity.
- `CData`, `Comment`, `RawText`: Subclasses of `CharacterData` that represent
    specific types of character data in XML.
"""

from __future__ import annotations

import abc
import collections
import reprlib
import sys
import warnings
from collections.abc import Generator, Mapping

import bs4
import pydantic
from typing_extensions import (
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

from svglab import constants, errors, models, serialize
from svglab.attrparse import iri, length, transform
from svglab.attrs import attrdefs, attrgroups
from svglab.attrs import names as attr_names
from svglab.elements import names
from svglab.utils import bsutils, iterutils, mathutils, miscutils


_T = TypeVar("_T")
_T_element = TypeVar("_T_element", bound="Element")
_TransformT1 = TypeVar("_TransformT1", bound=transform.TransformFunction)
_TransformT2 = TypeVar("_TransformT2", bound=transform.TransformFunction)

_EMPTY_PARAM: Final = object()
"""A sentinel value for an empty parameter."""


class StrokeWidthScaled:
    """The element's `stroke-width` attribute should be scaled."""


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
        case length.Length(_, "%"):
            return attr
        case int() | float() | length.Length():
            return cast(_T, attr * by)
        case list() | tuple():
            return type(attr)(_scale_attr(item, by) for item in attr)
        case _:
            return attr


def _scale_stroke_width(
    element: attrdefs.StrokeWidthAttr, by: float
) -> None:
    if (
        isinstance(element, attrdefs.VectorEffectAttr)
        and element.vector_effect == "non-scaling-stroke"
    ):
        return

    sw_set = element.stroke_width is not None

    if not sw_set:
        if not isinstance(element, StrokeWidthScaled):
            return

        element.stroke_width = length.Length(1)

    element.stroke_width = _scale_attr(element.stroke_width, by)  # type: ignore[reportAttributeAccessIssue]

    # if stroke-width was not set and the scaled value is 1 (default),
    # remove the attribute
    if (
        not sw_set
        and isinstance(element.stroke_width, length.Length)
        and mathutils.is_close(float(element.stroke_width), 1)
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
    if isinstance(element, attrdefs.StrokeDasharrayAttr) and isinstance(
        element.stroke_dasharray, list
    ):
        element.stroke_dasharray = [
            _scale_attr(dash, by) for dash in element.stroke_dasharray
        ]
    if isinstance(element, attrdefs.StrokeDashoffsetAttr):
        element.stroke_dashoffset = _scale_attr(
            element.stroke_dashoffset, by
        )


def _scale(element: object, scale: transform.Scale) -> None:  # noqa: PLR0915
    if not mathutils.is_close(scale.sx, scale.sy):
        raise ValueError("Non-uniform scaling is not supported.")

    factor = scale.sx

    if mathutils.is_close(factor, 1):
        return

    if isinstance(element, attrdefs.WidthAttr):
        element.width = _scale_attr(element.width, factor)
    if isinstance(element, attrdefs.HeightAttr):
        element.height = _scale_attr(element.height, factor)
    if isinstance(element, attrdefs.RAttr):
        element.r = _scale_attr(element.r, factor)
    if isinstance(element, attrdefs.X1Attr):
        element.x1 = _scale_attr(element.x1, factor)
    if isinstance(element, attrdefs.Y1Attr):
        element.y1 = _scale_attr(element.y1, factor)
    if isinstance(element, attrdefs.X2Attr):
        element.x2 = _scale_attr(element.x2, factor)
    if isinstance(element, attrdefs.Y2Attr):
        element.y2 = _scale_attr(element.y2, factor)
    if isinstance(element, attrdefs.RxAttr):
        element.rx = _scale_attr(element.rx, factor)
    if isinstance(element, attrdefs.RyAttr):
        element.ry = _scale_attr(element.ry, factor)
    if isinstance(element, attrdefs.CxAttr):
        element.cx = _scale_attr(element.cx, factor)
    if isinstance(element, attrdefs.CyAttr):
        element.cy = _scale_attr(element.cy, factor)
    if isinstance(element, attrdefs.FxAttr):
        element.fx = _scale_attr(element.fx, factor)
    if isinstance(element, attrdefs.FyAttr):
        element.fy = _scale_attr(element.fy, factor)
    if isinstance(element, attrdefs.FontSizeAttr):
        element.font_size = _scale_attr(element.font_size, factor)
    if (
        isinstance(element, attrdefs.PointsAttr)
        and element.points is not None
    ):
        element.points = [scale @ point for point in element.points]
    if isinstance(element, attrdefs.DAttr) and element.d is not None:
        element.d = scale @ element.d

    # these assignments have to be mutually exclusive, because the
    # type checker doesn't know that x being a <number> implies that x is
    # not a <coordinate> and vice versa
    if isinstance(element, attrdefs.XNumberAttr):  # noqa: SIM114
        element.x = _scale_attr(element.x, factor)
    elif isinstance(element, attrdefs.XCoordinateAttr):  # noqa: SIM114
        element.x = _scale_attr(element.x, factor)
    elif isinstance(element, attrdefs.XListOfCoordinatesAttr):
        element.x = _scale_attr(element.x, factor)

    if isinstance(element, attrdefs.YNumberAttr):  # noqa: SIM114
        element.y = _scale_attr(element.y, factor)
    elif isinstance(element, attrdefs.YCoordinateAttr):  # noqa: SIM114
        element.y = _scale_attr(element.y, factor)
    elif isinstance(element, attrdefs.YListOfCoordinatesAttr):
        element.y = _scale_attr(element.y, factor)

    if isinstance(element, attrdefs.StrokeWidthAttr):
        _scale_stroke_width(element, factor)

    # no need to scale distance-along-a-path attributes if a custom path
    # length is provided because those attributes and pathLength are
    # proportional
    if not isinstance(element, attrdefs.PathLengthAttr):
        scale_distance_along_a_path_attrs(element, factor)

    if isinstance(element, attrdefs.OffsetNumberPercentageAttr):
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
        case length.Length(_, "%"):
            return attr
        case int() | float():
            return cast(_T, attr + by)
        case length.Length():
            return attr + length.Length(by)
        case list() | tuple():
            return type(attr)(_translate_attr(item, by) for item in attr)
        case _:
            return attr


# pyright goes nuts if `element` is annotated as `Element`... seems like a bug
# luckily we don't really care
def _translate(element: object, translate: transform.Translate) -> None:
    tx, ty = translate.tx, translate.ty

    if mathutils.is_close(tx, 0) and mathutils.is_close(ty, 0):
        return

    zero = length.Length.zero()

    # these attributes are mandatory for the respective elements
    if isinstance(element, attrdefs.X1Attr):
        element.x1 = _translate_attr(element.x1, tx)
    if isinstance(element, attrdefs.Y1Attr):
        element.y1 = _translate_attr(element.y1, ty)
    if isinstance(element, attrdefs.X2Attr):
        element.x2 = _translate_attr(element.x2, tx)
    if isinstance(element, attrdefs.Y2Attr):
        element.y2 = _translate_attr(element.y2, ty)

    # but these are not, so if they are not present, we initialize them
    # to 0
    if isinstance(element, attrdefs.CxAttr):
        element.cx = _translate_attr(element.cx or zero, tx)
    if isinstance(element, attrdefs.CyAttr):
        element.cy = _translate_attr(element.cy or zero, ty)

    if isinstance(element, attrdefs.XNumberAttr):
        element.x = _translate_attr(element.x or 0, tx)
    elif isinstance(element, attrdefs.XCoordinateAttr):
        element.x = _translate_attr(element.x or zero, tx)
    elif isinstance(element, attrdefs.XListOfCoordinatesAttr):
        element.x = _translate_attr(element.x, tx)

    if isinstance(element, attrdefs.YNumberAttr):
        element.y = _translate_attr(element.y or 0, ty)
    elif isinstance(element, attrdefs.YCoordinateAttr):
        element.y = _translate_attr(element.y or zero, ty)
    elif isinstance(element, attrdefs.YListOfCoordinatesAttr):
        element.y = _translate_attr(element.y, ty)

    if (
        isinstance(element, attrdefs.PointsAttr)
        and element.points is not None
    ):
        element.points = [translate @ point for point in element.points]

    if isinstance(element, attrdefs.DAttr) and element.d is not None:
        element.d = translate @ element.d

    if isinstance(element, attrdefs.OffsetNumberPercentageAttr):
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
        case (transform.Translate(), transform.Translate()) | (
            transform.Scale(),
            transform.Scale(),
        ):
            return b, a

        # translate <-> scale
        case transform.Translate(tx, ty), transform.Scale(sx, sy) as scale:
            return scale, type(a)(tx / sx, ty / sy)

        case transform.Scale(sx, sy) as scale, transform.Translate(tx, ty):
            return type(b)(sx * tx, sy * ty), scale

        # translate <-> rotate
        case transform.Rotate(angle, cx, cy), transform.Translate(tx, ty):
            return type(b)(tx, ty), type(a)(angle, cx - tx, cy - ty)
        case transform.Translate(tx, ty), transform.Rotate(angle, cx, cy):
            return type(b)(angle, cx + tx, cy + ty), type(a)(tx, ty)

        # scale <-> rotate
        case transform.Rotate(angle, cx, cy), transform.Scale(
            sx, sy
        ) as scale:
            return scale, type(a)(angle, cx / sx, cy / sy)
        case transform.Scale(sx, sy) as scale, transform.Rotate(
            angle, cx, cy
        ):
            return type(b)(angle, cx * sx, cy * sy), scale

        # translate <-> skew
        case transform.SkewX(angle) as skew_x, transform.Translate(tx, ty):
            return type(b)(tx + ty * mathutils.tan(angle), ty), skew_x

        case transform.Translate(tx, ty), transform.SkewX(angle) as skew_x:
            return skew_x, type(a)(tx - ty * mathutils.tan(angle), ty)

        case transform.SkewY(angle) as skew_y, transform.Translate(tx, ty):
            return type(b)(tx, ty + tx * mathutils.tan(angle)), skew_y

        case transform.Translate(tx, ty), transform.SkewY(angle) as skew_y:
            return skew_y, type(a)(tx, ty - tx * mathutils.tan(angle))

        # scale <-> skew
        case transform.Scale(sx, sy) as scale, transform.SkewX(angle):
            if mathutils.is_close(sx, sy):
                return b, a

            angle = mathutils.arctan(sx / sy * mathutils.tan(angle))
            return type(b)(angle), scale

        case transform.SkewX(angle), transform.Scale(sx, sy) as scale:
            if mathutils.is_close(sx, sy):
                return b, a

            angle = mathutils.arctan(sy / sx * mathutils.tan(angle))
            return scale, type(a)(angle)

        case transform.Scale(sx, sy) as scale, transform.SkewY(angle):
            if mathutils.is_close(sx, sy):
                return b, a

            angle = mathutils.arctan(sy / sx * mathutils.tan(angle))
            return type(b)(angle), scale

        case transform.SkewY(angle), transform.Scale(sx, sy) as scale:
            if mathutils.is_close(sx, sy):
                return b, a

            angle = mathutils.arctan(sx / sy * mathutils.tan(angle))

            return scale, type(a)(angle)
        case _:
            raise errors.SvgTransformSwapError(a, b)


def _move_transformation_to_end(
    transform: transform.Transform, index: int
) -> None:
    """Move a transformation to the end of the transform list.

    This function moves a transformation from the given index to the end of
    the list, swapping it with each transformation that follows it.
    The transformations in the list are adjusted so that the result is the
    same. The transformation itself may have its parameters adjusted as well.

    Args:
        transform: A list of transformations.
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
    if not (0 <= index < len(transform)):
        msg = f"Index {index=} out of range"
        raise ValueError(msg)

    for i in range(index, len(transform) - 1):
        transform[i], transform[i + 1] = swap_transforms(
            transform[i], transform[i + 1]
        )


def element_name(element: Element | type[Element], /) -> names.ElementName:
    """Get the SVG element name of the given element or element class.

    Args:
    element: The element or element class.

    Returns:
    The SVG element name.

    Examples:
    >>> from svglab import Rect
    >>> element_name(Rect)
    'rect'

    """
    element_cls = element if isinstance(element, type) else type(element)

    return names.ELEMENT_NAME_TO_NORMALIZED.inverse[element_cls.__name__]


class Entity(models.BaseModel, metaclass=abc.ABCMeta):
    """The base class of the SVG element hierarchy."""

    parent: Element | None = pydantic.Field(default=None, init=False)

    def to_xml(
        self,
        *,
        pretty: bool = True,
        formatter: serialize.Formatter | None = None,
    ) -> str:
        """Convert the element to XML.

        Args:
        pretty: Whether to produce pretty-printed XML.
        indent: The number of spaces to indent each level of the document.
        formatter: The formatter to use for serialization.

        Returns:
        The XML representation of the element.

        Examples:
        >>> from svglab import Rect, Length
        >>> rect = Rect(id="foo", stroke_linecap="round")
        >>> rect.to_xml()
        '<rect id="foo" stroke-linecap="round"/>'

        """
        with formatter or serialize.get_current_formatter():
            soup = self.to_beautifulsoup_object()
            return bsutils.beautifulsoup_to_str(soup, pretty=pretty)

    @abc.abstractmethod
    def to_beautifulsoup_object(self) -> bs4.PageElement:
        """Convert the element to a corresponding `BeautifulSoup` object."""

    @abc.abstractmethod
    def _eq(self, other: Entity, /) -> bool: ...

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
        return (
            self._eq(other)
            if miscutils.basic_compare(other, self=self)
            else False
        )


class Element(
    Entity,
    attrgroups.CoreAttrs,
    attrgroups.PresentationAttrs,
    metaclass=abc.ABCMeta,
):
    """An element.

    An element is an entity that has a name, a set of attributes,
    and (optionally) one or more elements as children.

    Elements can have standard attributes (for example, `id`, `class`,
    `color`) and non-standard user-defined attributes.

    Example: `<rect id="foo" class="bar" color="red" />`
    ```
    """

    model_config = pydantic.ConfigDict(
        extra="allow",
        alias_generator=pydantic.AliasGenerator(
            validation_alias=lambda name: pydantic.AliasChoices(
                name,
                attr_names.ATTR_NAME_TO_NORMALIZED.inverse.get(name, name),
            ),
            serialization_alias=(
                lambda name: attr_names.ATTR_NAME_TO_NORMALIZED.inverse.get(
                    name, name
                )
            ),
        ),
    )

    prefix: str | None = None

    __children: list[Entity] = pydantic.PrivateAttr(default_factory=list)

    @pydantic.model_validator(mode="after")
    def __validate_extra(self) -> Element:  # pyright: ignore[reportUnusedFunction]
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

    def standard_attrs(self) -> Mapping[attr_names.AttributeName, object]:
        """Get the standard attributes of the element.

        Standard attributes are attributes that are part of the SVG standard.

        Returns:
            A mapping of standard attribute names to their values. The mapping
            should be considered immutable.

        """
        dump = self.model_dump(by_alias=True, exclude_none=True)

        return {
            attr: getattr(self, attr_names.ATTR_NAME_TO_NORMALIZED[attr])
            for key, _ in dump.items()
            if (attr := cast(attr_names.AttributeName, key))
            in attr_names.ATTR_NAME_TO_NORMALIZED
        }

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

    @override
    def _eq(self, other: Entity) -> bool:
        return (
            isinstance(other, Element)
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
    def descendants(self) -> Generator[Entity]:
        """Iterate over the descendants of the element.

        The descendants of the element are the children and their children,
        and so on. The descendants are returned in a breath-first order.

        Yields:
            The descendants of the element.

        """
        queue = collections.deque(self.children)

        while queue:
            child = queue.popleft()
            yield child

            if isinstance(child, Element):
                queue.extend(child.children)

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

        should_yield = False

        for sibling in self.parent.children:
            if should_yield:
                yield sibling
            elif sibling is self:
                should_yield = True

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

        for sibling in self.parent.children:
            if sibling is self:
                return

            yield sibling

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
                if the child already has a parent.

        """
        if child is self:
            raise ValueError("Cannot add an element as a child of itself.")

        if child.parent is not None:
            raise ValueError(
                "Cannot add a child that already has a parent."
            )

        if index is None:
            self.__children.append(child)
        else:
            self.__children.insert(index, child)

        child.parent = self

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
        for i, elem in enumerate(self.children):
            if elem is child:
                return self.pop_child(i)

        raise ValueError("Child not found")

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
        child.parent = None

        return child

    def clear_children(self) -> None:
        """Remove all children from the element."""
        for child in self.__children:
            child.parent = None

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
        return self.__children.index(child, start, stop)

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
            element[key] = serialize.serialize_attr(key, value)

        for child in self.children:
            element.append(child.to_beautifulsoup_object())

        if element_name(self) == "svg":
            formatter = serialize.get_current_formatter()

            if formatter.xmlns == "always":
                element["xmlns"] = constants.SVG_XMLNS
            elif formatter.xmlns == "never":
                del element["xmlns"]

        return element

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
    def main_transform(self) -> transform.Transform | None:
        """The main transform attribute of the element.

        For most elements, this is the `transform` attribute. However, certain
        elements such as `linearGradient` have theis own specialized
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
            transform.Transform | None,
            self.__get_attr_or_default(transform_attr_name),
        )

    def get_root(self) -> Element:
        """Get the top-level ancestor of the element.

        The root ancestor is the first ancestor that has no parent. If the
        element has no parent, it is considered the root ancestor.

        Returns:
            The root ancestor of the element.

        """
        return iterutils.take_last(self.ancestors) or self

    def resolve_iri(self, iri_: iri.Iri, /) -> Element:
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
        reference_attr_names: list[attr_names.AttributeName] = [
            "xlink:href",
            "href",
            "fill",
            "stroke",
            "mask",
            "clip-path",
        ]

        for attr_name in reference_attr_names:
            if not hasattr(self, attr_name):
                continue

            attr = self.__get_attr_or_default(attr_name)

            if not (isinstance(attr, iri.Iri) and attr.is_local):
                continue

            try:
                self.get_root().resolve_iri(attr)
            except ValueError:
                warnings.warn(
                    f"Dangling IRI reference {attr_name}={attr.serialize()!r}",
                    stacklevel=2,
                )
            else:
                return True

        return False

    @main_transform.setter
    def main_transform(self, value: transform.Transform | None) -> None:
        transform_attr_name = self.__get_main_transform_attribute()

        setattr(self, transform_attr_name, value)

    def __get_attr_or_default(
        self, attr_name: attr_names.AttributeName
    ) -> object:
        attrs = self.standard_attrs()

        if attr_name in attrs:
            return attrs[attr_name]

        match attr_name:
            case "gradientUnits":
                return "objectBoundingBox"
            case "patternUnits":
                return "objectBoundingBox"
            case "patternContentUnits":
                return "userSpaceOnUse"
            case _:
                return None

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
            and isinstance(self.transform_origin[0], length.Length)
            and isinstance(self.transform_origin[1], length.Length)
        ):
            raise errors.SvgTransformOriginError(self.transform_origin)

        if not self.main_transform:
            self.main_transform = []

        tx = float(self.transform_origin[0])
        ty = float(self.transform_origin[1])

        self.main_transform.insert(0, transform.Translate(tx, ty))
        self.main_transform.append(transform.Translate(-tx, -ty))

        self.transform_origin = None

    def apply_transformation(
        self, transformation: transform.TransformFunction, /
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
            case transform.Translate():
                _translate(self, transformation)
            case transform.Scale():
                _scale(self, transformation)
            case _:
                msg = f"Unsupported transformation: {transformation}"
                raise ValueError(msg)

    def __reify_this(self, *, limit: int = sys.maxsize) -> None:
        if limit < 0:
            raise ValueError("Limit must be a positive integer")

        self.decompose_transform_origin()

        if not self.main_transform:
            return

        transform.decompose_matrices(transform=self.main_transform)

        reified = 0
        i = 0

        while reified < limit and i < len(self.main_transform):
            if not isinstance(self.main_transform[i], transform.Reifiable):
                i += 1
                continue

            try:
                # move the transformation to the end of the list where it can
                # be directly applied to the elementf
                _move_transformation_to_end(self.main_transform, i)
                transformation = self.main_transform.pop()

                self.apply_transformation(transformation)

                for child in self.find_all(recursive=False):
                    if element_name(child) == "stop":
                        continue

                    if child.main_transform is None:
                        child.main_transform = []

                    # decompose transform-origin before we prepend
                    child.decompose_transform_origin()
                    child.main_transform.insert(0, transformation)

                    child.reify(
                        limit=1,
                        recursive=False,
                        remove_transform_list_if_empty=False,
                    )
            except (ValueError, errors.SvgTransformSwapError) as e:
                raise errors.SvgReifyError from e

            reified += 1

    def __can_reify(self) -> bool:
        # transformations on <use> elements cannot be reified.
        # reification would only work if all usages of the referenced element
        # via <use> have equal transform attributes (f.e. if the referenced
        # element is only used once), in which case we would continue with
        # reification on the referenced element (probably not worth the hassle)
        # patternTransforms also cannot be reified (no clue why)
        if element_name(self) in ["use", "pattern"]:
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
        return not self.references_other_element()

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

        Only `Translate` and `Scale` transformations are can be reified. If
        the `transform` attribute contains other transformations, their
        parameters are adjusted so that `Translate` and `Scale` transformations
        can be applied. Unsupported transformations are ignored.

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
            SvgReifyError: If the `transform` attribute cannot be reified.
            SvgUnitConversionError: If a length value cannot be converted to
                user units.
            SvgTransformOriginError: If the value of the `transform-origin`
                attribute is unsupported.

        Examples:
            >>> from svglab import Rect, Length, Translate
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

        """
        if not self.__can_reify():
            return

        self.__reify_this(limit=limit)

        if remove_transform_list_if_empty and not self.transform:
            self.transform = None

        if recursive:
            for child in self.find_all(recursive=False):
                child.reify(
                    limit=limit,
                    recursive=True,
                    remove_transform_list_if_empty=remove_transform_list_if_empty,
                )

    @overload
    def find_all(
        self, /, *, recursive: bool = True
    ) -> Generator[Element]: ...

    @overload
    def find_all(
        self, *elements: type[_T_element], recursive: bool = True
    ) -> Generator[_T_element]: ...

    @overload
    def find_all(
        self,
        *elements: type[Element] | names.ElementName,
        recursive: bool = True,
    ) -> Generator[Element]: ...

    def find_all(
        self,
        *elements: type[Element] | names.ElementName,
        recursive: bool = True,
    ) -> Generator[Element]:
        """Find all elements that match the given search criteria.

        Args:
        elements: The elements to search for. Can be element names or element
        classes.  If no search criteria are provided, all elements are
        returned.
        recursive: If `False`, only search the direct children of the element,
        otherwise search all descendants.

        Returns:
        An iterator over all elements that match the search criteria.

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
        self, *elements: type[_T_element], recursive: bool = True
    ) -> _T_element: ...

    @overload
    def find(
        self,
        *elements: type[Element] | names.ElementName,
        recursive: bool = True,
    ) -> Element: ...

    @overload
    def find(
        self,
        *elements: type[_T_element],
        recursive: bool = True,
        default: _T = _EMPTY_PARAM,
    ) -> _T_element | _T: ...

    @overload
    def find(
        self,
        *elements: type[Element] | names.ElementName,
        recursive: bool = True,
        default: _T = _EMPTY_PARAM,
    ) -> Element | _T: ...

    def find(
        self,
        *elements: type[Element] | names.ElementName,
        recursive: bool = True,
        default: _T = _EMPTY_PARAM,
    ) -> Element | _T:
        """Find the first element that matches the given search criteria.

        Args:
        elements: The elements to search for. Can be element names or element
        classes.
        recursive: If `False`, only search the direct children of the element,
        otherwise search all descendants.
        default: The default value to return if no element matches the search
        criteria.

        Returns:
        The first element that matches the search criteria.

        Raises:
        SvgElementNotFoundError: If no element matches the search criteria and
        no default value is provided.

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
            raise errors.SvgElementNotFoundError(msg) from e

    @property
    def num_children(self) -> int:
        """Get the number of children of the element.

        Returns:
        The number of children of the element.

        """
        return len(self.__children)

    def has_children(self) -> bool:
        """Check if the element has any children.

        Returns:
        `True` if the element has children, `False` otherwise.

        """
        return self.num_children > 0

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

    @reprlib.recursive_repr()
    @override
    def __repr__(self) -> str:
        name = type(self).__name__
        attrs = dict(self.all_attrs())

        if self.__children:
            attrs["children"] = list(self.children)

        attr_repr = ", ".join(
            f"{key}={value!r}" for key, value in attrs.items()
        )

        return f"{name}({attr_repr})"

    def get_iri(self) -> iri.Iri:
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

        return iri.Iri(fragment=self.id)

    def get_func_iri(self) -> iri.FuncIri:
        """Obtain a local FuncIRI reference to this element.

        The reference is constructed based on the element's id. If the element
        has no id, an exception is raised.

        Returns:
            A local FuncIRI reference to this element.

        Raises:
            RuntimeError: If the element has no id.

        """
        return self.get_iri().to_func_iri()


def _match_element(
    element: Element, /, *, search: type[Element] | names.ElementName
) -> bool:
    """Check if an element matches the given search criteria.

    Args:
    element: The element to check.
    search: The search criteria. Can be an element name or an element class.

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
