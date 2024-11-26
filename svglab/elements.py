from __future__ import annotations

from abc import ABCMeta, abstractmethod
from collections.abc import Hashable, Iterable
from contextlib import ExitStack, suppress
from functools import cache
from os import PathLike
from typing import ClassVar, Final, Self, cast, final
from warnings import warn

import bs4
from atomicwrites import atomic_write
from bs4.formatter import XMLFormatter

from .types import SupportsWrite
from .utils import MappingFilterWrapper, Repr, SizedIterable

type Backend = bs4.PageElement
type TextBackend = bs4.Comment | bs4.CData | bs4.NavigableString

type AnyElement = Element[Backend]
type AnyTextElement = TextElement[TextBackend]


def get_tag_class(tag_name: str) -> type[Tag] | None:
    classes = {
        cls.name: cls
        for cls in UnpairedTag.__subclasses__() + PairedTag.__subclasses__()
    }

    def inner() -> type[Tag] | None:
        return classes.get(tag_name)

    return inner()


def backend_to_element(backend: Backend) -> AnyElement | None:
    match backend:
        case bs4.Tag():
            tag_cls = get_tag_class(backend.name)

            if tag_cls is None:
                warn(f"Unknown tag: {backend.name}", stacklevel=1)
                return None

            return tag_cls(_backend=backend)
        case bs4.Comment():
            return Comment(_backend=backend)
        case bs4.CData():
            return CData(_backend=backend)
        case bs4.NavigableString():
            return Text(_backend=backend)
        case _:
            warn(f"Unknown backend type: {type(backend)}", stacklevel=1)
            return None


@cache
def get_formatter(indent: int) -> XMLFormatter:
    if indent < 0:
        raise ValueError("Indent must be a non-negative integer")

    return XMLFormatter(indent=indent)


class Element[T: Backend](Repr, Hashable, metaclass=ABCMeta):
    def __init__(self, *, _backend: T | None = None) -> None:
        self._backend = _backend if _backend is not None else self._default_backend

    @property
    @abstractmethod
    def _default_backend(self) -> T: ...

    def _to_str(self, indent: int = 2) -> str:
        formatter = get_formatter(indent)

        soup = bs4.BeautifulSoup()
        soup.append(self._backend)

        return soup.prettify(formatter=formatter).strip()

    def __str__(self) -> str:
        return self._to_str()

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, self.__class__):
            return False

        if self is other:
            return True

        return hash(self) == hash(other)

    # expose the backend so that we can join them together
    # when adding children to a tag
    @property
    def backend(self) -> T:
        return self._backend

    # TODO: restrict the type of element based on allowed children
    def replace_with(self, element: AnyElement) -> Self:
        self._backend.replace_with(element.backend)
        return self

    @property
    def parent(self) -> AnyElement | None:
        parent = self._backend.parent
        return backend_to_element(parent) if parent is not None else None


class TextElement[T: TextBackend](Element[T], metaclass=ABCMeta):
    def __init__(
        self,
        content: str | None = None,
        /,
        *,
        _backend: T | None = None,
    ) -> None:
        super().__init__(_backend=_backend)

        if content is not None:
            self.content = content

    @property
    def content(self) -> str:
        return self._backend.get_text()

    @content.setter
    def content(self, content: str) -> None:
        new_backend = self._backend_type(content)

        # replace_with() fails if the backend is not part of a tree,
        # which is fine if we are not attached to a soup
        with suppress(ValueError):
            self._backend.replace_with(new_backend)

        # TODO: figure out a way for mypy to eat this without the cast
        self._backend = cast(T, new_backend)

    def __hash__(self) -> int:
        return hash(self.content)

    @property
    def _backend_type(self) -> type[T]:
        return type(self._default_backend)


@final
class Comment(TextElement[bs4.Comment]):
    """Represents an XML/HTML comment.

    Example:
    >>> comment = Comment("foo")
    >>> print(comment)
    <!--foo-->

    """

    @property
    def _default_backend(self) -> bs4.Comment:
        return bs4.Comment("")


@final
class CData(TextElement[bs4.CData]):
    """Represents an XML/HTML CDATA section.

    Example:
    >>> cdata = CData("foo")
    >>> print(cdata)
    <![CDATA[foo]]>

    """

    @property
    def _default_backend(self) -> bs4.CData:
        return bs4.CData("")


@final
class Text(TextElement[bs4.NavigableString]):
    """Represents an XML/HTML text section.

    Example:
    >>> text = Text("foo")
    >>> print(text)
    foo

    """

    @property
    def _default_backend(self) -> bs4.NavigableString:
        return bs4.NavigableString("")


class Tag(Element[bs4.Tag], metaclass=ABCMeta):
    name: ClassVar[str]
    paired: ClassVar[bool]
    allowed_attrs: ClassVar[frozenset[str]]

    def __init__(self, *, _backend: bs4.Tag | None = None) -> None:
        super().__init__(_backend=_backend)

        self.attrs: Final = MappingFilterWrapper(
            self._backend.attrs, key_filter=lambda key: key in self.allowed_attrs
        )

        self.extra_attrs: Final = MappingFilterWrapper(
            self._backend.attrs, key_filter=lambda key: key not in self.allowed_attrs
        )

    def __hash__(self) -> int:
        return hash(self._backend)

    @property
    def _default_backend(self) -> bs4.Tag:
        return bs4.Tag(name=self.name, can_be_empty_element=not self.paired)

    @property
    def namespace(self) -> str | None:
        return self._backend.namespace

    @namespace.setter
    def namespace(self, namespace: str | None) -> None:
        self._backend.namespace = namespace

    def __getattribute__(self, name: str) -> object:
        __getattribute__ = super().__getattribute__

        if name in type(self).allowed_attrs:
            backend: bs4.Tag = __getattribute__("_backend")
            return backend.attrs.get(name)

        return __getattribute__(name)

    def __setattr__(self, name: str, value: object) -> None:
        if name in type(self).allowed_attrs:
            self._backend.attrs[name] = value
            return

        super().__setattr__(name, value)

    def __delattr__(self, name: str) -> None:
        if name in type(self).allowed_attrs:
            del self._backend.attrs[name]
            return

        super().__delattr__(name)


class PairedTag[T: AnyElement](Tag, metaclass=ABCMeta):
    paired = True

    def __init__(self, *children: T, _backend: bs4.Tag | None = None) -> None:
        super().__init__(_backend=_backend)
        self.add_children(children)

    @property
    def children(self) -> SizedIterable[T]:
        return SizedIterable(self.__children())

    @property
    @abstractmethod
    def allowed_children(self) -> set[type[T]]: ...

    def __children(self) -> Iterable[T]:
        for child in self._backend.children:
            element = backend_to_element(child)

            if element is None:
                continue

            cls = type(element)

            if cls not in self.allowed_children:
                warn(
                    f"Element {cls} is not allowed as a child of {self.__class__}",
                    stacklevel=1,
                )
                continue

            # there is no way to statically ensure that the
            # element is of the correct type, so we have to cast
            # TODO: make sure this is correctly handled at runtime
            yield cast(T, element)

    def add_child(self, child: T) -> Self:
        child_type = type(child)

        if child_type not in self.allowed_children:
            msg = f"Element {child_type} is not allowed as a child of {type(self)}"
            raise TypeError(msg)

        self._backend.append(child.backend)
        return self

    def add_children(self, children: Iterable[T]) -> Self:
        for child in children:
            self.add_child(child)

        return self

    def select(
        self,
        query: str,
        namespaces: Iterable[str] | None = None,
        limit: int | None = None,
        *,
        flags: int = 0,
        custom: dict[str, str] | None = None,
    ) -> SizedIterable[T]:
        matches = self._backend.select(
            query, namespaces=namespaces, limit=limit, flags=flags, custom=custom
        )

        # TODO: remove cast and unify with __children()
        return SizedIterable(cast(T, backend_to_element(match)) for match in matches)

    def __getitem__(self, query: str) -> SizedIterable[T]:
        return self.select(query)


class UnpairedTag(Tag, metaclass=ABCMeta):
    paired: ClassVar = False


@final
class Rect(UnpairedTag):
    name: ClassVar = "rect"
    allowed_attrs: ClassVar = frozenset(("x", "y", "width", "height"))

    x: str | None
    y: str | None
    width: str | None
    height: str | None


type GChildren = AnyTextElement | G | Rect
type SvgChildren = AnyElement


@final
class G(PairedTag[GChildren]):
    name: ClassVar = "g"
    allowed_attrs: ClassVar = frozenset()

    @property
    def allowed_children(self) -> set[type[GChildren]]:
        return {Text, G, Rect, Comment, CData}


@final
class Svg(PairedTag[SvgChildren]):
    name: ClassVar = "svg"
    allowed_attrs: ClassVar = frozenset(("xmlns", "viewBox"))

    xmlns: str | None
    viewBox: str | None  # noqa: N815

    @property
    def allowed_children(self) -> set[type[SvgChildren]]:
        return {Text, G, Rect, Comment, CData, Svg}

    def save(
        self,
        path_or_file: str | PathLike[str] | SupportsWrite[str],
        /,
        *,
        indent: int = 2,
    ) -> None:
        with ExitStack() as stack:
            file: SupportsWrite[str]

            match path_or_file:
                case str() | PathLike() as path:
                    file = stack.enter_context(
                        atomic_write(path, mode="w", overwrite=True)
                    )
                case SupportsWrite() as file:
                    pass

            file.write(self._to_str(indent=indent))
            file.write("\n")
