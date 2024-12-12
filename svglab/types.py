from typing import (
    Literal,
    Protocol,
    TypeAlias,
    TypeVar,
    runtime_checkable,
)

_AnyStr_contra = TypeVar("_AnyStr_contra", str, bytes, contravariant=True)
_AnyStr_co = TypeVar("_AnyStr_co", str, bytes, covariant=True)


@runtime_checkable
class SupportsRead(Protocol[_AnyStr_co]):
    """Protocol for objects that support reading.

    This exists because using `SupportsRead` from `typeshed` causes problems.

    Example:
    >>> from io import StringIO
    >>> buf = StringIO()
    >>> isinstance(buf, SupportsRead)
    True

    """

    def read(self, size: int | None = None, /) -> _AnyStr_co: ...


@runtime_checkable
class SupportsWrite(Protocol[_AnyStr_contra]):
    """Protocol for objects that support writing.

    This exists because using `SupportsWrite` from `typeshed` causes problems.

    Example:
    >>> from io import StringIO
    >>> buf = StringIO()
    >>> isinstance(buf, SupportsWrite)
    True

    """

    def write(self, data: _AnyStr_contra, /) -> int: ...


Parser: TypeAlias = Literal["html.parser", "lxml", "lxml-xml", "html5lib"]
""" Type for parsers supported by BeautifulSoup. """
