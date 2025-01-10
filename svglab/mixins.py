import abc

from typing_extensions import Generic, TypeVar, override

from svglab import protocols


_T_co = TypeVar("_T_co", covariant=True)
_T_contra = TypeVar("_T_contra", contravariant=True)


class AddSub(
    protocols.SupportsFullAddSub[_T_contra, _T_co],
    Generic[_T_contra, _T_co],
    metaclass=abc.ABCMeta,
):
    """A mixin for implementation of objects with addition and subtraction.

    The user must implement the `__add__` and `__sub__` methods.

    The class then provides default implementations for `__radd__`
    and `__rsub__`, which delegate to `__add__` and `__sub__`, respectively,
    and should be sufficient for most use cases.
    """

    @override
    def __radd__(self, other: _T_contra, /) -> _T_co:
        return self + other

    @override
    def __rsub__(self, other: _T_contra, /) -> _T_co:
        return self - other


class Mul(
    protocols.SupportsFullMul[_T_contra, _T_co],
    Generic[_T_contra, _T_co],
    metaclass=abc.ABCMeta,
):
    """A mixin for implementing objects with multiplication.

    The user must implement the `__mul__` method.

    The class then provides a default implementation for `__rmul__`,
    which delegates to `__mul__` and should be sufficient for most use cases.
    """

    @override
    def __rmul__(self, other: _T_contra, /) -> _T_co:
        return self * other
