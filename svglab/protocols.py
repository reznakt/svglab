import typing_extensions
from typing_extensions import (
    Protocol,
    TypeVar,
    override,
    runtime_checkable,
)
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
class SupportsAddSub(
    SupportsAdd[_T_contra, _T_co],
    SupportsSub[_T_contra, _T_co],
    SupportsRAdd[_T_contra, _T_co],
    SupportsRSub[_T_contra, _T_co],
    typing_extensions.Protocol,
):
    """Protocol for objects that support addition and subtraction.

    This is a combination of `SupportsAdd`, `SupportsSub`, `SupportsRAdd`,
    and `SupportsRSub`.

    The class also provides default implementations for `__radd__`
    and `__rsub__`, which delegate to `__add__` and `__sub__` respectively.
    This should be sufficient for most use cases.

    Example:
    >>> isinstance(1, SupportsAddSub)
    True

    """

    @override
    def __radd__(self, other: _T_contra, /) -> _T_co:
        return self + other

    @override
    def __rsub__(self, other: _T_contra, /) -> _T_co:
        return self - other


@runtime_checkable
class SupportsRMul(Protocol[_T_contra, _T_co]):
    """Protocol for objects that support right multiplication.

    Example:
    >>> isinstance(1, SupportsRMul)
    True

    """

    def __rmul__(self, other: _T_contra, /) -> _T_co: ...


@runtime_checkable
class SupportsMul(
    SupportsRMul[_T_contra, _T_co], Protocol[_T_contra, _T_co]
):
    """Protocol for objects that support multiplication.

    This is a combination of `SupportsRMul` and `SupportsMul`.

    The class also provides a default implementation for `__rmul__`,
    which delegates to `__mul__`. This should be sufficient for most use cases.

    Example:
    >>> isinstance(1, SupportsMul)
    True

    """

    def __mul__(self, other: _T_contra, /) -> _T_co: ...

    @override
    def __rmul__(self, other: _T_contra, /) -> _T_co:
        return self * other
