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
import itertools
import reprlib
import sys
import warnings
from collections.abc import Container, Generator, Mapping

import bs4
import pydantic
from typing_extensions import (
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

from svglab import constants, errors, models, reify, serialize
from svglab.attrparse import iri, length, transform
from svglab.attrs import attrdefs, attrgroups
from svglab.attrs import names as attr_names
from svglab.elements import names
from svglab.utils import bsutils, iterutils, miscutils


_T = TypeVar("_T")
_ElementT = TypeVar("_ElementT", bound="Element")

_EMPTY_PARAM: Final = object()
"""A sentinel value for an empty parameter."""

_REFERENCE_ATTR_NAMES: Final[tuple[attr_names.AttributeName, ...]] = (
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

_RESOURCE_ATTR_NAMES: Final[tuple[attr_names.AttributeName, ...]] = (
    "fill",
    "stroke",
    "mask",
    "clip-path",
)
"""Attributes that attach a resource drawn in some coordinate system."""


def _match_element(
    element: Element, /, *, search: type[Element] | names.ElementName | str
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


def _normalize_transform(
    matrix: transform.Matrix, /
) -> transform.Transform | None:
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
    if matrix == transform.Matrix.identity():
        return None

    return matrix.decompose()


def _attr_or_default(
    element: Element, attr_name: attr_names.AttributeName, /
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
    attrs = element.standard_attrs()

    if attr_name in attrs:
        return attrs[attr_name]

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

    """
    if isinstance(element, UnknownElement):
        return element.element_name

    return names.ELEMENT_NAME_TO_NORMALIZED.inverse[type(element).__name__]


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
        if not miscutils.basic_compare(other, self=self):
            return False

        return self._eq(other)

    @override
    def __hash__(self) -> int:
        return self._hash()


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
                lambda name: (
                    attr_names.ATTR_NAME_TO_NORMALIZED.inverse.get(
                        name, name
                    )
                )
            ),
        ),
    )

    prefix: str | None = None

    # a lambda is faster with pydantic than `list`
    __children: list[Entity] = pydantic.PrivateAttr(
        default_factory=lambda: []  # noqa: PIE807
    )

    # region Attribute Handling

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
        # `model_dump()` would walk the ancestor chain via `parent`
        extra = self.model_extra or {}
        fields = type(self).model_fields
        normalized = attr_names.ATTR_NAME_TO_NORMALIZED
        result: dict[attr_names.AttributeName, object] = {}

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
                result[cast(attr_names.AttributeName, attr)] = value

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
        return iterutils.take_last(self.ancestors) or self

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
        try:
            index = iterutils.search_by_reference(self.__children, child)
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
        *elements: type[Element] | names.ElementName | str,
        recursive: bool = True,
    ) -> Generator[Element]: ...

    def find_all(
        self,
        *elements: type[Element] | names.ElementName | str,
        recursive: bool = True,
    ) -> Generator[Element]:
        """Find all elements that match the given search criteria.

        Args:
            elements: The elements to search for. Can be element names or
                element classes.  If no search criteria are provided, all
                elements are returned.
            recursive: If `False`, only search the direct children of the
                element, otherwise search all descendants.

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
        self, *elements: type[_ElementT], recursive: bool = True
    ) -> _ElementT: ...

    @overload
    def find(
        self,
        *elements: type[Element] | names.ElementName | str,
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
        *elements: type[Element] | names.ElementName | str,
        recursive: bool = True,
        default: _T = _EMPTY_PARAM,
    ) -> Element | _T: ...

    def find(
        self,
        *elements: type[Element] | names.ElementName | str,
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
            raise errors.SvgElementNotFoundError(msg) from e

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
        for attr_name in _REFERENCE_ATTR_NAMES:
            if not hasattr(self, attr_name):
                continue

            attr = _attr_or_default(self, attr_name)

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
    def main_transform(self) -> transform.Transform | None:
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
            transform.Transform | None,
            _attr_or_default(self, transform_attr_name),
        )

    @main_transform.setter
    def main_transform(self, value: transform.Transform | None) -> None:
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

    # region Reification

    def reify(
        self,
        *,
        recursive: bool = True,
        convert_shapes_to_paths: bool = False,
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
            context=_build_context(self.get_root()),
            recursive=recursive,
            convert_shapes_to_paths=convert_shapes_to_paths,
        )

    # endregion


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

    capabilities: Mapping[int, reify.Capability]
    """What each element of the tree can absorb, by object identity."""

    stylesheet: reify.Capability
    """What the document's stylesheets leave reifiable anywhere in it."""


def _resolve_reference(
    element: Element,
    attr_name: attr_names.AttributeName,
    index: Mapping[str, Element],
    /,
    *,
    warn: bool = False,
) -> Element | None:
    """Follow a local IRI reference to the element it points at.

    A reference that resolves to nothing renders as nothing, so reification
    treats it as no reference at all.
    """
    attr = _attr_or_default(element, attr_name)

    if not (isinstance(attr, iri.Iri) and attr.is_local):
        return None

    assert attr.fragment is not None
    target = index.get(attr.fragment)

    if target is None and warn:
        warnings.warn(
            f"Dangling IRI reference {attr_name}={attr.serialize()!r}",
            stacklevel=2,
        )

    return target


def _pattern_transform_capability(target: Element, /) -> reify.Capability:
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
    """
    pattern_transform = _attr_or_default(target, "patternTransform")
    matrix = transform.compose(
        cast("transform.Transform | None", pattern_transform) or []
    )
    identity = transform.Matrix.identity()

    if matrix == identity:
        return reify.AFFINE

    if matrix.linear() == identity:
        return reify.TRANSLATION

    if matrix.translation() == transform.Translate(0, 0):
        return reify.UNIFORM_SCALING - reify.TRANSLATION

    return reify.NOTHING


def _pattern_capability(target: Element, /) -> reify.Capability:
    """Work out what a pattern lets the element it paints absorb.

    The tile is placed relative to the bounding box, so it moves and resizes
    with the element. The content inside the tile only follows as far as its
    own coordinate system does: a `viewBox` maps it onto the tile, and
    `patternContentUnits` can tie it to the bounding box, but by default it is
    drawn at its natural size in user space and only the tiling changes.

    Whatever the tile allows is then narrowed by the pattern's own
    `patternTransform`, which the tiling has to keep in step with.
    """
    if _attr_or_default(target, "patternUnits") != "objectBoundingBox":
        return reify.NOTHING

    return _pattern_tile_capability(
        target
    ) & _pattern_transform_capability(target)


def _pattern_tile_capability(target: Element, /) -> reify.Capability:
    """Work out how far the content of a pattern follows its tile."""
    if _attr_or_default(target, "viewBox") is not None:
        return (
            reify.UPRIGHT
            if reify.stretches_content(target)
            else reify.UNIFORM_SCALING
        )

    if (
        _attr_or_default(target, "patternContentUnits")
        == "objectBoundingBox"
    ):
        return reify.UPRIGHT

    return reify.TRANSLATION


def _paint_server_capability(target: Element, /) -> reify.Capability:
    """Work out what a paint server lets the element it paints absorb."""
    if isinstance(target, attrdefs.PatternUnitsAttr):
        return _pattern_capability(target)

    if isinstance(target, attrdefs.GradientUnitsAttr):
        # a gradient is a ramp across whatever space it is defined in, so it
        # is carried along by anything that leaves the box upright
        units = _attr_or_default(target, "gradientUnits")

        return (
            reify.UPRIGHT
            if units == "objectBoundingBox"
            else reify.NOTHING
        )

    # not a paint server at all; nothing to keep in step with
    return reify.AFFINE


def _resource_capability(
    target: Element, attr_name: attr_names.AttributeName, /
) -> reify.Capability:
    """Work out what a referenced resource lets the element absorb.

    A resource described as a fraction of the box of whatever refers to it
    follows that element wherever reification puts it -- but only as far as
    moving and resizing go, since turning or flipping the element would have
    turned or flipped the resource too, and rewriting a box cannot say that.
    A resource expressed in user space follows nowhere: it is resolved in the
    coordinate system the referencing element renders in, which is exactly
    what reification takes away.
    """
    match attr_name:
        case "fill" | "stroke":
            return _paint_server_capability(target)
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

    return reify.UPRIGHT if units == "objectBoundingBox" else reify.NOTHING


def _reference_capability(
    element: Element, index: Mapping[str, Element], /
) -> reify.Capability:
    """Work out what the element's references let it absorb."""
    capability = reify.AFFINE

    for attr_name in _RESOURCE_ATTR_NAMES:
        target = _resolve_reference(element, attr_name, index, warn=True)

        if target is not None:
            capability &= _resource_capability(target, attr_name)

    filter_ = _resolve_reference(element, "filter", index)

    if filter_ is not None:
        capability &= _filter_capability(filter_)

    return capability


def _filter_capability(target: Element, /) -> reify.Capability:
    """Work out what a filter lets the element it is attached to absorb."""
    if _attr_or_default(target, "filterUnits") != "objectBoundingBox":
        # the filter region is pinned to the coordinate system the element
        # renders in, so moving the element would leave the region behind
        return reify.NOTHING

    # the region follows the bounding box, but the primitives are
    # parametrized in user space, so the element may only move
    return reify.TRANSLATION


def _is_outermost_viewport(element: Element, /) -> bool:
    return (
        isinstance(element, reify.DocumentFragmentRoot)
        and element.parent is None
    )


def _pushes_transform_to_children(element: Element, /) -> bool:
    """Check whether the children inherit the element's coordinate system.

    When they do, a transformation on the element is equivalent to the same
    transformation on each of its children, which is what lets reification
    carry one down the tree to elements that can absorb it.
    """
    return isinstance(
        element, reify.TransformInheritedByChildren
    ) or _is_outermost_viewport(element)


def _delegates_transform(element: Element, /) -> bool:
    """Check whether the transformation belongs entirely to the children.

    A `g` has no geometry of its own, so there is nothing to fold a
    transformation into -- handing it to the children is the whole of the
    work. The outermost `svg` is in the same position: its `x`, `y`, `width`
    and `height` describe the canvas rather than anything drawn on it, so its
    transformation applies to its content.
    """
    return _pushes_transform_to_children(element) and (
        _is_outermost_viewport(element)
        or not reify.has_own_geometry(element)
    )


def _children_inheriting_transform(element: Element, /) -> list[Element]:
    """List the children a transformation would have to be handed to."""
    return [
        child
        for child in element.find_all(recursive=False)
        if not isinstance(child, reify.RenderedIndirectly)
    ]


def _has_unusable_transform_origin(element: Element, /) -> bool:
    """Check whether `transform-origin` is something reification can fold in.

    Only a pair of absolute lengths can be turned into the two translations
    that carry a transformation around the origin. A keyword such as
    `center`, or a percentage of a box reification cannot see, cannot -- and
    an element that cannot take its own origin apart cannot be handed a
    transformation by its parent either.
    """
    origin = _attr_or_default(element, "transform-origin")

    if origin is None:
        return False

    if not (
        isinstance(origin, tuple)
        and len(origin) == 2  # noqa: PLR2004
        and all(isinstance(value, length.Length) for value in origin)
    ):
        return True

    try:
        float(origin[0])
        float(origin[1])
    except errors.SvgUnitConversionError:
        return True

    return False


def _element_capability(
    element: Element,
    /,
    *,
    context: _Context,
    children: Mapping[int, reify.Capability],
) -> reify.Capability:
    """Work out how much of a transformation an element can take on.

    `children` holds the capability of every element below this one, so that
    the whole tree is worked out from the leaves upwards in a single pass.
    """
    if id(element) in context.frozen or _has_unusable_transform_origin(
        element
    ):
        return reify.NOTHING

    inheriting = _children_inheriting_transform(element)

    if _pushes_transform_to_children(element) and any(
        id(child) in context.pinned or id(child) in context.frozen
        for child in inheriting
    ):
        # a child that something else in the document points at has to keep
        # rendering the way it does now, so nothing may be pushed into it --
        # and pushing to only some of the children would tear the group apart
        return reify.NOTHING

    if _delegates_transform(element):
        # the element has no geometry of its own, but what it refers to is
        # still resolved where it sits: a clip path, a mask or a filter in
        # user space stays behind when the transformation moves down to the
        # children, and the content slides out from under it
        capability = (
            _reference_capability(element, context.by_id)
            & reify.style_capability(element)
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
        reify.geometry_capability(element)
        & _reference_capability(element, context.by_id)
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
            return reify.NOTHING

        capability &= children[id(child)]

    return capability


def _capabilities(
    root: Element, /, *, context: _Context
) -> dict[int, reify.Capability]:
    """Work out what every element of a tree can absorb, leaves first.

    A container can only take on what its children can, so the tree has to be
    read from the bottom up. Doing that once here keeps it linear, and keeps
    the depth of the document out of the call stack.
    """
    order: list[Element] = []
    stack = collections.deque([root])

    while stack:
        element = stack.pop()
        order.append(element)
        stack.extend(element.find_all(recursive=False))

    capabilities: dict[int, reify.Capability] = {}

    # a parent always comes before its children in the order above, so
    # reversing it puts every child before its parent
    for element in reversed(order):
        capabilities[id(element)] = _element_capability(
            element, context=context, children=capabilities
        )

    return capabilities


def _transform_capability(
    element: Element, /, *, context: _Context
) -> reify.Capability:
    """Look up how much of a transformation an element can take on."""
    capability = context.capabilities.get(id(element))

    if capability is not None:
        return capability

    # an element made during the walk rather than read from the document --
    # the `path` a basic shape is converted into. It draws the shape itself
    # and has no children, so there is nothing below it to work out first
    return _element_capability(
        element, context=context, children=context.capabilities
    )


def _reify_element(element: Element, /, *, context: _Context) -> None:
    """Fold as much of the element's transformation into it as will go."""
    try:
        element.decompose_transform_origin()
    except (errors.SvgTransformOriginError, errors.SvgUnitConversionError):
        # the origin is a keyword or a percentage of a box reification
        # cannot see, so the transformation has to stay where it is
        return

    if not element.main_transform:
        element.main_transform = None
        return

    identity = transform.Matrix.identity()
    matrix = transform.compose(element.main_transform)
    capability = _transform_capability(element, context=context)
    residue, absorbed = reify.split(matrix, capability)

    if absorbed == identity:
        if matrix == identity:
            # the list does nothing, so the attribute can simply go
            element.main_transform = None

        # nothing was folded in; the list is left exactly as written
        return

    if reify.has_own_geometry(element) and not _delegates_transform(
        element
    ):
        reify.apply(element, absorbed)

    if _pushes_transform_to_children(element):
        # the children are placed in the coordinate system the element
        # establishes, so they have to be given back what was taken out of it
        for child in _children_inheriting_transform(element):
            child.decompose_transform_origin()

            if child.main_transform is None:
                child.main_transform = []

            child.main_transform.insert(0, absorbed)

    element.main_transform = _normalize_transform(residue)


def _convert_to_path(
    parent: Element, child: Element, /, *, context: _Context
) -> None:
    """Replace a basic shape with an equivalent `path`, if that helps.

    A `rect` cannot be rotated, but the path that draws the same rectangle
    can. If the conversion does not get rid of the transformation after all,
    the original element is put back.
    """
    to_path = getattr(child, "to_path", None)

    if to_path is None:
        return

    try:
        path = cast(Element, to_path())
    except errors.SvgUnitConversionError:
        # a shape sized in percentages has no path equivalent that does not
        # need to know the viewport
        return

    position = parent.get_child_index(child)

    parent.pop_child(position)
    parent.add_child(path, index=position)

    _reify_element(path, context=context)

    if path.main_transform is not None:
        parent.pop_child(position)
        parent.add_child(child, index=position)


def _reify_tree(
    element: Element,
    /,
    *,
    context: _Context,
    recursive: bool,
    convert_shapes_to_paths: bool,
) -> None:
    """Reify an element and, if asked, everything below it.

    The walk keeps its own stack: an SVG can be nested arbitrarily deeply and
    a recursive walk would run out of Python frames long before the document
    runs out of elements.
    """
    _reify_element(element, context=context)

    if not recursive:
        return

    # each entry is a parent whose children still have to be visited, so that
    # a shape can be replaced in place once its own subtree is done
    pending: list[Element] = [element]

    while pending:
        parent = pending.pop()

        for child in list(parent.find_all(recursive=False)):
            _reify_element(child, context=context)
            pending.append(child)

    if not convert_shapes_to_paths:
        return

    for parent in [element, *element.find_all()]:
        for child in list(parent.find_all(recursive=False)):
            if child.main_transform is not None:
                _convert_to_path(parent, child, context=context)


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
    """
    frozen: set[int] = set()

    for element in itertools.chain([root], root.find_all()):
        if not isinstance(element, reify.Animation):
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
    """
    pinned: set[int] = set()

    def pin(target: Element, /) -> None:
        pinned.add(id(target))
        pinned.update(id(ancestor) for ancestor in target.ancestors)

    for element in itertools.chain([root], root.find_all()):
        if id(element) in frozen:
            pin(element)

        for attr_name in (*_REFERENCE_ATTR_NAMES, "filter"):
            target = _resolve_reference(element, attr_name, index)

            if target is not None:
                pin(target)

    return pinned


def _stylesheet_capability(root: Element, /) -> reify.Capability:
    """Work out what the document's stylesheets leave reifiable."""
    capability = reify.AFFINE

    for element in itertools.chain([root], root.find_all()):
        if not isinstance(element, reify.Stylesheet):
            continue

        css = "".join(
            child.content
            for child in element.children
            if isinstance(child, CharacterData)
        )
        capability &= reify.stylesheet_capability(css)

    return capability


def _build_context(root: Element, /) -> _Context:
    """Gather what reifying part of a tree needs to know about all of it."""
    index = _index_by_id(root)
    frozen = _frozen_elements(root, index)

    context = _Context(
        by_id=index,
        pinned=_pinned_elements(root, index, frozen),
        frozen=frozen,
        capabilities={},
        stylesheet=_stylesheet_capability(root),
    )

    return context._replace(
        capabilities=_capabilities(root, context=context)
    )


# endregion
