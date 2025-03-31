from __future__ import annotations

import abc
import collections
import reprlib
import sys
from collections.abc import Generator, Mapping, Sequence

import bs4
import pydantic
from typing_extensions import (
    Final,
    Self,
    SupportsIndex,
    TypeVar,
    cast,
    overload,
    override,
)

from svglab import constants, errors, models, serialize, utils
from svglab.attrparse import length, transform
from svglab.attrs import common as common_attrs
from svglab.attrs import groups, presentation, regular
from svglab.attrs import names as attr_names
from svglab.elements import names


_T = TypeVar("_T")
_T_tag = TypeVar("_T_tag", bound="Tag")
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


def _scale_stroke_width(tag: presentation.StrokeWidth, by: float) -> None:
    if (
        isinstance(tag, presentation.VectorEffect)
        and tag.vector_effect == "non-scaling-stroke"
    ):
        return

    sw_set = tag.stroke_width is not None

    if not sw_set and not isinstance(tag, StrokeWidthScaled):
        return

    if not sw_set:
        tag.stroke_width = length.Length(1)

    tag.stroke_width = _scale_attr(tag.stroke_width, by)  # type: ignore[reportAttributeAccessIssue]

    # if stroke-width was not set and the scaled value is 1 (default),
    # remove the attribute
    if (
        not sw_set
        and isinstance(tag.stroke_width, length.Length)
        and utils.is_close(float(tag.stroke_width), 1)
    ):
        tag.stroke_width = None


def scale_distance_along_a_path_attrs(tag: object, by: float) -> None:
    if isinstance(tag, presentation.StrokeDasharray) and isinstance(
        tag.stroke_dasharray, list
    ):
        tag.stroke_dasharray = [
            _scale_attr(dash, by) for dash in tag.stroke_dasharray
        ]
    if isinstance(tag, presentation.StrokeDashoffset):
        tag.stroke_dashoffset = _scale_attr(tag.stroke_dashoffset, by)


def _scale(tag: object, scale: transform.Scale) -> None:
    if not utils.is_close(scale.sx, scale.sy):
        raise ValueError("Non-uniform scaling is not supported.")

    factor = scale.sx

    if utils.is_close(factor, 1):
        return

    if isinstance(tag, regular.Width):
        tag.width = _scale_attr(tag.width, factor)
    if isinstance(tag, regular.Height):
        tag.height = _scale_attr(tag.height, factor)
    if isinstance(tag, regular.R):
        tag.r = _scale_attr(tag.r, factor)
    if isinstance(tag, regular.X1):
        tag.x1 = _scale_attr(tag.x1, factor)
    if isinstance(tag, regular.Y1):
        tag.y1 = _scale_attr(tag.y1, factor)
    if isinstance(tag, regular.X2):
        tag.x2 = _scale_attr(tag.x2, factor)
    if isinstance(tag, regular.Y2):
        tag.y2 = _scale_attr(tag.y2, factor)
    if isinstance(tag, regular.Rx):
        tag.rx = _scale_attr(tag.rx, factor)
    if isinstance(tag, regular.Ry):
        tag.ry = _scale_attr(tag.ry, factor)
    if isinstance(tag, regular.Cx):
        tag.cx = _scale_attr(tag.cx, factor)
    if isinstance(tag, regular.Cy):
        tag.cy = _scale_attr(tag.cy, factor)
    if isinstance(tag, common_attrs.FontSize):
        tag.font_size = _scale_attr(tag.font_size, factor)
    if isinstance(tag, regular.Points) and tag.points is not None:
        tag.points = [scale @ point for point in tag.points]
    if isinstance(tag, regular.D) and tag.d is not None:
        tag.d = scale @ tag.d

    # these assignments have to be mutually exclusive, because the
    # type checker doesn't know that x being a <number> implies that x is
    # not a <coordinate> and vice versa
    if isinstance(tag, regular.XNumber):  # noqa: SIM114
        tag.x = _scale_attr(tag.x, factor)
    elif isinstance(tag, regular.XCoordinate):
        tag.x = _scale_attr(tag.x, factor)

    if isinstance(tag, regular.YNumber):  # noqa: SIM114
        tag.y = _scale_attr(tag.y, factor)
    elif isinstance(tag, regular.YCoordinate):
        tag.y = _scale_attr(tag.y, factor)

    if isinstance(tag, presentation.StrokeWidth):
        _scale_stroke_width(tag, factor)

    # no need to scale distance-along-a-path attributes if a custom path
    # length is provided because those attributes and pathLength are
    # proportional
    if not isinstance(tag, regular.PathLength):
        scale_distance_along_a_path_attrs(tag, factor)


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


# pyright goes nuts if `tag` is annotated as `Element`... seems like a bug
# luckily we don't really care
def _translate(tag: object, translate: transform.Translate) -> None:
    tx, ty = translate.tx, translate.ty

    if utils.is_close(tx, 0) and utils.is_close(ty, 0):
        return

    zero = length.Length.zero()

    # these attributes are mandatory for the respective elements
    if isinstance(tag, regular.X1):
        tag.x1 = _translate_attr(tag.x1, tx)
    if isinstance(tag, regular.Y1):
        tag.y1 = _translate_attr(tag.y1, ty)
    if isinstance(tag, regular.X2):
        tag.x2 = _translate_attr(tag.x2, tx)
    if isinstance(tag, regular.Y2):
        tag.y2 = _translate_attr(tag.y2, ty)

    # but these are not, so if they are not present, we initialize them
    # to 0
    if isinstance(tag, regular.Cx):
        tag.cx = _translate_attr(tag.cx or zero, tx)
    if isinstance(tag, regular.Cy):
        tag.cy = _translate_attr(tag.cy or zero, ty)

    if isinstance(tag, regular.XNumber):
        tag.x = _translate_attr(tag.x or 0, tx)
    elif isinstance(tag, regular.XCoordinate):
        tag.x = _translate_attr(tag.x or zero, tx)

    if isinstance(tag, regular.YNumber):
        tag.y = _translate_attr(tag.y or 0, ty)
    elif isinstance(tag, regular.YCoordinate):
        tag.y = _translate_attr(tag.y or zero, ty)

    if isinstance(tag, regular.Points) and tag.points is not None:
        tag.points = [translate @ point for point in tag.points]

    if isinstance(tag, regular.D) and tag.d is not None:
        tag.d = translate @ tag.d


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
            return type(b)(tx + ty * utils.tan(angle), ty), skew_x

        case transform.Translate(tx, ty), transform.SkewX(angle) as skew_x:
            return skew_x, type(a)(tx - ty * utils.tan(angle), ty)

        case transform.SkewY(angle) as skew_y, transform.Translate(tx, ty):
            return type(b)(tx, ty + tx * utils.tan(angle)), skew_y

        case transform.Translate(tx, ty), transform.SkewY(angle) as skew_y:
            return skew_y, type(a)(tx, ty - tx * utils.tan(angle))

        # scale <-> skew
        case transform.Scale(sx, sy) as scale, transform.SkewX(angle):
            if utils.is_close(sx, sy):
                return b, a

            angle = utils.arctan(sx / sy * utils.tan(angle))
            return type(b)(angle), scale

        case transform.SkewX(angle), transform.Scale(sx, sy) as scale:
            if utils.is_close(sx, sy):
                return b, a

            angle = utils.arctan(sy / sx * utils.tan(angle))
            return scale, type(a)(angle)

        case transform.Scale(sx, sy) as scale, transform.SkewY(angle):
            if utils.is_close(sx, sy):
                return b, a

            angle = utils.arctan(sy / sx * utils.tan(angle))
            return type(b)(angle), scale

        case transform.SkewY(angle), transform.Scale(sx, sy) as scale:
            if utils.is_close(sx, sy):
                return b, a

            angle = utils.arctan(sx / sy * utils.tan(angle))

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


def _apply_transformation(
    tag: Tag, transformation: transform.TransformFunction, /
) -> None:
    """Apply a transformation to the attributes of the tag.

    Args:
    tag: The tag to transform.
    transformation: The transformation to apply.

    Raises:
    ValueError: If the transformation is not supported.
    SvgLengthConversionError: If a length attribute is not convertible
    to user units.

    """
    match transformation:
        case transform.Translate():
            _translate(tag, transformation)
        case transform.Scale():
            _scale(tag, transformation)
        case _:
            msg = f"Unsupported transformation: {transformation}"
            raise ValueError(msg)


def tag_name(tag: Tag | type[Tag], /) -> names.TagName:
    """Get the SVG tag name of the given tag or tag class.

    Args:
    tag: The tag or tag class.

    Returns:
    The SVG tag name.

    Examples:
    >>> from svglab import Rect
    >>> tag_name(Rect)
    'rect'

    """
    tag_cls = tag if isinstance(tag, type) else type(tag)

    return names.TAG_NAME_TO_NORMALIZED.inverse[tag_cls.__name__]


class Element(models.BaseModel, metaclass=abc.ABCMeta):
    """The base class of the SVG element hierarchy."""

    parent: Tag | None = pydantic.Field(default=None, init=False)

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
        formatter = formatter or serialize.get_current_formatter()

        with formatter:
            soup = self.to_beautifulsoup_object()
            return utils.beautifulsoup_to_str(
                soup, pretty=pretty, indent=formatter.indent
            )

    @abc.abstractmethod
    def to_beautifulsoup_object(self) -> bs4.PageElement:
        """Convert the element to a corresponding `BeautifulSoup` object."""

    @abc.abstractmethod
    def _eq(self, other: Self, /) -> bool: ...

    @property
    def parents(self) -> Generator[Tag]:
        curr = self.parent

        while curr is not None:
            yield curr
            curr = curr.parent

    @override
    def __eq__(self, other: object) -> bool:
        if not utils.basic_compare(other, self=self):
            return False

        return self._eq(other)


class Tag(
    Element, groups.Core, groups.Presentation, metaclass=abc.ABCMeta
):
    """A tag.

    A tag is an element that has a name, a set of attributes and (optionally)
    one or more elements as children.

    Tags can have standard attributes (for example, `id`, `class`, `color`) and
    non-standard user-defined attributes.

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

    __children: list[Element] = pydantic.PrivateAttr(default_factory=list)

    @pydantic.model_validator(mode="after")
    def __validate_extra(self) -> Tag:  # pyright: ignore[reportUnusedFunction]
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
        assert self.model_extra is not None, "model_extra is None"
        return self.model_extra

    def standard_attrs(self) -> Mapping[attr_names.AttributeName, object]:
        dump = self.model_dump(by_alias=True, exclude_none=True)

        return {
            attr: getattr(self, attr_names.ATTR_NAME_TO_NORMALIZED[attr])
            for key, _ in dump.items()
            if (attr := cast(attr_names.AttributeName, key))
            in attr_names.ATTR_NAME_TO_NORMALIZED
        }

    def all_attrs(self) -> Mapping[str, object]:
        standard = cast(Mapping[str, object], self.standard_attrs())
        extra = self.extra_attrs()

        return {**standard, **extra}

    @override
    def _eq(self, other: Self) -> bool:
        return (
            self.prefix == other.prefix
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
    def children(self) -> Generator[Element]:
        yield from self.__children

    @property
    def descendants(self) -> Generator[Element]:
        queue = collections.deque(self.children)

        while queue:
            child = queue.popleft()
            yield child

            if isinstance(child, Tag):
                queue.extend(child.children)

    @property
    def next_siblings(self) -> Generator[Element]:
        if self.parent is None:
            return

        should_yield = False

        for sibling in self.parent.children:
            if should_yield:
                yield sibling
            elif sibling is self:
                should_yield = True

    @property
    def prev_siblings(self) -> Generator[Element]:
        if self.parent is None:
            return

        for sibling in self.parent.children:
            if sibling is self:
                return

            yield sibling

    @property
    def siblings(self) -> Generator[Element]:
        yield from self.prev_siblings
        yield from self.next_siblings

    def add_child(
        self, child: Element, /, *, index: int | None = None
    ) -> Self:
        if child is self:
            raise ValueError("Cannot add a tag as a child of itself.")

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

    def add_children(self, *children: Element) -> Self:
        for child in children:
            self.add_child(child)

        return self

    def remove_child(self, child: Element, /) -> Element:
        for i, elem in enumerate(self.children):
            if elem is child:
                return self.pop_child(i)

        raise ValueError("Child not found")

    def pop_child(self, index: SupportsIndex = -1, /) -> Element:
        child = self.__children.pop(index)
        child.parent = None

        return child

    def clear_children(self) -> None:
        for child in self.__children:
            child.parent = None

        self.__children.clear()

    def get_child(self, index: SupportsIndex = -1, /) -> Element:
        return self.__children[index]

    def get_child_index(
        self,
        child: Element,
        /,
        start: SupportsIndex = 0,
        stop: SupportsIndex = sys.maxsize,
    ) -> int:
        return self.__children.index(child, start, stop)

    @override
    def to_beautifulsoup_object(self) -> bs4.Tag:
        tag = bs4.Tag(
            name=tag_name(self),
            can_be_empty_element=True,
            prefix=self.prefix,
            is_xml=True,
        )

        tag.can_be_empty_element = len(self.__children) == 0

        for key, value in self.all_attrs().items():
            tag[key] = serialize.serialize_attr(value)

        for child in self.children:
            tag.append(child.to_beautifulsoup_object())

        if tag_name(self) == "svg":
            formatter = serialize.get_current_formatter()

            if formatter.xmlns == "always":
                tag["xmlns"] = constants.SVG_XMLNS
            elif formatter.xmlns == "never":
                del tag["xmlns"]

        return tag

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

        if utils.is_type(self.transform_origin, Sequence[length.Length]):
            tx = float(self.transform_origin[0])
            ty = float(self.transform_origin[1])

            if not self.transform:
                self.transform = []

            self.transform.insert(0, transform.Translate(tx, ty))
            self.transform.append(transform.Translate(-tx, -ty))

            self.transform_origin = None
        else:
            raise errors.SvgTransformOriginError(self.transform_origin)

    def __reify_this(self, *, limit: int = sys.maxsize) -> None:
        if limit < 0:
            raise ValueError("Limit must be a positive integer")

        self.decompose_transform_origin()

        if not self.transform:
            return

        transform.decompose_matrices(transform=self.transform)

        reified = 0
        i = 0

        while reified < limit and i < len(self.transform):
            if not isinstance(self.transform[i], transform.Reifiable):
                i += 1
                continue

            try:
                # move the transformation to the end of the list where it can
                # be directly applied to the elementf
                _move_transformation_to_end(self.transform, i)
                transformation = self.transform.pop()

                _apply_transformation(self, transformation)

                for child in self.find_all(recursive=False):
                    if child.transform is None:
                        child.transform = []

                    # decompose transform-origin before we prepend
                    child.decompose_transform_origin()
                    child.transform.insert(0, transformation)

                    child.reify(
                        limit=1,
                        recursive=False,
                        remove_transform_list_if_empty=False,
                    )
            except (ValueError, errors.SvgTransformSwapError) as e:
                raise errors.SvgReifyError from e

            reified += 1

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
    def find_all(self, /, *, recursive: bool = True) -> Generator[Tag]: ...

    @overload
    def find_all(
        self, *tags: type[_T_tag], recursive: bool = True
    ) -> Generator[_T_tag]: ...

    @overload
    def find_all(
        self, *tags: type[Tag] | names.TagName, recursive: bool = True
    ) -> Generator[Tag]: ...

    def find_all(
        self, *tags: type[Tag] | names.TagName, recursive: bool = True
    ) -> Generator[Tag]:
        """Find all tags that match the given search criteria.

        Args:
        tags: The tags to search for. Can be tag names or tag classes.
            If no search criteria are provided, all tags are returned.
        recursive: If `False`, only search the direct children of the tag,
        otherwise search all descendants.

        Returns:
        An iterator over all tags that match the search criteria.

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
            if isinstance(child, Tag) and (
                len(tags) == 0
                or any(_match_tag(child, search=tag) for tag in tags)
            ):
                yield child

    @overload
    def find(
        self, *tags: type[_T_tag], recursive: bool = True
    ) -> _T_tag: ...

    @overload
    def find(
        self, *tags: type[Tag] | names.TagName, recursive: bool = True
    ) -> Tag: ...

    @overload
    def find(
        self,
        *tags: type[_T_tag],
        recursive: bool = True,
        default: _T = _EMPTY_PARAM,
    ) -> _T_tag | _T: ...

    @overload
    def find(
        self,
        *tags: type[Tag] | names.TagName,
        recursive: bool = True,
        default: _T = _EMPTY_PARAM,
    ) -> Tag | _T: ...

    def find(
        self,
        *tags: type[Tag] | names.TagName,
        recursive: bool = True,
        default: _T = _EMPTY_PARAM,
    ) -> Tag | _T:
        """Find the first tag that matches the given search criteria.

        Args:
        tags: The tags to search for. Can be tag names or tag classes.
        recursive: If `False`, only search the direct children of the tag,
        otherwise search all descendants.
        default: The default value to return if no tag matches the search
        criteria.

        Returns:
        The first tag that matches the search criteria.

        Raises:
        SvgElementNotFoundError: If no tag matches the search criteria and no
        default value is provided.

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
            return next(self.find_all(*tags, recursive=recursive))
        except StopIteration as e:
            if default is not _EMPTY_PARAM:
                return default

            msg = f"Unable to find tag by search criteria: {tags}"
            raise errors.SvgElementNotFoundError(msg) from e

    @property
    def num_children(self) -> int:
        return len(self.__children)

    def has_children(self) -> bool:
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


def _match_tag(tag: Tag, /, *, search: type[Tag] | names.TagName) -> bool:
    """Check if a tag matches the given search criteria.

    Args:
    tag: The tag to check.
    search: The search criteria. Can be a tag name or a tag class.

    Returns:
    `True` if the tag matches the search criteria, `False` otherwise.

    Examples:
    >>> from svglab import Rect
    >>> rect = Rect()
    >>> _match_tag(rect, search="rect")
    True
    >>> _match_tag(rect, search=Rect)
    True
    >>> _match_tag(rect, search="circle")
    False

    """
    if isinstance(search, type):
        return isinstance(tag, search)

    return tag_name(tag) == search


class TextElement(Element, metaclass=abc.ABCMeta):
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
    def _eq(self, other: Self) -> bool:
        return self.content == other.content

    @override
    def __repr__(self) -> str:
        name = type(self).__name__
        return f"{name}({self.content!r})"
