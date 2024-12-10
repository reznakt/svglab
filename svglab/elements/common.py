from __future__ import annotations

import abc
import collections
import reprlib
import sys
from collections.abc import Iterable, Mapping
from typing import SupportsIndex, cast

import bs4
import pydantic
from typing_extensions import Self

from svglab import attrs, models, serialize, utils

__all__ = [
    "Element",
    "PairedTag",
    "Tag",
    "TextElement",
]


class Element(models.BaseModel, abc.ABC):
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
        >>> from svglab import Rect
        >>> rect = Rect(id="foo", x=100, y=100)
        >>> rect.to_xml()
        '<rect id="foo" x="100.0" y="100.0"/>'

        """
        formatter = formatter or serialize.get_current_formatter()

        with formatter:
            soup = self.to_beautifulsoup_object()
            return utils.beautifulsoup_to_str(
                soup, pretty=pretty, indent=formatter.indent
            )

    @abc.abstractmethod
    def to_beautifulsoup_object(self) -> bs4.PageElement: ...


class TextElement(Element, abc.ABC):
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

    def __repr__(self) -> str:
        name = type(self).__name__
        return f"{name}({self.content!r})"


class Tag(Element, abc.ABC):
    """A tag.

    A tag is an element that has a name and a set of attributes.

    Tags can be of two types:
    - paired tags, which have children (for example, `<g></g>`; see `PairedTag`)
    - unpaired tags, which do not have children (for example, `<rect />`)

    Tags can have standard attributes (for example, `id`, `class`, `color`) and
    non-standard user-defined attributes.

    Example: `<rect id="foo" class="bar" color="red" />`
    ```
    """

    model_config = pydantic.ConfigDict(
        extra="allow",
        alias_generator=lambda name: attrs.ATTR_TO_NORMALIZED.inverse.get(name, name),
    )

    prefix: str | None = None

    @pydantic.computed_field
    @property
    def name(self) -> str:
        return type(self).__name__.lower()

    @pydantic.model_validator(mode="after")
    def __validate_extra(self) -> Tag:
        # model_extra cannot be None because extra is set to "allow"
        assert self.model_extra is not None

        for key, value in self.model_extra.items():
            if not isinstance(value, str):
                msg = (
                    f"Non-standard attribute {key!r} must be of type str,"
                    f" got {type(value).__name__}"
                )
                raise TypeError(msg)

        return self

    def __getitem__(self, key: str) -> str:
        assert self.model_extra is not None
        value: str = self.model_extra[key]
        return value

    def __setitem__(self, key: str, value: str) -> None:
        assert self.model_extra is not None
        self.model_extra[key] = value

    def __delitem__(self, key: str) -> None:
        assert self.model_extra is not None
        del self.model_extra[key]

    def extra_attrs(self) -> Mapping[str, str]:
        assert self.model_extra is not None
        return self.model_extra

    def standard_attrs(self) -> Mapping[attrs.AttributeName, object]:
        dump = self.model_dump(
            by_alias=True,
            exclude_defaults=True,
            exclude_unset=True,
            exclude_none=True,
        )

        return {
            cast(attrs.AttributeName, key): getattr(self, key)
            for key, _ in dump.items()
            if key in attrs.ATTRIBUTE_NAMES
        }

    def all_attrs(self) -> Mapping[str, object]:
        standard = cast(Mapping[str, object], self.standard_attrs())
        extra = self.extra_attrs()

        return {**standard, **extra}

    @reprlib.recursive_repr()
    def __repr__(self) -> str:
        name = type(self).__name__
        attrs = dict(self.all_attrs())

        if isinstance(self, PairedTag):
            attrs["children"] = list(self.children)

        attr_repr = ", ".join(f"{key}={value!r}" for key, value in attrs.items())

        return f"{name}({attr_repr})"

    def to_beautifulsoup_object(self) -> bs4.Tag:
        tag = bs4.Tag(
            name=self.name,
            can_be_empty_element=True,
            prefix=self.prefix,
            is_xml=True,
        )

        for key, value in self.all_attrs().items():
            tag[key] = str(value)

        return tag


class PairedTag(Tag, abc.ABC):
    """A paired tag.

    A paired tag is a tag that can have children.

    Example: `<g><rect /></g>`
    """

    __children: list[Element] = pydantic.PrivateAttr(default_factory=list)

    @pydantic.computed_field
    @property
    def children(self) -> Iterable[Element]:
        return iter(self.__children)

    @pydantic.computed_field
    @property
    def descendants(self) -> Iterable[Element]:
        queue = collections.deque(self.children)

        while queue:
            child = queue.popleft()
            yield child

            if isinstance(child, PairedTag):
                queue.extend(child.children)

    @pydantic.computed_field
    @property
    def parents(self) -> Iterable[Element]:
        curr = self.parent

        while curr is not None:
            yield curr
            curr = curr.parent

    @pydantic.computed_field
    @property
    def next_siblings(self) -> Iterable[Element]:
        if self.parent is None or not isinstance(self.parent, PairedTag):
            return

        should_yield = False

        for sibling in self.parent.children:
            if should_yield:
                yield sibling
            elif sibling is self:
                should_yield = True

    @pydantic.computed_field
    @property
    def prev_siblings(self) -> Iterable[Element]:
        if self.parent is None or not isinstance(self.parent, PairedTag):
            return

        for sibling in self.parent.children:
            if sibling is self:
                return

            yield sibling

    def add_child(self, child: Element, /, *, index: int | None = None) -> Self:
        if child is self:
            raise ValueError("Cannot add a tag as a child of itself.")

        if child.parent is not None:
            raise ValueError("Cannot add a child that already has a parent.")

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
        self.__children.remove(child)
        child.parent = None

        return child

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

    def to_beautifulsoup_object(self) -> bs4.Tag:
        tag = super().to_beautifulsoup_object()
        tag.can_be_empty_element = False

        for child in self.children:
            tag.append(child.to_beautifulsoup_object())

        return tag
