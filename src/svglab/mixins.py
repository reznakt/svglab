"""Miscellaneous useful utility mixins.

This module is used to define mixins that can be used to add common
functionality to classes. The mixins are used to define common functionality
that is not specific to a particular class, but is useful for multiple classes.
"""

import abc

import pydantic
import pydantic_core
from typing_extensions import Any, Literal, Self, TypeVar, override

from svglab import protocols


_T_contra = TypeVar("_T_contra", contravariant=True)
_SupportsNegT_contra = TypeVar(
    "_SupportsNegT_contra", bound=protocols.SupportsNeg, contravariant=True
)
_SupportsRTrueDivT_contra = TypeVar(
    "_SupportsRTrueDivT_contra",
    bound=protocols.SupportsRTrueDiv[Any],
    contravariant=True,
)


class CustomModel(protocols.PydanticCompatible, metaclass=abc.ABCMeta):
    """A mixin for easy creation of custom pydantic-compatible classes.

    This class is a mixin for classes that need to be pydantic-compatible,
    but are not, for technical reasons, pydantic dataclasses or subclasses
    of `BaseModel` (for example collections).

    By implementing the `_validate` class method, the class can be used
    in pydantic models. `__get_pydantic_core_schema__` is created
    automatically and should not be overridden.
    """

    @classmethod
    @abc.abstractmethod
    def _validate(
        cls, value: object, info: pydantic_core.core_schema.ValidationInfo
    ) -> Self:
        """Validate the value and return a new instance of the class."""

    @override
    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: type, handler: pydantic.GetCoreSchemaHandler
    ) -> pydantic_core.core_schema.CoreSchema:
        del source_type, handler

        return (
            pydantic_core.core_schema.with_info_plain_validator_function(
                function=cls._validate
            )
        )


class SubWithNeg(
    protocols.SupportsAdd[_SupportsNegT_contra],
    protocols.SupportsSub[_SupportsNegT_contra],
    metaclass=abc.ABCMeta,
):
    """Implement subtraction using negation and addition."""

    @override
    def __sub__(self, other: _SupportsNegT_contra, /) -> Self:
        return self + -other


class RAddWithAdd(
    protocols.SupportsRAdd[_T_contra],
    protocols.SupportsAdd[_T_contra],
    metaclass=abc.ABCMeta,
):
    """Implement right addition using addition."""

    @override
    def __radd__(self, other: _T_contra, /) -> Self:
        return self + other


class RSubWithSub(
    protocols.SupportsRSub[_T_contra],
    protocols.SupportsSub[_T_contra],
    metaclass=abc.ABCMeta,
):
    """Implement right subtraction using subtraction."""

    @override
    def __rsub__(self, other: _T_contra, /) -> Self:
        return self - other


class RMulWithMul(
    protocols.SupportsRMul[_T_contra],
    protocols.SupportsMul[_T_contra],
    metaclass=abc.ABCMeta,
):
    """Implement right multiplication using multiplication."""

    @override
    def __rmul__(self, other: _T_contra, /) -> Self:
        return self * other


class RTruedivWithTrueDiv(
    protocols.SupportsRTrueDiv[_T_contra],
    protocols.SupportsTrueDiv[_T_contra],
    metaclass=abc.ABCMeta,
):
    """Implement right true division using true division."""

    @override
    def __rtruediv__(self, other: _T_contra, /) -> Self:
        return self / other


class NegWithMul(
    protocols.SupportsNeg,
    protocols.SupportsMul[Literal[-1]],
    metaclass=abc.ABCMeta,
):
    """Implement negation using multiplication by -1."""

    @override
    def __neg__(self) -> Self:
        return self * -1


class TrueDivWithMul(
    protocols.SupportsTrueDiv[_SupportsRTrueDivT_contra],
    protocols.SupportsMul[_SupportsRTrueDivT_contra],
    metaclass=abc.ABCMeta,
):
    """Implement true division using multiplication by the reciprocal."""

    @override
    def __truediv__(self, other: _SupportsRTrueDivT_contra, /) -> Self:
        return self * (1 / other)


class FloatMulDiv(
    NegWithMul,
    RMulWithMul[float],
    RTruedivWithTrueDiv[float],
    TrueDivWithMul[float],
    metaclass=abc.ABCMeta,
):
    """Implement multiplication and division as effortlessly as possible."""


class AddSub(
    SubWithNeg[_SupportsNegT_contra],
    RAddWithAdd[_SupportsNegT_contra],
    RSubWithSub[_SupportsNegT_contra],
    metaclass=abc.ABCMeta,
):
    """Implement addition and subtraction as effortlessly as possible."""
