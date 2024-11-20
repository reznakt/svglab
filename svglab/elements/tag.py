from abc import ABCMeta
from collections.abc import Iterable
from typing import Final, Self, final

import bs4

from svglab.utils import SizedIterable

from .element import AnyElement, Element
from .text_element import CData, Comment, Text


def backend_to_element(backend: bs4.PageElement) -> AnyElement:
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
            msg = f"Unsupported backend type: {type(backend)}"
            raise ValueError(msg)


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
        return map(backend_to_element, self._backend.children)

    def add_child(self, child: AnyElement) -> Self:
        self._backend.append(child.backend)
        return self


class UnpairedTag(Tag, metaclass=ABCMeta):
    paired = False


@final
class Rect(UnpairedTag):
    name: Final = "rect"


@final
class G(PairedTag):
    name: Final = "g"
