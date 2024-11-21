from abc import ABCMeta, abstractmethod
from collections.abc import Hashable, Iterable
from contextlib import suppress
from typing import Final, Self, cast, final
from warnings import warn

import bs4

from .utils import Repr, SizedIterable

__all__ = [
    "Comment",
    "CData",
    "Text",
    "Tag",
    "Rect",
    "G",
]

type AnyElement = Element[bs4.PageElement]


def backend_to_element(backend: bs4.PageElement) -> AnyElement | None:
    match backend:
        case bs4.Tag():
            if backend.is_empty_element:
                return UnpairedTag(_backend=backend)
            return PairedTag(_backend=backend)
        case bs4.Comment():
            return Comment(_backend=backend)
        case bs4.CData():
            return CData(_backend=backend)
        case bs4.NavigableString():
            return Text(_backend=backend)
        case _:
            warn(f"Unknown backend type: {type(backend)}", stacklevel=1)
            return None


class Element[T: bs4.PageElement](Repr, Hashable, metaclass=ABCMeta):
    def __init__(self, *, _backend: T | None = None) -> None:
        self._backend = _backend if _backend is not None else self._default_backend

    @property
    @abstractmethod
    def _default_backend(self) -> T: ...

    def __str__(self) -> str:
        soup = bs4.BeautifulSoup()
        soup.append(self._backend)
        return soup.prettify().strip()

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


class TextElement[T: bs4.Comment | bs4.CData | bs4.NavigableString](
    Element[T], metaclass=ABCMeta
):
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
        comment = self._backend_type(content)

        # replace_with() fails if the backend is not part of a tree,
        # which is fine if we are not attached to a soup
        with suppress(ValueError):
            self._backend.replace_with(comment)

        # TODO: figure out a way for mypy to eat this without the cast
        self._backend = cast(T, comment)

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
    name: str
    paired: bool = NotImplemented

    def __hash__(self) -> int:
        return hash(self._backend)

    @property
    def _default_backend(self) -> bs4.Tag:
        return bs4.Tag(name=self.name, can_be_empty_element=not self.paired)


class PairedTag(Tag, metaclass=ABCMeta):
    paired = True

    def __init__(self, *children: AnyElement, _backend: bs4.Tag | None = None) -> None:
        super().__init__(_backend=_backend)

        for child in children:
            self.add_child(child)

    @property
    def children(self) -> SizedIterable[AnyElement]:
        return SizedIterable(self.__children())

    def __children(self) -> Iterable[AnyElement]:
        for child in self._backend.children:
            element = backend_to_element(child)

            if element is not None:
                yield element

    def add_child(self, child: AnyElement) -> Self:
        self._backend.append(child.backend)
        return self

    def add_children(self, children: Iterable[AnyElement]) -> Self:
        # use extend() because it's faster than multiple calls to add_child()
        self._backend.extend(child.backend for child in children)
        return self


class UnpairedTag(Tag, metaclass=ABCMeta):
    paired = False


@final
class Rect(UnpairedTag):
    name: Final = "rect"


@final
class G(PairedTag):
    name: Final = "g"
