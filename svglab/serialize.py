from __future__ import annotations

import re
from types import TracebackType
from typing import (
    Final,
    Literal,
    Protocol,
    TypeAlias,
    overload,
    runtime_checkable,
)

import pydantic
import readable_number

from svglab import models

ColorSerializationMode: TypeAlias = Literal[
    "named",
    "hex-short",
    "hex-long",
    "rgb",
    "hsl",
    "auto",
    "original",
]
""" Mode for serializing colors.

- `named`: Serialize colors using their named representation, if possible.
            Falls back to `hex-short`.
- `hex-short`: Serialize colors using the short hex format
            (for example, `#fff`).
- `hex-long`: Serialize colors using the long hex format
            (for example, `#ffffff`).
- `rgb`: Serialize colors using the RGB format
            (for example, `rgb(255, 255, 255)`).
- `hsl`: Serialize colors using the HSL format
            (for example, `hsl(0, 0%, 100%)`).
- `auto`: Automatically choose the most appropriate serialization mode.
- `original`: Serialize colors using their original representation,
            if possible. Falls back to `auto`.
"""

ListSeparator: TypeAlias = Literal[", ", ",", " "]
""" Type for basic valid separators for lists of values. """


@runtime_checkable
class Serializable(Protocol):
    """Protocol for objects with special serialization behavior.

    When a `Serializable` object is serialized, its `serialize()` method is
    used to obtain the string representation, instead of using `str()`.
    """

    def serialize(self) -> str:
        """Return an SVG-friendly string representation of this object."""


class Formatter(models.BaseModel):
    """Formatter for serializing SVG elements.

    This class, together with `set_formatter()` and `get_current_formatter()`,
    can be used to customize the serialization of SVG elements.

    Attributes:
    `color_mode`: The color serialization mode (`hsl`, `rgb`, ...)
    to use when serializing colors.

    `show_decimal_part_if_int`: Whether to show the decimal part of a number
    even if it is an integer. For example, `1.0` instead of `1`.
    `max_precision`: The maximum number of significant digits
    after the decimal point to use when serializing numbers.
    `small_number_scientific_threshold`: The magnitude threshold below which
    numbers are serialized using scientific notation.
    For example, `1e-06` instead of `0.000001`. If `None`, scientific notation
    is not used for small numbers.
    `large_number_scientific_threshold`: The magnitude threshold above which
    numbers are serialized using scientific notation.
    For example, `1e+06` instead of `1000000`. If `None`, scientific notation
    is not used for large numbers.

    `indent`: The number of spaces to use for indentation in the resulting
    SVG document.
    `list_separator`: The separator to use when serializing lists of values.
    `spaces_around_attrs`: Whether to add spaces around attribute values.
    For example, `fill=" red "` instead of `fill="red"`.
    `spaces_around_function_args`: Whether to add spaces around function
    arguments. For example, `rotate( 45 )` instead of `rotate(45)`.

    """

    model_config = pydantic.ConfigDict(frozen=True)

    # colors
    color_mode: models.KwOnly[ColorSerializationMode] = "auto"

    # numbers
    show_decimal_part_if_int: models.KwOnly[bool] = False
    max_precision: models.KwOnly[int | None] = pydantic.Field(
        default=None, ge=0
    )
    small_number_scientific_threshold: models.KwOnly[float | None] = (
        pydantic.Field(default=1e-6, ge=0)
    )
    large_number_scientific_threshold: models.KwOnly[float | None] = (
        pydantic.Field(default=1e6, ge=0)
    )

    # misc
    indent: models.KwOnly[int] = pydantic.Field(default=2, ge=0)
    list_separator: models.KwOnly[ListSeparator] = ", "
    spaces_around_attrs: models.KwOnly[bool] = False
    spaces_around_function_args: models.KwOnly[bool] = False

    __original_formatter: Formatter | None = pydantic.PrivateAttr(
        default=None
    )

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
                "Cannot exit unentered context manager.",
                " Call `__enter__` first",
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
    """Format a number or a sequence of numbers for SVG serialization.

    Args:
    numbers: The numbers to format.

    Returns:
    The formatted number or numbers.

    Examples:
    >>> format_number(42)
    '42'
    >>> format_number(3.14)
    '3.14'
    >>> format_number(1, 2, 3)
    ('1', '2', '3')
    >>> format_number(1.0, 2.0, 3.0)
    ('1', '2', '3')
    >>> format_number(1e9)
    '1e+09'

    """
    formatter = get_current_formatter()

    rn = readable_number.ReadableNumber(
        digit_group_delimiter="",  # group separators are not allowed in SVG
        significant_figures_after_decimal_point=formatter.max_precision,
        show_decimal_part_if_integer=formatter.show_decimal_part_if_int,
        use_exponent_for_small_numbers=(
            formatter.small_number_scientific_threshold is not None
        ),
        small_number_threshold=formatter.small_number_scientific_threshold,
        use_exponent_for_large_numbers=(
            formatter.large_number_scientific_threshold is not None
        ),
        large_number_threshold=formatter.large_number_scientific_threshold,
    )

    result = tuple(rn.of(number) for number in numbers)

    return result[0] if len(result) == 1 else result


def _serialize_attr(value: object, /) -> str:
    formatter = get_current_formatter()

    match value:
        case Serializable():
            result = value.serialize()

            if (
                formatter.spaces_around_function_args
                and (fn_call := extract_function_name_and_args(result))
                is not None
            ):
                fn, args = fn_call
                return f"{fn}( {args} )"

            return result

        case list() | tuple():
            return formatter.list_separator.join(
                _serialize_attr(item) for item in value
            )
        case int() | float():
            return format_number(value)
        case _:
            return str(value)


def serialize_attr(value: object, /) -> str:
    """Serialize an attribute value into its SVG representation.

    Args:
    value: The value to serialize.

    Returns:
    The SVG representation of the value.

    Examples:
    >>> serialize_attr(42)
    '42'
    >>> serialize_attr(3.14)
    '3.14'
    >>> serialize_attr("foo")
    'foo'
    >>> serialize_attr(["foo", "bar"])
    'foo, bar'

    """
    formatter = get_current_formatter()
    result = _serialize_attr(value)

    if formatter.spaces_around_attrs:
        result = f" {result} "

    return result


def extract_function_name_and_args(
    attr: str,
) -> tuple[str, str] | None:
    """Extract function name and arguments from a function-call-like attribute.

    An attribute is considered to be a function call if it has the form
    `name(args)`. This function extracts the name and the arguments from such
    an attribute. If the attribute is not a function call, `None` is returned.

    Args:
    attr: The attribute to extract the function name and arguments from.

    Returns:
    A tuple containing the function name and the arguments,
    or `None` if the attribute is not a function call.

    Examples:
    >>> extract_function_name_and_args("foo()") is None  # no arguments
    True
    >>> extract_function_name_and_args("foo(42)")
    ('foo', '42')
    >>> extract_function_name_and_args("foo(42, 'bar')")
    ('foo', "42, 'bar'")
    >>> extract_function_name_and_args(
    ...     "bar"
    ... ) is None  # not a function call
    True

    """
    match = re.match(r"^([^\(\)]+)\(([^\(\)]+)\)$", attr)

    if match is None:
        return None

    return match.group(1), match.group(2)
