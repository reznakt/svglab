from __future__ import annotations

import abc
import collections
import reprlib
import sys
from collections.abc import Generator, Mapping

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
from svglab.attrs import groups
from svglab.attrs import names as attr_names
from svglab.elements import names


_T = TypeVar("_T")
_T_tag = TypeVar("_T_tag", bound="Tag")

_EMPTY_PARAM: Final = object()
"""A sentinel value for an empty parameter."""


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

        with serialize.use_formatter(formatter):
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

    def _find_children(self, *tags: type[_T_tag]) -> Generator[_T_tag]:
        return self.find_all(*tags, recursive=False)

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
