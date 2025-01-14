from __future__ import annotations

import contextlib
import re
from collections.abc import Generator, Iterable, MutableSequence

import pydantic
import readable_number
from typing_extensions import (
    Final,
    Literal,
    Protocol,
    TypeAlias,
    TypeIs,
    overload,
    runtime_checkable,
)

from svglab import models


_ColorMode: TypeAlias = Literal[
    "named", "hex-short", "hex-long", "rgb", "hsl", "auto", "original"
]
_Separator: TypeAlias = Literal[", ", ",", " "]
_BoolMode: TypeAlias = Literal["text", "number"]
_PathDataCoordinateMode: TypeAlias = Literal["relative", "absolute"]
_PathDataShorthandMode: TypeAlias = Literal["always", "never", "original"]
_PathDataCommandMode: TypeAlias = Literal["explicit", "implicit"]


@runtime_checkable
class CustomSerializable(Protocol):
    """Protocol for objects with special serialization behavior.

    When a `Serializable` object is serialized, its `serialize()` method is
    used to obtain the string representation, instead of using `str()`.
    """

    def serialize(self) -> str:
        """Return an SVG-friendly string representation of this object."""
        ...


Serializable: TypeAlias = (
    bool
    | int
    | float
    | str
    | CustomSerializable
    | Iterable["Serializable"]
)
""" Type for objects that can be serialized to a SVG-friendly string. """


def _is_serializable(value: object, /) -> TypeIs[Serializable]:
    return isinstance(
        value,
        bool
        | int
        | float
        | str
        | MutableSequence
        | tuple
        | CustomSerializable,
    )


@pydantic.dataclasses.dataclass(frozen=True)
class Formatter:
    """Formatter for serializing SVG elements.

    This class, together with `set_formatter()` and `get_current_formatter()`,
    can be used to customize the serialization of SVG elements.

    Attributes:
    `color_mode`: The color serialization mode (`hsl`, `rgb`, ...)
    to use when serializing colors:
        - `named`: Serialize colors using their named representation,
                    if possible. Falls back to `hex-short`.
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

    `path_data_coordinates`: The coordinate mode to use when serializing
    path data coordinates:
        - `relative`: Serialize coordinates as relative values (e.g. use
                    relative commands, for example, `l 10 10`).
        - `absolute`: Serialize coordinates as absolute values (e.g., use
                    absolute commands, for example, `L 10 10`).

    `path_data_shorthand_line_commands`: Whether to use shorthand commands
    for line segments in path data:
        - `always`: Always use shorthand commands (e.g., `H` instead of
                    `L`).
        - `never`: Never use shorthand commands.
        - `original`: Use the original commands.

    `path_data_shorthand_curve_commands`: Whether to use shorthand commands
    for curve segments in path data:
        - `always`: Always use shorthand commands (e.g., `S` instead of
                    `C`).
        - `never`: Never use shorthand commands.
        - `original`: Use the original commands.

    `path_data_commands`: The command mode to use when serializing path data:
        - `implicit`: Serialize path data using implicit commands,
                    if possible. For example, `M 0 0 10 10` instead of
                    `M 0 0 L 10 10`.
        - `explicit`: Always list the commands explicitly.

    `path_data_space_before_args`: Whether to add a space before the arguments
    in path data commands. For example, `M 0 0` instead of `M0 0`.

    `list_separator`: The separator to use when serializing lists of values.
    `point_separator`: The separator to use when serializing points.

    `indent`: The number of spaces to use for indentation in the resulting
    SVG document.
    `spaces_around_attrs`: Whether to add spaces around attribute values.
    For example, `fill=" red "` instead of `fill="red"`.
    `spaces_around_function_args`: Whether to add spaces around function
    arguments. For example, `rotate( 45 )` instead of `rotate(45)`.

    """

    # colors
    color_mode: models.KwOnly[_ColorMode] = "auto"

    # numbers
    show_decimal_part_if_int: models.KwOnly[bool] = False
    max_precision: models.KwOnly[int | None] = pydantic.Field(
        default=None, ge=0
    )
    small_number_scientific_threshold: models.KwOnly[float | None] = (
        pydantic.Field(default=1e-6, ge=0)
    )
    large_number_scientific_threshold: models.KwOnly[int | None] = (
        pydantic.Field(default=int(1e6), ge=0)
    )

    # path data
    path_data_coordinates: models.KwOnly[_PathDataCoordinateMode] = (
        "absolute"
    )
    path_data_shorthand_line_commands: models.KwOnly[
        _PathDataShorthandMode
    ] = "always"
    path_data_shorthand_curve_commands: models.KwOnly[
        _PathDataShorthandMode
    ] = "always"
    path_data_commands: models.KwOnly[_PathDataCommandMode] = "implicit"
    path_data_space_before_args: models.KwOnly[bool] = False

    # separators
    list_separator: models.KwOnly[_Separator] = " "
    point_separator: models.KwOnly[_Separator] = ","

    # whitespace
    indent: models.KwOnly[int] = pydantic.Field(default=2, ge=0)
    spaces_around_attrs: models.KwOnly[bool] = False
    spaces_around_function_args: models.KwOnly[bool] = False


DEFAULT_FORMATTER: Final = Formatter()
"""The default formatter used by the library.
Use `set_formatter()` to set a custom one."""

_formatter = DEFAULT_FORMATTER


def get_current_formatter() -> Formatter:
    """Obtain a reference to the current formatter."""
    return _formatter


def set_formatter(formatter: Formatter, /) -> None:
    """Set the current formatter."""
    global _formatter  # noqa: PLW0603
    _formatter = formatter


@contextlib.contextmanager
def use_formatter(formatter: Formatter, /) -> Generator[None]:
    """Temporarily use a custom formatter."""
    original_formatter = get_current_formatter()
    set_formatter(formatter)

    try:
        yield
    finally:
        set_formatter(original_formatter)


@overload
def _serialize_number(number: float, /) -> str: ...


@overload
def _serialize_number(
    first: float, second: float, /, *numbers: float
) -> tuple[str, ...]: ...


def _serialize_number(*numbers: float) -> str | tuple[str, ...]:
    """Format a number or a sequence of numbers for SVG serialization.

    Args:
    numbers: The numbers to format.

    Returns:
    The formatted number or numbers.

    Examples:
    >>> _serialize_number(42)
    '42'
    >>> _serialize_number(3.14)
    '3.14'
    >>> _serialize_number(1, 2, 3)
    ('1', '2', '3')
    >>> _serialize_number(1.0, 2.0, 3.0)
    ('1', '2', '3')
    >>> _serialize_number(1e9)
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
        small_number_threshold=formatter.small_number_scientific_threshold
        or 0,
        use_exponent_for_large_numbers=(
            formatter.large_number_scientific_threshold is not None
        ),
        large_number_threshold=formatter.large_number_scientific_threshold
        or 0,
    )

    result = tuple(rn.of(number) for number in numbers)

    return result[0] if len(result) == 1 else result


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
    'foo bar'

    """
    if not _is_serializable(value):
        msg = f"Type {type(value)} is not serializable."
        raise TypeError(msg)

    formatter = get_current_formatter()
    result = serialize(value)

    if formatter.spaces_around_attrs:
        result = f" {result} "

    return result


def _extract_function_name_and_args(attr: str) -> tuple[str, str] | None:
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
    >>> _extract_function_name_and_args("foo()") is None  # no arguments
    True
    >>> _extract_function_name_and_args("foo(42)")
    ('foo', '42')
    >>> _extract_function_name_and_args("foo(42, 'bar')")
    ('foo', "42, 'bar'")
    >>> _extract_function_name_and_args(
    ...     "bar"
    ... ) is None  # not a function call
    True

    """
    match = re.match(r"^([^\(\)]+)\(([^\(\)]+)\)$", attr)

    if match is None:
        return None

    return match.group(1), match.group(2)


@overload
def serialize(
    value: Serializable, /, *, bool_mode: _BoolMode = "text"
) -> str: ...


@overload
def serialize(
    first: Serializable,
    second: Serializable,
    /,
    *values: Serializable,
    bool_mode: _BoolMode = "text",
) -> tuple[str, ...]: ...


def serialize(
    *values: Serializable, bool_mode: _BoolMode = "text"
) -> str | tuple[str, ...]:
    """Return an SVG-friendly string representation of the given value(s)."""
    result = tuple(
        _serialize(value, bool_mode=bool_mode) for value in values
    )
    return result[0] if len(result) == 1 else result


def _serialize(value: Serializable, /, *, bool_mode: _BoolMode) -> str:
    formatter = get_current_formatter()
    result: str

    match value:
        case CustomSerializable():
            result = value.serialize()

            if (
                formatter.spaces_around_function_args
                and (fn_call := _extract_function_name_and_args(result))
                is not None
            ):
                fn, args = fn_call
                result = f"{fn}( {args} )"
        # needs to be before int (bool is a subclass of int)
        case bool():
            result = _serialize_bool(value, mode=bool_mode)
        case int() | float():
            result = _serialize_number(value)
        case str():
            result = value
        case bytes():
            result = value.decode()
        # this should go last to avoid classifying strings as iterables, etc.
        case Iterable():
            result = formatter.list_separator.join(
                _serialize(v, bool_mode=bool_mode) for v in value
            )

    return result


def _serialize_bool(
    value: bool,  # noqa: FBT001
    /,
    *,
    mode: _BoolMode,
) -> str:
    """Serialize a boolean value into its SVG representation.

    Args:
    value: The boolean value to serialize.
    mode: The serialization mode to use. Can be either "text" or "number".
    If set to "text", the value is serialized as "true" or "false".
    If set to "number", the value is serialized as "1" or "0".

    Returns:
    The SVG representation of the boolean value.

    Examples:
    >>> _serialize_bool(True, mode="text")
    'true'
    >>> _serialize_bool(False, mode="text")
    'false'
    >>> _serialize_bool(True, mode="number")
    '1'
    >>> _serialize_bool(False, mode="number")
    '0'

    """
    match mode:
        case "text":
            return "true" if value else "false"
        case "number":
            return "1" if value else "0"
