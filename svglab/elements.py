from __future__ import annotations

import collections
import contextlib
import itertools
import os
import pathlib
import reprlib
import sys
from collections.abc import Iterable, Mapping
from typing import Final, SupportsIndex, cast, final, overload

import bidict
import bs4
import pydantic
from typing_extensions import Self

from svglab import attrs, constants, models, serialize, types, utils


class Element(models.BaseModel):
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

    def to_beautifulsoup_object(self) -> bs4.PageElement:
        match self:
            case TextElement():
                cls = BS_TO_TEXT_ELEMENT.inverse[type(self)]
                return cls(self.content)
            case Tag():
                tag = bs4.Tag(
                    name=self.name,
                    can_be_empty_element=not isinstance(self, PairedTag),
                    prefix=self.prefix,
                    is_xml=True,
                )

                for key, value in self.all_attrs().items():
                    tag[key] = str(value)

                if isinstance(self, PairedTag):
                    for child in self.children:
                        tag.append(child.to_beautifulsoup_object())

                return tag
            case _:
                msg = f"Unable to convert {type(self)} to a BeautifulSoup object."
                raise TypeError(msg)


class TextElement(Element):
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


class CData(TextElement):
    """A `CDATA` section.

    A `CDATA` section is a block of text that is not parsed by the XML parser,
    but is interpreted verbatim.

    `CDATA` sections are used to include text that contains characters
    that would otherwise be interpreted as XML markup.

    Example: `<![CDATA[<g id="foo"></g>]]>`
    """

    def __init__(self, content: str, /) -> None:
        super().__init__(content=content)


class Comment(TextElement):
    """A comment.

    A comment is a block of text that is not parsed by the XML parser,
    but is ignored.

    Comments are used to include notes and other information that is not
    intended to be displayed to the user.

    Example: `<!-- This is a comment -->`
    """

    def __init__(self, content: str, /) -> None:
        super().__init__(content=content)


class Text(TextElement):
    """A text node.

    A text node is a block of text that is parsed by the XML parser.

    Text nodes are used to include text that is intended to be displayed to the user.

    Example: `Hello, world!`
    """

    def __init__(self, content: str, /) -> None:
        super().__init__(content=content)


class Tag(Element):
    """A tag.

    A tag is an element that has a name and a set of attributes.

    Tags can be of two types:
    - paired tags, which have children (for example, `<g></g>`; see `PairedTag`)
    - unpaired tags, which do not have children (for example, `<rect />`)

    Tags can have standard attributes (for example, `id`, `class`, `color`) and
    non-standard user-defined attributes.

    Example: `<rect id="foo" class="bar" color="red" />`

    Usage:
    ```
    >>> tag = Rect(id="foo", class_="bar", color="red")
    >>> tag.id
    'foo'
    >>> tag.color
    Color('red', rgb=(255, 0, 0))

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


class PairedTag(Tag):
    """A paired tag.

    A paired tag is a tag that can have children.

    Example: `<g><rect /></g>`

    Usage:
    ```
    >>> g = G().add_child(Rect())
    >>> for child in g.children:
    ...     print(type(child).__name__)
    Rect

    ```
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


class CommonAttrs(pydantic.BaseModel):
    id: models.Attr[str] = None
    class_: models.Attr[str] = None
    color: models.Attr[attrs.ColorType] = None


class GeometricAttrs(pydantic.BaseModel):
    x: models.Attr[float] = None
    y: models.Attr[float] = None
    width: models.Attr[attrs.LengthType] = None
    height: models.Attr[attrs.LengthType] = None
    transform: models.Attr[attrs.TransformType] = None


@final
class Rect(CommonAttrs, GeometricAttrs, Tag):
    pass


@final
class G(CommonAttrs, PairedTag):
    pass


@final
class Svg(CommonAttrs, PairedTag):
    xmlns: models.Attr[str] = constants.DEFAULT_XMLNS

    @overload
    def save(
        self,
        path: str | os.PathLike[str],
        /,
        *,
        pretty: bool = True,
        trailing_newline: bool = True,
        formatter: serialize.Formatter | None = None,
    ) -> None: ...

    @overload
    def save(
        self,
        file: types.SupportsWrite[str],
        /,
        *,
        pretty: bool = True,
        trailing_newline: bool = True,
        formatter: serialize.Formatter | None = None,
    ) -> None: ...

    def save(
        self,
        path_or_file: str | os.PathLike[str] | types.SupportsWrite[str],
        /,
        *,
        pretty: bool = True,
        trailing_newline: bool = True,
        formatter: serialize.Formatter | None = None,
    ) -> None:
        """Convert the SVG document fragment to XML and write it to a file.

        Args:
        path_or_file: The path to the file to save the XML to, or a file-like object.
        pretty: Whether to produce pretty-printed XML.
        indent: The number of spaces to indent each level of the document.
        trailing_newline: Whether to add a trailing newline to the file.
        formatter: The formatter to use for serialization.

        Examples:
        >>> svg = Svg(id="foo").add_child(Rect())
        >>> formatter = serialize.Formatter(indent=4)
        >>> svg.save(
        ...     sys.stdout, pretty=True, trailing_newline=False, formatter=formatter
        ... )
        <svg id="foo">
            <rect/>
        </svg>

        """
        with contextlib.ExitStack() as stack:
            output = self.to_xml(pretty=pretty, formatter=formatter)
            file: types.SupportsWrite[str]

            match path_or_file:
                case str() | os.PathLike() as path:
                    file = stack.enter_context(pathlib.Path(path).open("w"))
                case types.SupportsWrite() as file:
                    pass

            file.write(output)

            if trailing_newline:
                file.write("\n")


BS_TO_TEXT_ELEMENT: Final = bidict.frozenbidict(
    {
        bs4.CData: CData,
        bs4.Comment: Comment,
        bs4.NavigableString: Text,
    }
)


TAG_NAME_TO_CLASS: Final = {
    cls().name: cls
    for cls in itertools.chain(Tag.__subclasses__(), PairedTag.__subclasses__())
}
