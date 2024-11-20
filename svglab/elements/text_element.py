from abc import ABCMeta
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
        /,
        *,
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

    def __hash__(self) -> int:
        return hash(self.content)

    @property
    def _backend_type(self) -> type[T]:
        return type(self._default_backend)


@final
class Comment(TextElement[_Comment]):
    """Represents an XML/HTML comment.

    Example:
    >>> comment = Comment("foo")
    >>> print(comment)
    <!--foo-->

    """

    @property
    def _default_backend(self) -> _Comment:
        return _Comment("")


@final
class CData(TextElement[_CData]):
    """Represents an XML/HTML CDATA section.

    Example:
    >>> cdata = CData("foo")
    >>> print(cdata)
    <![CDATA[foo]]>

    """

    @property
    def _default_backend(self) -> _CData:
        return _CData("")


@final
class Text(TextElement[NavigableString]):
    """Represents an XML/HTML text section.

    Example:
    >>> text = Text("foo")
    >>> print(text)
    foo

    """

    @property
    def _default_backend(self) -> NavigableString:
        return NavigableString("")
