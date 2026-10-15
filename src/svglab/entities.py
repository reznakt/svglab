"""Abstract base classes for representing common XML entities."""

from __future__ import annotations

import abc
import collections
import functools
import itertools
import operator
import re
import reprlib
import sys
import warnings
from collections.abc import Container, Generator, Iterator, Mapping

import bs4
import pydantic
from typing_extensions import (
    TYPE_CHECKING,
    Any,
    ClassVar,
    Final,
    Literal,
    NamedTuple,
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
from svglab.attrparse.point import Point
from svglab.attrparse.transform import (
    Matrix,
    Transform,
    Translate,
    compose,
)
from svglab.attrs.attrdefs import GradientUnitsAttr, PatternUnitsAttr
from svglab.attrs.attrgroups import CoreAttrs, PresentationAttrs
from svglab.attrs.names import ATTR_NAME_TO_NORMALIZED, AttributeName
from svglab.attrs.typedefs import TransformOrigin
from svglab.constants import SVG_XMLNS
from svglab.elements.names import ELEMENT_NAME_TO_NORMALIZED, ElementName
from svglab.errors import (
    SvgElementNotFoundError,
    SvgTransformOriginError,
    SvgUnitConversionError,
)
from svglab.models import Attr, BaseModel
from svglab.reify import (
    AFFINE,
    NOTHING,
    TRANSLATION,
    UNIFORM_SCALING,
    UNKNOWN,
    UPRIGHT,
    AffineGeometry,
    Animation,
    Capability,
    DocumentFragmentRoot,
    Grouping,
    PercentageDefaults,
    RenderedIndirectly,
    Scope,
    SelectsAChild,
    Stylesheet,
    TransformIgnored,
    TransformInheritedByChildren,
    ViewportEstablishing,
    apply,
    declared_properties,
    features,
    geometry_capability,
    has_own_geometry,
    property_value,
    spell_out_gradient,
    split,
    stretches_content,
    style_capability,
    style_declarations,
    stylesheet_capability,
    stylesheet_declarations,
)
from svglab.serialize import (
    Formatter,
    get_current_formatter,
    serialize_attr,
)
from svglab.utils.bsutils import beautifulsoup_to_str
from svglab.utils.iterutils import search_by_reference, take_last
from svglab.utils.mathutils import is_close
from svglab.utils.miscutils import basic_compare


_T = TypeVar("_T")
_ElementT = TypeVar("_ElementT", bound="Element")
_EntityT = TypeVar("_EntityT", bound="Entity")

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

_ANIMATABLE_BY_REIFICATION: Final[frozenset[str]] = frozenset(
    {
        "transform",
        "gradientTransform",
        "patternTransform",
        "transform-origin",
        "x",
        "y",
        "width",
        "height",
        "r",
        "rx",
        "ry",
        "cx",
        "cy",
        "fx",
        "fy",
        "fr",
        "x1",
        "y1",
        "x2",
        "y2",
        "points",
        "d",
        "dx",
        "dy",
        "font-size",
        "textLength",
        "stroke-width",
        "stroke-dasharray",
        "stroke-dashoffset",
    }
)
"""The attributes reification rewrites, and an animation must keep."""

_RESOURCE_ATTR_NAMES: Final[tuple[AttributeName, ...]] = (
    "fill",
    "stroke",
    "mask",
    "clip-path",
)
"""Attributes that attach a resource drawn in some coordinate system."""


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
        >>> _match_element(rect, search=Element)
        True
        >>> unknown = UnknownElement(element_name="foo")
        >>> _match_element(unknown, search="foo")
        True

    """
    if isinstance(search, type):
        return isinstance(element, search)

    return element_name(element) == search


def _normalize_transform(matrix: Matrix, /) -> Transform | None:
    """Express a matrix in the shortest transform list that serializes it.

    Args:
        matrix: The transformation left over after reification.

    Returns:
        A transform list equivalent to the matrix, or `None` if the matrix is
        the identity and the attribute can be dropped altogether.

    Examples:
        >>> from svglab.attrparse.transform import Matrix, Translate
        >>> _normalize_transform(Matrix.identity()) is None
        True
        >>> _normalize_transform(Translate(10, 20).to_matrix())
        [Translate(tx=10.0, ty=20.0)]

    """
    if matrix == Matrix.identity():
        return None

    return matrix.decompose()


def _attr_or_default(
    element: Element, attr_name: AttributeName, /
) -> object:
    """Read an attribute, falling back to the value the spec says it has.

    Only the attributes whose default matters to the rest of the library are
    filled in; everything else reads as `None` when it is not set.

    Args:
        element: The element to read from.
        attr_name: The name of the attribute.

    Returns:
        The value of the attribute, its default, or `None`.

    """
    name = ATTR_NAME_TO_NORMALIZED[attr_name]

    if name in type(element).model_fields:
        value = getattr(element, name, None)

        if value is not None:
            return value

    match attr_name:
        case (
            "gradientUnits" | "patternUnits" | "maskUnits" | "filterUnits"
        ):
            return "objectBoundingBox"
        case (
            "patternContentUnits"
            | "clipPathUnits"
            | "maskContentUnits"
            | "primitiveUnits"
        ):
            return "userSpaceOnUse"
        case _:
            return None


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
        >>> from svglab import FeGaussianBlur, FontFaceName
        >>> element_name(FeGaussianBlur())
        'feGaussianBlur'
        >>> element_name(FontFaceName())
        'font-face-name'
        >>> element_name(UnknownElement(element_name="foo"))
        'foo'

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
            >>> from svglab import Formatter, G, Rect
            >>> rect = Rect(id="foo", stroke_linecap="round")
            >>> rect.to_xml()
            '<rect id="foo" stroke-linecap="round"/>'
            >>> g = G().add_child(Rect(id="foo"))
            >>> print(g.to_xml())
            <g>
              <rect id="foo"/>
            </g>
            >>> print(g.to_xml(formatter=Formatter(indent=4)))
            <g>
                <rect id="foo"/>
            </g>
            >>> g.to_xml(pretty=False)
            '<g><rect id="foo"/></g>'

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
    if not TYPE_CHECKING:

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

    @override
    def __deepcopy__(self, memo: dict[int, object] | None = None) -> Self:
        """Copy the entity and everything below it, but nothing above it.

        The copy is detached from the tree unless its parent is being copied
        along with it. Pydantic only records a copy in `memo` once it is
        complete, so following the parent link would copy the ancestors all
        over again -- and, through their children, the entity itself.

        Returns:
            The copy.

        """
        memo = {} if memo is None else memo
        parent = self.parent
        blocked = parent is not None and id(parent) not in memo

        # mapping the parent to itself keeps the copy from following the link,
        # and the copy is detached afterwards. a `None` entry would detach it
        # directly, but Python 3.15.0 ignores it
        if blocked:
            memo[id(parent)] = parent

        try:
            copied = super().__deepcopy__(memo)
        finally:
            if blocked:
                del memo[id(parent)]

        if blocked:
            object.__setattr__(copied, "parent", None)

        return copied


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
        default_factory=lambda: []  # ruff: ignore[PIE807]
    )

    @property
    def __children(self) -> list[Entity]:
        # `BaseModel.__getattr__` is an order of magnitude slower than reading
        # the private attribute from its storage
        assert self.__pydantic_private__ is not None, "private attrs unset"
        return self.__pydantic_private__["_children"]

    # region Attribute Handling

    if not TYPE_CHECKING:
        __pydantic_extra__: dict[str, str]

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

            attr = normalized.inverse.get(name)

            if attr is None:
                continue

            # the attribute may have been deleted
            value = getattr(self, name, None)

            if value is not None:
                result[attr] = value

        return result

    def all_attrs(self) -> Mapping[str, object]:
        """Get all attributes of the element.

        This includes both standard and extra attributes.

        Returns:
            A mapping of attribute names to their values. The mapping should
            be considered immutable.

        """
        return {**self.standard_attrs(), **self.extra_attrs()}

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
    # region Copying

    @override
    def __deepcopy__(self, memo: dict[int, object] | None = None) -> Self:
        copied = super().__deepcopy__(memo)

        # each child was copied while this element was still being copied,
        # so it could not be attached to the copy yet; the link is known to be
        # valid, so it skips the validation an assignment would run
        for child in copied.children:
            object.__setattr__(child, "parent", copied)

        return copied

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

    def remove_child(self, child: _EntityT, /) -> _EntityT:
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

        self.pop_child(index)

        return child

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
    def find(self, /, *, recursive: bool = True) -> Element: ...

    @overload
    def find(
        self, /, *, recursive: bool = True, default: _T
    ) -> Element | _T: ...

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
            >>> g.find("circle")
            Traceback (most recent call last):
                ...
            svglab.errors.SvgElementNotFoundError: Unable to find element ...

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
            attr = _attr_or_default(self, attr_name)

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
            Transform | None, _attr_or_default(self, transform_attr_name)
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

        A keyword such as `center` and a percentage are resolved against the
        nearest viewport, as `transform-box: view-box` prescribes for SVG
        elements. The outermost `svg` has a CSS box of its own and turns
        about its center unless told otherwise, so it is treated as if it
        said `transform-origin="50% 50%"`.

        If the `transform-origin` attribute is not set, this function does
        nothing.

        Raises:
            SvgTransformOriginError: If the value of the `transform-origin`
                attribute cannot be decomposed: it has a depth, or it is
                relative to a viewport whose size is not known.
            SvgUnitConversionError: If an offset cannot be converted to user
                units.

        """
        origin = _transform_origin(self)

        if origin is None:
            return

        if not self.main_transform:
            self.main_transform = []

        self.main_transform.insert(0, Translate(origin.x, origin.y))
        self.main_transform.append(Translate(-origin.x, -origin.y))

        self.transform_origin: Attr[TransformOrigin] = None

    # region Reification

    def reify(
        self,
        *,
        recursive: bool = True,
        convert_shapes_to_paths: bool = False,
        unwrap_groups: bool = False,
    ) -> None:
        """Replace transformations with equivalent changes to the geometry.

        This method takes the transformation described by the `transform`
        attribute and folds it into the coordinate, length, and path data
        attributes of the element, so that the element looks the same but no
        longer carries the attribute.

        The whole transform list is composed into a single matrix first, so
        the order of the individual transformation functions does not matter
        and a `matrix(...)` is no harder to reify than a `translate(...)`.

        How much of that matrix an element can take on depends on what its
        attributes are able to describe. A `path` can express any affine
        transformation; a `rect` can be moved, resized and turned by a
        quarter, but not rotated freely; a `text` can only be moved and
        resized, since mirroring it would mean mirroring its glyphs. Whatever
        is left over stays in the `transform` attribute, in the shortest form
        the library can find for it. An element that establishes a coordinate
        system for its children, such as a `g`, hands the transformation to
        them instead of absorbing it.

        Reification never changes the way the document looks. Where that
        cannot be guaranteed -- an element painted by a gradient defined in
        user space, a shape carrying markers, a length given as a percentage
        -- the transformation is left alone.

        Args:
            recursive: If `True`, the method is called recursively on all
                child elements.
            convert_shapes_to_paths: If `True`, a basic shape whose
                transformation cannot otherwise be absorbed is replaced by an
                equivalent `path` element, which can absorb anything. Only
                descendants are replaced; the element the method is called on
                keeps its type.
            unwrap_groups: If `True`, a descendant `g` that is left without
                any attributes once its transformation is gone is replaced by
                its children. Groups that had no attributes to begin with are
                left alone, and so is every group in a document with a
                stylesheet, whose selectors may depend on the tree's shape.

        Raises:
            SvgTransformOriginError: If the value of the `transform-origin`
                attribute is unsupported.

        Examples:
            >>> from svglab import Rect, Length, Rotate, Scale, Translate
            >>> rect = Rect(
            ...     x=Length(10),
            ...     y=Length(20),
            ...     width=Length(20),
            ...     height=Length(40),
            ...     transform=[Translate(5, 5)],
            ... )
            >>> rect.reify()
            >>> rect.x, rect.y
            (Length(value=15.0, unit=None), Length(value=25.0, unit=None))
            >>> rect.transform is None
            True

            Non-uniform scaling is no trouble for a rectangle:

            >>> rect = Rect(width=Length(20), height=Length(10))
            >>> rect.transform = [Scale(2, 3)]
            >>> rect.reify()
            >>> rect.width, rect.height
            (Length(value=40.0, unit=None), Length(value=30.0, unit=None))

            A rotation is, so it stays where it is:

            >>> rect = Rect(width=Length(20), transform=[Rotate(45)])
            >>> rect.reify()
            >>> rect.transform
            [Rotate(angle=45.0, cx=0.0, cy=0.0)]

        """
        _reify_tree(
            self,
            context=_build_context(
                self, convert_shapes_to_paths=convert_shapes_to_paths
            ),
            recursive=recursive,
            unwrap_groups=unwrap_groups,
        )

    # endregion


# Models defer their build, so the forward reference in `Entity.parent` would
# otherwise stay unresolved in every subclass and fail to resolve later in the
# subclass's own module, where `Element` is not in scope.
Entity.model_rebuild()
Element.model_rebuild()


@final
class UnknownElement(RenderedIndirectly, Element):
    """Represents an unknown element that is not part of the SVG specification.

    This element has no standard parsed attributes. All attributes are treated
    as extra attributes.

    If you need to parse custom elements including their attributes, it is
    recommended to subclass the `Element` class instead; this class is only
    intended as a last-resort fallback so we don't lose information about
    elements the library does not know about.

    A renderer draws nothing it does not know, so reification treats an
    unknown element like one that is not drawn where it sits: a
    transformation handed down from above neither reaches it nor is held up
    by it.
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


# region Reification


class _Context(NamedTuple):
    """What the reification of one tree needs to know about the whole of it."""

    by_id: Mapping[str, Element]
    """The elements of the tree, keyed by their `id` attribute."""

    pinned: Container[int]
    """Elements no transformation may be pushed into, by object identity.

    An element that something else in the document refers to renders wherever
    the reference is, not where it sits in the tree, so handing it a
    transformation from an ancestor would change what the reference sees.
    Everything on the way down to it is off limits for the same reason.
    """

    frozen: Container[int]
    """Elements that may not be reified at all, by object identity.

    An animation records the values of an attribute in the coordinate system
    the document was written in; rewriting that system underneath it would
    move the animation, not the element.
    """

    scopes: Mapping[int, Scope]
    """How far each element's inherited properties can be seen."""

    capabilities: Mapping[int, Capability]
    """What each element of the tree can absorb, by object identity."""

    stylesheet: Capability
    """What the document's stylesheets leave reifiable anywhere in it."""

    paint_servers: Mapping[str, Capability]
    """What a shape whose `fill` or `stroke` cannot be told may absorb.

    The least any paint server named by a `fill`, or by a `stroke`, anywhere
    in the document allows.
    """

    markers: bool
    """Whether the document has any `marker` to put on a shape."""

    convert_shapes: bool
    """Whether a basic shape may be replaced by the `path` it draws."""

    pushed: set[int]
    """Elements handed a transformation by their parent during this pass."""


def _resolve_reference(
    element: Element,
    attr_name: AttributeName,
    index: Mapping[str, Element],
    /,
    *,
    warn: bool = False,
) -> Element | None:
    """Follow a local IRI reference to the element it points at.

    A reference that resolves to nothing renders as nothing, so reification
    treats it as no reference at all.

    Returns:
        The element referred to, or `None` if the attribute is not a local
        reference or nothing in the index has its id.

    """
    attr = _attr_or_default(element, attr_name)

    if not (isinstance(attr, Iri) and attr.is_local):
        return None

    assert attr.fragment is not None
    target = index.get(attr.fragment)

    if target is None and warn:
        warnings.warn(
            f"Dangling IRI reference {attr_name}={attr.serialize()!r}",
            stacklevel=2,
        )

    return target


def _paint_server_attr(
    target: Element,
    attr_name: AttributeName,
    index: Mapping[str, Element],
    /,
) -> object:
    """Read an attribute of a gradient or pattern, following its `href`.

    A gradient or pattern takes every attribute it leaves out from the one
    it refers to, which may in turn refer to another.

    Returns:
        The value of the attribute, or its default.

    """
    seen: set[int] = set()
    element: Element | None = target

    while element is not None and id(element) not in seen:
        seen.add(id(element))
        attrs = element.standard_attrs()

        if attr_name in attrs:
            return attrs[attr_name]

        element = _paint_server_template(element, index)

    return _attr_or_default(target, attr_name)


def _paint_server_template(
    element: Element, index: Mapping[str, Element], /
) -> Element | None:
    """Find the gradient or pattern the element inherits attributes from."""
    if not isinstance(element, PatternUnitsAttr | GradientUnitsAttr):
        return None

    for attr_name in ("href", "xlink:href"):
        template = _resolve_reference(element, attr_name, index)

        if isinstance(template, PatternUnitsAttr | GradientUnitsAttr):
            return template

    return None


def _pattern_transform_capability(
    target: Element, index: Mapping[str, Element], /
) -> Capability:
    """Work out what survives a pattern's own `patternTransform`.

    The tiling is laid out in the bounding box of the element and the pattern
    transform is applied to the result, in user space. Reification rewrites
    the bounding box, which happens *before* the pattern transform, so the
    picture only survives if doing the absorbed part first comes to the same
    thing as doing it last -- that is, if the two commute.

    Moving the tiling commutes with moving the element. A pattern transform
    that only turns or stretches the tiling commutes with resizing the
    element about the origin, which is the one resizing that leaves the
    corner of the box where it is. Nothing else is safe.

    Returns:
        What a shape painted with the pattern may absorb.

    """
    pattern_transform = _paint_server_attr(
        target, "patternTransform", index
    )
    matrix = compose(cast("Transform | None", pattern_transform) or [])
    identity = Matrix.identity()

    if matrix == identity:
        return AFFINE

    if matrix.linear() == identity:
        return TRANSLATION

    if matrix.translation() == Translate(0, 0):
        return UNIFORM_SCALING - TRANSLATION

    return NOTHING


def _pattern_capability(
    target: Element, index: Mapping[str, Element], /
) -> Capability:
    """Work out what a pattern lets the element it paints absorb.

    The tile is placed relative to the bounding box, so it moves and resizes
    with the element. The content inside the tile only follows as far as its
    own coordinate system does: a `viewBox` maps it onto the tile, and
    `patternContentUnits` can tie it to the bounding box, but by default it is
    drawn at its natural size in user space and only the tiling changes.

    Whatever the tile allows is then narrowed by the pattern's own
    `patternTransform`, which the tiling has to keep in step with.

    Returns:
        What a shape painted with the pattern may absorb.

    """
    if (
        _paint_server_attr(target, "patternUnits", index)
        != "objectBoundingBox"
    ):
        return NOTHING

    return _pattern_tile_capability(
        target, index
    ) & _pattern_transform_capability(target, index)


def _pattern_tile_capability(
    target: Element, index: Mapping[str, Element], /
) -> Capability:
    """Work out how far the content of a pattern follows its tile."""
    if _paint_server_attr(target, "viewBox", index) is not None:
        return (
            UPRIGHT
            if stretches_content(
                _paint_server_attr(target, "preserveAspectRatio", index)
            )
            else UNIFORM_SCALING
        )

    if (
        _paint_server_attr(target, "patternContentUnits", index)
        == "objectBoundingBox"
    ):
        return UPRIGHT

    return TRANSLATION


def _paint_server_capability(
    target: Element, index: Mapping[str, Element], /
) -> Capability:
    """Work out what a paint server lets the element it paints absorb."""
    if isinstance(target, PatternUnitsAttr):
        return _pattern_capability(target, index)

    if isinstance(target, GradientUnitsAttr):
        # a gradient is a ramp across whatever space it is defined in, so it
        # is carried along by anything that leaves the box upright
        units = _paint_server_attr(target, "gradientUnits", index)

        return UPRIGHT if units == "objectBoundingBox" else NOTHING

    # not a paint server at all; nothing to keep in step with
    return AFFINE


def _resource_capability(
    target: Element, attr_name: AttributeName, /
) -> Capability:
    """Work out what a referenced resource lets the element absorb.

    A resource described as a fraction of the box of whatever refers to it
    follows that element wherever reification puts it -- but only as far as
    moving and resizing go, since turning or flipping the element would have
    turned or flipped the resource too, and rewriting a box cannot say that.
    A resource expressed in user space follows nowhere: it is resolved in the
    coordinate system the referencing element renders in, which is exactly
    what reification takes away.

    Returns:
        What an element referring to the resource may absorb.

    """
    match attr_name:
        case "clip-path":
            units = _attr_or_default(target, "clipPathUnits")
        case _:
            # a mask's region and its content have separate unit settings,
            # and both have to follow the box for the mask to move with the
            # element
            units = (
                _attr_or_default(target, "maskUnits")
                if _attr_or_default(target, "maskContentUnits")
                == "objectBoundingBox"
                else "userSpaceOnUse"
            )

    return UPRIGHT if units == "objectBoundingBox" else NOTHING


_URL_FRAGMENT: Final = re.compile(r"url\(\s*['\"]?#([^'\")\s]+)")


def _reference_capability(
    element: Element, /, *, context: _Context, scope: Scope
) -> Capability:
    """Work out what the element's references let it absorb.

    The paint and the markers are inherited, so they are resolved the way the
    element is rendered -- and where they cannot be resolved, the element is
    held to the worst any paint server or marker in the document could do.

    Returns:
        What the element may absorb.

    """
    capability = AFFINE

    for name in ("fill", "stroke"):
        paint = property_value(element, name, scope=scope)

        if paint is UNKNOWN:
            capability &= context.paint_servers[name]
            continue

        target = _paint_target(paint, context.by_id)

        if target is not None:
            capability &= _paint_server_capability(target, context.by_id)
        elif isinstance(paint, str) and "url(" in paint:
            # a paint server reification cannot find, declared in a style
            capability &= NOTHING

    if isinstance(element, AffineGeometry):
        # a marker is placed in user space and oriented along the path, so
        # anything but a move changes its size or its angle
        for name in _MARKER_ATTRS:
            marker = property_value(element, name, scope=scope)

            if marker is UNKNOWN:
                if context.markers:
                    capability &= TRANSLATION
            elif marker is not None and marker != "none":
                capability &= TRANSLATION

    for attr_name in ("mask", "clip-path"):
        target = _resolve_reference(
            element, attr_name, context.by_id, warn=True
        )

        if target is not None:
            capability &= _resource_capability(target, attr_name)

    filter_ = _resolve_reference(element, "filter", context.by_id)

    if filter_ is not None:
        capability &= _filter_capability(filter_)

    return capability


_MARKER_ATTRS: Final = (
    "marker",
    "marker_start",
    "marker_mid",
    "marker_end",
)
"""The marker properties, shorthand included."""


def _filter_capability(target: Element, /) -> Capability:
    """Work out what a filter lets the element it is attached to absorb."""
    if _attr_or_default(target, "filterUnits") != "objectBoundingBox":
        # the filter region is pinned to the coordinate system the element
        # renders in, so moving the element would leave the region behind
        return NOTHING

    if _attr_or_default(
        target, "primitiveUnits"
    ) == "userSpaceOnUse" and any(
        element_name(primitive) == "feTurbulence"
        or any(
            _attr_or_default(primitive, name) is not None
            for name in _PRIMITIVE_POSITION_ATTRS
        )
        for primitive in target.find_all()
    ):
        # a primitive placed at a point of the user space, or noise sampled
        # from it, stays where it is when the element moves out from under it
        return NOTHING

    # the region follows the bounding box, but the primitives are
    # parametrized in user space, so the element may only move
    return TRANSLATION


_PRIMITIVE_POSITION_ATTRS: Final[tuple[AttributeName, ...]] = (
    "x",
    "y",
    "pointsAtX",
    "pointsAtY",
)
"""Attributes that place a filter primitive, or its light, in user space."""


def _is_outermost_viewport(element: Element, /) -> bool:
    return (
        isinstance(element, DocumentFragmentRoot)
        and element.parent is None
    )


def _pushes_transform_to_children(element: Element, /) -> bool:
    """Check whether the children inherit the element's coordinate system.

    When they do, a transformation on the element is equivalent to the same
    transformation on each of its children, which is what lets reification
    carry one down the tree to elements that can absorb it.

    Returns:
        `True` if a transformation on the element may be handed down to
        its children.

    """
    if _attr_or_default(element, "clipPathUnits") == "objectBoundingBox":
        # the content is drawn in the bounding box of whatever the clip path
        # is applied to, and the transformation is applied on top of that
        # mapping, so it cannot be handed down past it
        return False

    return isinstance(
        element, TransformInheritedByChildren
    ) or _is_outermost_viewport(element)


def _delegates_transform(element: Element, /) -> bool:
    """Check whether the transformation belongs entirely to the children.

    A `g` has no geometry of its own, so there is nothing to fold a
    transformation into -- handing it to the children is the whole of the
    work. The outermost `svg` is in the same position: its `x`, `y`, `width`
    and `height` describe the canvas rather than anything drawn on it, so its
    transformation applies to its content.

    Returns:
        `True` if the element has nothing of its own to fold a
        transformation into.

    """
    return _pushes_transform_to_children(element) and (
        _is_outermost_viewport(element) or not has_own_geometry(element)
    )


def _children_inheriting_transform(element: Element, /) -> list[Element]:
    """List the children a transformation would have to be handed to."""
    return [
        child
        for child in element.find_all(recursive=False)
        if not isinstance(child, RenderedIndirectly)
    ]


_HORIZONTAL_KEYWORDS: Final = {"left": 0.0, "center": 50.0, "right": 100.0}
_VERTICAL_KEYWORDS: Final = {"top": 0.0, "center": 50.0, "bottom": 100.0}
_CSS_INITIAL_ORIGIN: Final = (Length(50, "%"), Length(50, "%"))


def _transform_origin(element: Element, /) -> Point | None:
    """Resolve the point the element's `transform-origin` turns about.

    The outermost `svg` with a transformation has one even when it says
    nothing: a CSS box turns about its center.

    Returns:
        The origin, or `None` when the element has none to speak of.

    Raises:
        SvgTransformOriginError: If the origin has a depth, names a side
            that cannot be told apart from the other axis, or is relative to
            a viewport whose size is not known.
        SvgUnitConversionError: If an offset cannot be converted.

    """
    origin = _attr_or_default(element, "transform-origin")

    if origin is None:
        if not (
            _is_outermost_viewport(element) and element.main_transform
        ):
            return None

        origin = _CSS_INITIAL_ORIGIN

    match origin:
        case (first, second):
            pass
        case (first, second, depth):
            if not (
                isinstance(depth, Length) and is_close(float(depth), 0)
            ):
                raise SvgTransformOriginError(origin)
        case "top" | "bottom":
            first, second = "center", origin
        case _:
            first, second = origin, "center"

    if first in {"top", "bottom"} or second in {"left", "right"}:
        # two keywords may be written in either order
        first, second = second, first

    offsets: list[float] = []

    for value, keywords, axis in (
        (first, _HORIZONTAL_KEYWORDS, 0),
        (second, _VERTICAL_KEYWORDS, 1),
    ):
        if isinstance(value, str):
            if value not in keywords:
                raise SvgTransformOriginError(origin)

            value = Length(keywords[value], "%")  # ruff: ignore[PLW2901]

        if not isinstance(value, Length):
            raise SvgTransformOriginError(origin)

        if value.unit == "%":
            # `transform-box` is `view-box` for SVG elements, so a percentage
            # is of the nearest viewport
            viewport = _viewport_size(element)

            if viewport is None:
                raise SvgTransformOriginError(origin)

            offsets.append(value.value / 100 * viewport[axis])
        else:
            offsets.append(float(value))

    return Point(*offsets)


def _viewport_size(element: Element, /) -> tuple[float, float] | None:
    """Measure the viewport the element's percentages are resolved against.

    The nearest viewport is the one established by the closest ancestor
    that establishes one; for the outermost `svg` it is its own. Its size is
    that of its `viewBox`, or for an `svg` without one, its `width` and
    `height`.

    Returns:
        The width and height of the viewport, or `None` if they are not
        known.

    """
    start = element if _is_outermost_viewport(element) else element.parent

    if start is None:
        return None

    for candidate in itertools.chain([start], start.ancestors):
        if not isinstance(candidate, ViewportEstablishing):
            continue

        view_box = _attr_or_default(candidate, "viewBox")

        if isinstance(view_box, tuple):
            _, _, width, height = cast("tuple[float, ...]", view_box)
            return width, height

        if element_name(candidate) != "svg":
            return None

        width = _attr_or_default(candidate, "width")
        height = _attr_or_default(candidate, "height")

        try:
            if isinstance(width, Length) and isinstance(height, Length):
                return float(width), float(height)
        except SvgUnitConversionError:
            return None

        return None

    return None


def _has_unusable_transform_origin(element: Element, /) -> bool:
    """Check whether `transform-origin` keeps the element where it is.

    An element whose origin cannot be taken apart cannot have its
    transformation reified, nor be handed one by its parent. An origin on an
    element with no transformation does nothing at all, and is simply dropped
    when a transformation arrives.

    Returns:
        `True` if the element's transformation has to stay where it is.

    """
    if not element.main_transform:
        return False

    try:
        _transform_origin(element)
    except (SvgTransformOriginError, SvgUnitConversionError):
        return True

    return False


def _is_convertible_shape(
    element: Element, /, *, context: _Context
) -> bool:
    """Check whether the element may be replaced by the path it draws."""
    to_path_data = getattr(element, "to_path_data", None)

    if (
        not context.convert_shapes
        or to_path_data is None
        or id(element) in context.frozen
    ):
        # an animation of the shape's own attributes would have nothing left
        # to animate on a path
        return False

    try:
        to_path_data()
    except SvgUnitConversionError:
        # a shape sized in percentages has no path equivalent that does not
        # need to know the viewport
        return False

    return True


def _element_capability(
    element: Element,
    /,
    *,
    context: _Context,
    children: Mapping[int, Capability],
) -> Capability:
    """Work out how much of a transformation an element can take on.

    `children` holds the capability of every element below this one, so that
    the whole tree is worked out from the leaves upwards in a single pass.

    Returns:
        What the element may absorb.

    """
    if id(element) in context.frozen or _has_unusable_transform_origin(
        element
    ):
        return NOTHING

    inheriting = _children_inheriting_transform(element)

    if _pushes_transform_to_children(element) and any(
        id(child) in context.pinned or id(child) in context.frozen
        for child in inheriting
    ):
        # a child that something else in the document points at has to keep
        # rendering the way it does now, so nothing may be pushed into it --
        # and pushing to only some of the children would tear the group apart
        return NOTHING

    scope = context.scopes[id(element)]

    if _delegates_transform(element):
        # the element has no geometry of its own, but what it refers to is
        # still resolved where it sits: a clip path, a mask or a filter in
        # user space stays behind when the transformation moves down to the
        # children, and the content slides out from under it
        capability = (
            _reference_capability(element, context=context, scope=scope)
            & style_capability(element)
            & context.stylesheet
        )

        # handing the transformation to the children is the rest of the
        # work, so the element can take on exactly as much as all of them
        # can. Handing them more only writes the leftover onto every one of
        # them, where it started out written once
        for child in inheriting:
            capability &= children[id(child)]

        return capability

    capability = (
        geometry_capability(
            element,
            scope=scope,
            as_path=_is_convertible_shape(element, context=context),
        )
        & _reference_capability(element, context=context, scope=scope)
        & context.stylesheet
    )

    if not _pushes_transform_to_children(element):
        return capability

    # the element draws content of its own *and* establishes the coordinate
    # system its children draw in. Inherited properties -- `font-size`, the
    # stroke -- are folded into its own attributes, so a child that kept the
    # transformation instead of absorbing it would have the inherited part
    # applied to it twice
    for child in inheriting:
        if child.main_transform:
            return NOTHING

        capability &= children[id(child)]

    return capability


def _capabilities(
    root: Element, /, *, context: _Context
) -> dict[int, Capability]:
    """Work out what every element of a tree can absorb, leaves first.

    A container can only take on what its children can, so the tree has to be
    read from the bottom up. Doing that once here keeps it linear, and keeps
    the depth of the document out of the call stack.

    Returns:
        What every element may absorb, by object identity.

    """
    order: list[Element] = []
    stack = collections.deque([root])

    while stack:
        element = stack.pop()
        order.append(element)
        stack.extend(element.find_all(recursive=False))

    capabilities: dict[int, Capability] = {}

    # a parent always comes before its children in the order above, so
    # reversing it puts every child before its parent
    for element in reversed(order):
        capabilities[id(element)] = _element_capability(
            element, context=context, children=capabilities
        )

    return capabilities


def _reify_element(
    element: Element, /, *, context: _Context, as_descendant: bool = True
) -> Element:
    """Fold as much of the element's transformation into it as will go.

    A basic shape that is asked to absorb more than its attributes can
    express is replaced by the `path` drawing the same shape, which absorbs
    anything -- unless it is the element reification was called on, which
    keeps its type.

    Returns:
        The element, or the `path` that replaced it.

    """
    if id(element) in context.frozen:
        return element

    if (
        isinstance(element, TransformIgnored)
        and id(element) not in context.pushed
    ):
        # renderers ignore the attribute, so it is left as written
        return element

    identity = Matrix.identity()

    if (
        not element.main_transform
        or compose(element.main_transform) == identity
    ):
        # the list does nothing, about any origin, so the attribute can go
        element.main_transform = None
        return element

    written = list(element.main_transform), element.transform_origin

    try:
        element.decompose_transform_origin()
    except (SvgTransformOriginError, SvgUnitConversionError):
        # the origin is a keyword or a percentage of a box reification
        # cannot see, so the transformation has to stay where it is
        return element

    matrix = compose(element.main_transform)
    scope = context.scopes[id(element)]
    convertible = as_descendant and _is_convertible_shape(
        element, context=context
    )
    capability = (
        context.capabilities[id(element)]
        if convertible
        or not _is_convertible_shape(element, context=context)
        # the element reification was called on keeps its type, so it is
        # judged as the shape it is rather than the path it could become
        else _element_capability(
            element, context=context, children=context.capabilities
        )
    )
    residue, absorbed = split(matrix, capability)

    if absorbed == identity:
        # nothing was folded in; the list is left exactly as written, with
        # the origin it was written with
        if written[1] is not None or element.main_transform != written[0]:
            element.main_transform, element.transform_origin = written

        return element

    if has_own_geometry(element) and not _delegates_transform(element):
        if convertible and not features(absorbed) <= geometry_capability(
            element, scope=scope
        ):
            element = _convert_to_path(element)

        # a span was handed the transformation by a text that resized the
        # magnitudes it inherits already
        apply(
            element,
            absorbed,
            scope=scope,
            inherited_resized=id(element) in context.pushed
            and has_own_geometry(cast(Element, element.parent)),
        )

    if _pushes_transform_to_children(element):
        # the children are placed in the coordinate system the element
        # establishes, so they have to be given back what was taken out of it
        for child in _children_inheriting_transform(element):
            if child.main_transform and not isinstance(
                child, TransformIgnored
            ):
                child.decompose_transform_origin()
            else:
                # an origin without a transformation did nothing, and must
                # not start doing something now; a transformation renderers
                # ignore did nothing either
                child.transform_origin = None
                child.main_transform = []

            child.main_transform.insert(0, absorbed)
            context.pushed.add(id(child))

    element.main_transform = _normalize_transform(residue)

    if element.main_transform and _is_outermost_viewport(element):
        # the residue was worked out about the origin, and an outermost svg
        # left to its own devices would turn about its center instead
        element.transform_origin = (Length(0), Length(0))

    return element


def _convert_to_path(shape: Element, /) -> Element:
    """Replace a basic shape with the `path` drawing the same shape."""
    parent = shape.parent
    assert parent is not None

    path = cast(Element, cast("Any", shape).to_path())
    position = parent.get_child_index(shape)

    parent.pop_child(position)
    parent.add_child(path, index=position)

    return path


def _reify_tree(
    element: Element,
    /,
    *,
    context: _Context,
    recursive: bool,
    unwrap_groups: bool,
) -> None:
    """Reify an element and, if asked, everything below it.

    The walk keeps its own stack: an SVG can be nested arbitrarily deeply and
    a recursive walk would run out of Python frames long before the document
    runs out of elements.
    """
    _reify_element(element, context=context, as_descendant=False)

    # each entry is a parent whose children still have to be visited
    pending: list[Element] = [element]
    # groups whose transformation was taken off in full, parents first
    emptied: list[Element] = []

    while pending:
        parent = pending.pop()

        for child in list(parent.find_all(recursive=False)):
            if not recursive and id(child) not in context.pushed:
                # only what the element handed down is followed up, since
                # leaving that half done would leave the picture changed
                continue

            grouping = (
                unwrap_groups
                and isinstance(child, Grouping)
                and child.main_transform is not None
            )
            reified = _reify_element(child, context=context)
            pending.append(reified)

            if grouping and reified.main_transform is None:
                emptied.append(reified)

    if emptied and not _has_stylesheet(element.get_root()):
        # children first, so that each group is spliced into a parent that is
        # still where it was
        for group in reversed(emptied):
            if _is_bare_group(group):
                _unwrap(group)


def _has_stylesheet(root: Element, /) -> bool:
    return any(
        isinstance(element, Stylesheet)
        for element in itertools.chain([root], root.find_all())
    )


def _is_bare_group(group: Element, /) -> bool:
    """Check that lifting the group's children would not change a thing."""
    return (
        group.parent is not None
        and not isinstance(group.parent, SelectsAChild)
        and not group.all_attrs()
    )


def _unwrap(group: Element, /) -> None:
    """Put the group's children where the group is."""
    parent = group.parent
    assert parent is not None

    index = parent.get_child_index(group)
    parent.pop_child(index)

    while group.has_children():
        parent.add_child(group.pop_child(), index=index)


def _index_by_id(root: Element, /) -> Mapping[str, Element]:
    """Index the elements of a tree by their `id` attribute."""
    index: dict[str, Element] = {}

    for element in itertools.chain([root], root.find_all()):
        if element.id is not None:
            index.setdefault(element.id, element)

    return index


def _animation_target(
    animation: Element, index: Mapping[str, Element], /
) -> Element | None:
    """Find the element an animation animates.

    An animation acts on the element it references, or on its parent when it
    references none.

    Returns:
        The animated element, or `None` for a detached animation that
        references nothing.

    """
    for attr_name in ("href", "xlink:href"):
        target = _resolve_reference(animation, attr_name, index)

        if target is not None:
            return target

    return animation.parent


def _frozen_elements(
    root: Element, index: Mapping[str, Element], /
) -> Container[int]:
    """Find the elements an animation pins to the coordinates they are in.

    An animation records values of an attribute in the coordinate system the
    document was written in. Reification rewrites that system, so an animated
    attribute it would touch has to be left exactly where it is -- and so
    does the element carrying it.

    A gradient or pattern that refers to another inherits every attribute it
    leaves out, its transformation included, and even an identity
    transformation of its own overrides the inherited one. Both ends of such
    a reference are left as written.

    Returns:
        The `id()`s of the elements.

    """
    frozen: set[int] = set()

    for element in itertools.chain([root], root.find_all()):
        template = _paint_server_template(element, index)

        if template is not None:
            frozen.update((id(element), id(template)))

        if not isinstance(element, Animation):
            continue

        attr_name = _attr_or_default(element, "attributeName")

        if (
            element_name(element) != "animateTransform"
            and attr_name not in _ANIMATABLE_BY_REIFICATION
        ):
            continue

        target = _animation_target(element, index)

        if target is not None:
            frozen.add(id(target))

    return frozen


def _pinned_elements(
    root: Element, index: Mapping[str, Element], frozen: Container[int], /
) -> Container[int]:
    """Find the elements no transformation may be pushed into.

    An element that something else in the document refers to renders wherever
    the reference is, not where it sits in the tree. Handing it a
    transformation from an ancestor would change what the reference sees, so
    it -- and everything on the way down to it -- is off limits. So is an
    element whose transformation an animation replaces.

    Returns:
        The `id()`s of the elements.

    """
    pinned: set[int] = set()

    for target in _referenced_elements(root, index, frozen):
        pinned.add(id(target))
        pinned.update(id(ancestor) for ancestor in target.ancestors)

    return pinned


def _referenced_elements(
    root: Element, index: Mapping[str, Element], frozen: Container[int], /
) -> Iterator[Element]:
    """Find the elements that are seen with their own transformation.

    An element that something else in the document refers to renders there
    with its own transformation, and one an animation targets has its
    transformation replaced over time.

    Yields:
        The elements, possibly more than once.

    """
    for element in itertools.chain([root], root.find_all()):
        if id(element) in frozen:
            yield element

        for attr_name in (*_REFERENCE_ATTR_NAMES, "filter"):
            target = _resolve_reference(element, attr_name, index)

            if target is not None:
                yield target


def referenced_elements(root: Element, /) -> Container[int]:
    """Find the elements whose own transformation is seen somewhere else.

    Prepending to the `transform` of such an element does not only move what
    is drawn where it sits: a `use` referencing it would see the prepended
    transformation as well, and an animation of it would discard it.

    Args:
        root: The root of the document to search.

    Returns:
        The `id()`s of the elements.

    """
    index = _index_by_id(root)
    frozen = _frozen_elements(root, index)

    return {
        id(target) for target in _referenced_elements(root, index, frozen)
    }


def _stylesheets(root: Element, /) -> Iterator[str]:
    """Read the text of every stylesheet in the document."""
    for element in itertools.chain([root], root.find_all()):
        if isinstance(element, Stylesheet):
            yield "".join(
                child.content
                for child in element.children
                if isinstance(child, CharacterData)
            )


def _declared_properties(root: Element, /) -> frozenset[str]:
    """List every attribute and property the document declares anywhere."""
    declared: set[str] = set()

    for element in itertools.chain([root], root.find_all()):
        declared.update(element.all_attrs())
        declared.update(style_declarations(element))

    for css in _stylesheets(root):
        declared.update(declared_properties(css))

    return frozenset(declared)


def _scopes(
    root: Element, index: Mapping[str, Element], /
) -> Mapping[int, Scope]:
    """Work out how far each element's inherited properties can be seen.

    An element a `use` refers to is also rendered with whatever the `use`
    passes down, so inheritance stops being known at it, for it and for
    everything below it. `feImage` renders what it refers to the same way.

    Returns:
        The scope of every element, by object identity.

    """
    boundaries: set[int] = set()

    for element in itertools.chain([root], root.find_all()):
        if element_name(element) in {"use", "feImage"}:
            for attr_name in ("href", "xlink:href"):
                target = _resolve_reference(element, attr_name, index)

                if target is not None:
                    boundaries.add(id(target))

    declared = _declared_properties(root)
    styled = frozenset().union(
        *map(declared_properties, _stylesheets(root))
    )
    scopes: dict[int, Scope] = {}
    stack: list[tuple[Element, Scope]] = [
        (root, Scope(None, declared, styled))
    ]

    while stack:
        element, scope = stack.pop()

        if id(element) in boundaries:
            scope = scope._replace(boundary=element)

        scopes[id(element)] = scope
        stack.extend(
            (child, scope) for child in element.find_all(recursive=False)
        )

    return scopes


def _paint_servers_capability(
    root: Element, index: Mapping[str, Element], /
) -> Mapping[str, Capability]:
    """Work out the least the paint servers named by fills, or strokes, allow.

    Returns:
        The capability for a `fill` and for a `stroke` that cannot be told.

    """
    capabilities: dict[str, Capability] = {
        "fill": AFFINE,
        "stroke": AFFINE,
    }
    declarations: list[tuple[str, object]] = []

    for element in itertools.chain([root], root.find_all()):
        declarations.extend(
            (name, _attr_or_default(element, name))
            for name in ("fill", "stroke")
        )
        declarations.extend(style_declarations(element).items())

    for css in _stylesheets(root):
        declarations.extend(stylesheet_declarations(css))

    for name, value in declarations:
        if name not in capabilities:
            continue

        target = _paint_target(value, index)

        if target is not None:
            capabilities[name] &= _paint_server_capability(target, index)
        elif isinstance(value, str) and "url(" in value:
            capabilities[name] = NOTHING

    return capabilities


def _paint_target(
    paint: object, index: Mapping[str, Element], /
) -> Element | None:
    """Find the element a paint names, if it names one in this document.

    Returns:
        The paint server, or `None`.

    """
    if isinstance(paint, Iri) and paint.is_local:
        assert paint.fragment is not None
        return index.get(paint.fragment)

    if isinstance(paint, str):
        # declared in a `style` or a stylesheet, so it survives as the
        # string it was written as
        match = _URL_FRAGMENT.search(paint)

        if match is not None:
            return index.get(match.group(1))

    return None


def _spell_out_gradients(
    root: Element, subject: Element, frozen: Container[int], /
) -> None:
    """Write out the geometry of every gradient about to be reified.

    A gradient's coordinates default to percentages, which say nothing a
    transformation could be folded into until they are written out as
    fractions of the box, or of the viewport, they refer to.

    In user space a percentage is of the viewport of whatever is painted
    with the gradient, which may be a different one for every shape, so it
    is only written out when the document has a single viewport.
    """
    viewport = (
        _viewport_size(root)
        if not any(
            isinstance(element, ViewportEstablishing)
            and element_name(element) not in {"image", "foreignObject"}
            for element in root.find_all()
        )
        else None
    )

    for element in itertools.chain([subject], subject.find_all()):
        if (
            isinstance(element, PercentageDefaults)
            and element.main_transform
            and id(element) not in frozen
        ):
            spell_out_gradient(element, viewport=viewport)


def _build_context(
    subject: Element, /, *, convert_shapes_to_paths: bool
) -> _Context:
    """Gather what reifying part of a tree needs to know about all of it.

    Returns:
        The context for reifying `subject` and everything below it.

    """
    root = subject.get_root()
    index = _index_by_id(root)
    frozen = _frozen_elements(root, index)

    _spell_out_gradients(root, subject, frozen)

    context = _Context(
        by_id=index,
        pinned=_pinned_elements(root, index, frozen),
        frozen=frozen,
        scopes=_scopes(root, index),
        capabilities={},
        stylesheet=functools.reduce(
            operator.and_,
            map(stylesheet_capability, _stylesheets(root)),
            AFFINE,
        ),
        paint_servers=_paint_servers_capability(root, index),
        markers=any(
            element_name(element) == "marker"
            for element in itertools.chain([root], root.find_all())
        ),
        # a selector may pick a shape out by its name, which a path no
        # longer answers to
        convert_shapes=convert_shapes_to_paths
        and not _has_stylesheet(root),
        pushed=set(),
    )

    return context._replace(
        capabilities=_capabilities(root, context=context)
    )


# endregion
