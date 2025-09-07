"""Utilities for working with Pydantic."""

import copy
import functools
import re
import reprlib
from collections.abc import Callable

import pydantic
from typing_extensions import (
    Annotated,
    Final,
    TypeAlias,
    TypeVar,
    override,
)


_T = TypeVar("_T")
_T_co = TypeVar("_T_co", covariant=True)
_ListOrTupleT = TypeVar("_ListOrTupleT", list[str], tuple[str])
_BaseModelT = TypeVar("_BaseModelT", bound=pydantic.BaseModel)

_T1 = TypeVar("_T1")
_T2 = TypeVar("_T2")
_T3 = TypeVar("_T3")
_T4 = TypeVar("_T4")


Attr: TypeAlias = _T_co | None
""" Pydantic field for an attribute. """


DATACLASS_CONFIG: Final = pydantic.ConfigDict(
    extra="forbid",
    strict=True,
    validate_default=True,
    validate_assignment=True,
    validate_return=True,
)


def convert(
    source: pydantic.BaseModel,
    target_type: type[_BaseModelT],
    *,
    strict: bool | None = None,
    deepcopy: bool = True,
) -> _BaseModelT:
    """Convert a pydantic model to another pydantic model.

    Fields that are defined on both models are copied over. If the source model
    has extra fields, they are included in the new model as well. Other fields
    are discarded.

    If `deepcopy` is set to `False`, the source model instance should not be
    used after the conversion, as the new model will hold references to the
    source model's fields.

    Args:
        source: The source model to convert.
        target_type: The target model type.
        strict: Whether to use pydantic's strict mode when instantiating the
                new model.
        deepcopy: Whether to create deep copies of the fields.

    Returns:
        The converted model.

    """
    common_fields = (
        source.model_fields.keys() & target_type.model_fields.keys()
    )

    data = {field: getattr(source, field) for field in common_fields}

    if source.model_extra is not None:
        data |= source.model_extra

    target = target_type.model_validate(data, strict=strict)

    return copy.deepcopy(target) if deepcopy else target


def _parse_list(
    text: str, /, collection: type[_ListOrTupleT] = list
) -> _ListOrTupleT:
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


def _get_validator(
    func: Callable[[str], object], /
) -> pydantic.BeforeValidator:
    def validator(value: object) -> object:
        return func(value) if isinstance(value, str) else value

    return pydantic.BeforeValidator(validator)


List: TypeAlias = Annotated[
    list[_T],
    _get_validator(functools.partial(_parse_list, collection=list)),
]
"""Pydantic field for a list of strings. Uses `_parse_list` as a validator."""

Tuple: TypeAlias = Annotated[
    _T, _get_validator(functools.partial(_parse_list, collection=tuple))
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
