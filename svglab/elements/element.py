from abc import ABCMeta, abstractmethod

from bs4 import BeautifulSoup, PageElement

__all__ = ["Element"]


class Repr:
    def __repr__(self) -> str:
        name = self.__class__.__name__
        attrs = ", ".join(f"{key}={value!r}" for key, value in self.__dict__.items())

        return f"{name}({attrs})"


class Element[T: PageElement](Repr, metaclass=ABCMeta):
    def __init__(self, backend: T | None = None) -> None:
        self._backend = backend if backend is not None else self._backend_type()

    @property
    @abstractmethod
    def _backend_type(self) -> type[T]: ...

    def __str__(self) -> str:
        return self.to_str(pretty=False)

    @abstractmethod
    def __hash__(self) -> int: ...

    def to_str(self, *, pretty: bool = True) -> str:
        if pretty:
            soup = BeautifulSoup()
            soup.append(self._backend)
            return soup.prettify()

        return str(self._backend)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, self.__class__):
            return False

        if self is other:
            return True

        return hash(self) == hash(other)
