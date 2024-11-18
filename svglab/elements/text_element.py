from abc import ABCMeta, abstractmethod
from contextlib import suppress
from typing import cast, final

from bs4 import CData as _CData
from bs4 import Comment as _Comment
from bs4 import NavigableString

from .element import Element

__all__ = ["Comment", "CData", "Text"]


class TextElement[T: _Comment | _CData | NavigableString](
    Element[T], metaclass=ABCMeta
):
    def __init__(
        self,
        content: str | None = None,
        backend: T | None = None,
    ) -> None:
        super().__init__(backend=backend)

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

    def __str__(self) -> str:
        return self.content

    def __hash__(self) -> int:
        return hash(self.content)

    @property
    @abstractmethod
    def _backend_type(self) -> type[T]: ...


@final
class Comment(TextElement[_Comment]):
    @property
    def _backend_type(self) -> type[_Comment]:
        return _Comment


@final
class CData(TextElement[_CData]):
    @property
    def _backend_type(self) -> type[_CData]:
        return _CData


@final
class Text(TextElement[NavigableString]):
    @property
    def _backend_type(self) -> type[NavigableString]:
        return NavigableString
