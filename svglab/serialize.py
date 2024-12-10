from __future__ import annotations

from types import TracebackType
from typing import Final, Literal, TypeAlias, overload

import pydantic

from svglab import models, utils

ColorSerializationMode: TypeAlias = Literal[
    "named",
    "hex-short",
    "hex-long",
    "rgb",
    "hsl",
    "auto",
    "original",
]


class Formatter(models.BaseModel):
    """Formatter for serializing SVG elements.

    This class, together with `set_formatter()` and `get_current_formatter()`,
    can be used to customize the serialization of SVG elements.

    Attributes:
    max_precision: The maximum number of significant digits
    after the decimal point to use when serializing numbers.
    color_mode: The color serialization mode (`hsl`, `rgb`, ...)
    to use when serializing colors.
    indent: The number of spaces to use for indentation in the resulting SVG document.

    """

    model_config = pydantic.ConfigDict(frozen=True, **models.MODEL_CONFIG)

    max_precision: models.KwOnly[int | None] = pydantic.Field(default=None, ge=0)
    color_mode: models.KwOnly[ColorSerializationMode] = "auto"
    indent: models.KwOnly[int] = pydantic.Field(default=2, ge=0)

    __original_formatter: Formatter | None = pydantic.PrivateAttr(default=None)

    def __enter__(self) -> None:
        self.__original_formatter = get_current_formatter()
        set_formatter(self)

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        del exc_type, exc_val, exc_tb

        if self.__original_formatter is None:
            msg = (
                "Cannot exit unentered context manager."
                f" Call `__enter__` first or use `with {type(self).__name__}()`."
            )
            raise RuntimeError(msg)

        set_formatter(self.__original_formatter)


DEFAULT_FORMATTER: Final = Formatter()
"""The default formatter used by the library.
Use `set_formatter()` to set a custom one."""

_formatter = DEFAULT_FORMATTER


def get_current_formatter() -> Formatter:
    """Obtain a reference to the current formatter."""
    return _formatter


def set_formatter(formatter: Formatter) -> None:
    """Set the current formatter."""
    global _formatter  # noqa: PLW0603
    _formatter = formatter


@overload
def format_number(number: float, /) -> str: ...


@overload
def format_number(*numbers: float) -> tuple[str, ...]: ...


def format_number(*numbers: float) -> str | tuple[str, ...]:
    formatter = get_current_formatter()

    result = tuple(
        utils.format_number(number, max_precision=formatter.max_precision)
        for number in numbers
    )

    return result[0] if len(result) == 1 else result
