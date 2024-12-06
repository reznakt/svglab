import reprlib
from typing import Annotated, TypeAlias, TypeVar

import pydantic
from pydantic import Field
from typing_extensions import Self

_T_co = TypeVar("_T_co", covariant=True)

Attr: TypeAlias = Annotated[_T_co | None, Field(kw_only=True)]
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

    def __copy__(self) -> Self:
        return self.model_copy(deep=False)

    def __deepcopy__(self, memo: dict[int, object] | None = None) -> Self:
        del memo
        return self.model_copy(deep=True)

    def __str__(self) -> str:
        return repr(self)

    # patch pydantic's __repr__ so that is doesn't break on cyclic models
    # see https://github.com/pydantic/pydantic/issues/9424
    @reprlib.recursive_repr()
    def __repr__(self) -> str:
        return super().__repr__()