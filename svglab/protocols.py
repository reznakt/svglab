from __future__ import annotations

import pydantic
import pydantic_core
from typing_extensions import Protocol, Self, TypeVar, runtime_checkable


_T_contra = TypeVar("_T_contra", contravariant=True)

_AnyStr_contra = TypeVar("_AnyStr_contra", str, bytes, contravariant=True)
_AnyStr_co = TypeVar("_AnyStr_co", str, bytes, covariant=True)


@runtime_checkable
class CustomSerializable(Protocol):
    """Protocol for objects with special serialization behavior.

    When a `Serializable` object is serialized, its `serialize()` method is
    used to obtain the string representation, instead of using `str()`.
    """

    def serialize(self) -> str:
        """Return an SVG-friendly string representation of this object."""
        ...


@runtime_checkable
class PydanticCompatible(Protocol):
    """A protocol for classes that can be used as pydantic models."""

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: type, handler: pydantic.GetCoreSchemaHandler
    ) -> pydantic_core.core_schema.CoreSchema: ...


@runtime_checkable
class SupportsRead(Protocol[_AnyStr_co]):
    def read(self, size: int | None = None, /) -> _AnyStr_co: ...


@runtime_checkable
class SupportsWrite(Protocol[_AnyStr_contra]):
    def write(self, data: _AnyStr_contra, /) -> int: ...


@runtime_checkable
class SupportsAdd(Protocol[_T_contra]):
    def __add__(self, other: _T_contra, /) -> Self: ...


@runtime_checkable
class SupportsRAdd(Protocol[_T_contra]):
    def __radd__(self, other: _T_contra, /) -> Self: ...


@runtime_checkable
class SupportsSub(Protocol[_T_contra]):
    def __sub__(self, other: _T_contra, /) -> Self: ...


@runtime_checkable
class SupportsRSub(Protocol[_T_contra]):
    def __rsub__(self, other: _T_contra, /) -> Self: ...


@runtime_checkable
class SupportsMul(Protocol[_T_contra]):
    def __mul__(self, other: _T_contra, /) -> Self: ...


@runtime_checkable
class SupportsRMul(Protocol[_T_contra]):
    def __rmul__(self, other: _T_contra, /) -> Self: ...


@runtime_checkable
class SupportsTrueDiv(Protocol[_T_contra]):
    def __truediv__(self, other: _T_contra, /) -> Self: ...


class SupportsRTrueDiv(Protocol[_T_contra]):
    def __rtruediv__(self, other: _T_contra, /) -> Self: ...


@runtime_checkable
class SupportsRMatmul(Protocol[_T_contra]):
    def __rmatmul__(self, other: _T_contra, /) -> Self: ...


@runtime_checkable
class SupportsNeg(Protocol):
    def __neg__(self) -> Self: ...


@runtime_checkable
class PointLike(SupportsNeg, Protocol):
    x: float
    y: float
