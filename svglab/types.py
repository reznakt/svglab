from typing import Protocol, runtime_checkable


@runtime_checkable
class SupportsRead[T: str | bytes](Protocol):
    """Protocol for objects that support reading.

    This exists because using `SupportsRead` from `typeshed` causes problems.

    Example:
    >>> from io import StringIO
    >>> buf = StringIO()
    >>> isinstance(buf, SupportsRead)
    True

    """

    def read(self, size: int | None = None, /) -> T: ...


@runtime_checkable
class SupportsWrite[T: str | bytes](Protocol):
    """Protocol for objects that support writing.

    This exists because using `SupportsWrite` from `typeshed` causes problems.

    Example:
    >>> from io import StringIO
    >>> buf = StringIO()
    >>> isinstance(buf, SupportsWrite)
    True

    """

    def write(self, data: T, /) -> int: ...
