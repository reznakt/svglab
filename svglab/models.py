import abc
import reprlib
from typing import (
    Annotated,
    Protocol,
    TypeAlias,
    TypeVar,
    runtime_checkable,
)

import pydantic
import pydantic_core.core_schema
from pydantic import Field
from typing_extensions import Self, override


_T_co = TypeVar("_T_co", covariant=True)

KwOnly: TypeAlias = Annotated[_T_co, Field(kw_only=True)]
""" Pydantic field for a keyword-only attribute. """

Attr: TypeAlias = KwOnly[_T_co | None]
""" Pydantic field for an attribute. """


class BaseModel(pydantic.BaseModel):
    """Pydantic BaseModel with sane defaults and a few extra tweaks."""

    model_config = pydantic.ConfigDict(
        allow_inf_nan=False,
        extra="forbid",
        strict=True,
        validate_assignment=True,
        validate_default=True,
        validate_return=True,
    )

    @override
    def __copy__(self) -> Self:
        return self.model_copy(deep=False)

    @override
    def __deepcopy__(self, memo: dict[int, object] | None = None) -> Self:
        del memo
        return self.model_copy(deep=True)

    @override
    def __str__(self) -> str:
        return repr(self)

    # patch pydantic's __repr__ so that is doesn't break on cyclic models
    # see https://github.com/pydantic/pydantic/issues/9424
    @reprlib.recursive_repr()
    @override
    def __repr__(self) -> str:
        return super().__repr__()


@runtime_checkable
class PydanticCompatible(Protocol):
    """A protocol for classes that can be used as pydantic models."""

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: type, handler: pydantic.GetCoreSchemaHandler
    ) -> pydantic_core.core_schema.CoreSchema: ...


class CustomModel(PydanticCompatible, metaclass=abc.ABCMeta):
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
