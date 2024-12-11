import reprlib
from typing import Annotated, TypeAlias, TypeVar

import pydantic
from pydantic import Field
from typing_extensions import Self, override

_T_co = TypeVar("_T_co", covariant=True)

KwOnly: TypeAlias = Annotated[_T_co, Field(kw_only=True)]
""" Pydantic field for a keyword-only argument. """

Attr: TypeAlias = KwOnly[_T_co | None]
""" Pydantic field for an attribute. """


class BaseModel(pydantic.BaseModel):
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
