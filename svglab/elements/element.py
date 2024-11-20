from abc import ABCMeta, abstractmethod
from collections.abc import Hashable
from typing import Self

import bs4

from svglab.utils import Repr

__all__ = ["Element", "AnyElement"]

type AnyElement = Element[bs4.PageElement]


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

    # TODO: restrict the type of element based allowed children
    def replace_with(self, element: AnyElement) -> Self:
        self._backend.replace_with(element.backend)
        return self
