import typing_extensions
from typing_extensions import Protocol, TypeVar, runtime_checkable
from useful_types import (
    SupportsAdd,
    SupportsRAdd,
    SupportsRSub,
    SupportsSub,
)


_T_co = TypeVar("_T_co", covariant=True)
_T_contra = TypeVar("_T_contra", contravariant=True)

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


@runtime_checkable
class SupportsFullAddSub(
    SupportsAdd[_T_contra, _T_co],
    SupportsSub[_T_contra, _T_co],
    SupportsRAdd[_T_contra, _T_co],
    SupportsRSub[_T_contra, _T_co],
    typing_extensions.Protocol,
):
    """Protocol for objects that support addition and subtraction.

    This is a combination of `SupportsAdd`, `SupportsSub`, `SupportsRAdd`,
    and `SupportsRSub`.

    Example:
    >>> isinstance(1, SupportsFullAddSub)
    True

    """


@runtime_checkable
class SupportsMul(Protocol[_T_contra, _T_co]):
    """Protocol for objects that support multiplication.

    Example:
    >>> isinstance(1, SupportsMul)
    True

    """

    def __mul__(self, other: _T_contra, /) -> _T_co: ...


@runtime_checkable
class SupportsRMul(Protocol[_T_contra, _T_co]):
    """Protocol for objects that support right multiplication.

    Example:
    >>> isinstance(1, SupportsRMul)
    True

    """

    def __rmul__(self, other: _T_contra, /) -> _T_co: ...


@runtime_checkable
class SupportsFullMul(
    SupportsMul[_T_contra, _T_co],
    SupportsRMul[_T_contra, _T_co],
    Protocol[_T_contra, _T_co],
):
    """Protocol for objects that support multiplication in both directions.

    Example:
    >>> isinstance(1, SupportsFullMul)
    True

    """
