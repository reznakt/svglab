import abc
import functools
import re
import reprlib
from collections.abc import Callable

import pydantic
import pydantic_core.core_schema
from pydantic import Field
from typing_extensions import (
    Annotated,
    Protocol,
    Self,
    TypeAlias,
    TypeVar,
    override,
    runtime_checkable,
)


_T = TypeVar("_T")
_T_co = TypeVar("_T_co", covariant=True)
_T_seq = TypeVar("_T_seq", list[str], tuple[str])

_T1 = TypeVar("_T1")
_T2 = TypeVar("_T2")
_T3 = TypeVar("_T3")
_T4 = TypeVar("_T4")

KwOnly: TypeAlias = Annotated[_T_co, Field(kw_only=True)]
""" Pydantic field for a keyword-only attribute. """

Attr: TypeAlias = KwOnly[_T_co | None]
""" Pydantic field for an attribute. """


def _parse_list(text: str, /, collection: type[_T_seq] = list) -> _T_seq:
    """Parse a string into a list of strings.

    Items are separated by whitespace or commas.

    Args:
        text: The string to parse.
        collection: The type of collection to return.

    Returns:
        A collection of strings.

    Examples:
        >>> _parse_list("a b c")
        ['a', 'b', 'c']
        >>> _parse_list("a, b, c")
        ['a', 'b', 'c']
        >>> _parse_list("a b, c")
        ['a', 'b', 'c']
        >>> _parse_list("a,b,c")
        ['a', 'b', 'c']
        >>> _parse_list("")
        []

    """
    result = (part for part in re.split(r"\s+|\s*,\s*", text) if part)
    return collection(result)


def get_validator(
    func: Callable[[str], object], /
) -> pydantic.BeforeValidator:
    def validator(value: object) -> object:
        if isinstance(value, str):
            return func(value)

        return value

    return pydantic.BeforeValidator(validator)


List: TypeAlias = Annotated[
    list[_T],
    get_validator(functools.partial(_parse_list, collection=list)),
]
"""Pydantic field for a list of strings. Uses `_parse_list` as a validator."""

Tuple: TypeAlias = Annotated[
    _T, get_validator(functools.partial(_parse_list, collection=tuple))
]
"""Pydantic field for a tuple of strings. Uses `_parse_list` as a validator."""

# unfortunately, there doesn't seem to be a better way to do this
# see https://github.com/python/typing/issues/779
Tuple1: TypeAlias = Tuple[tuple[_T1]]
Tuple2: TypeAlias = Tuple[tuple[_T1, _T2]]
Tuple3: TypeAlias = Tuple[tuple[_T1, _T2, _T3]]
Tuple4: TypeAlias = Tuple[tuple[_T1, _T2, _T3, _T4]]


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

    # patch pydantic's __repr__ so that is doesn't break on cyclic models
    # see https://github.com/pydantic/pydantic/issues/9424
    @reprlib.recursive_repr()
    @override
    def __repr__(self) -> str:
        return super().__repr__()

    @override
    def __str__(self) -> str:
        return repr(self)


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
