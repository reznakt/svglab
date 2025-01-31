from __future__ import annotations

import contextlib
import functools
import math
from collections.abc import Generator, Iterable

import pydantic
from typing_extensions import Final, Literal, TypeAlias, TypeIs, overload

from svglab import protocols, utils


_ColorMode: TypeAlias = Literal[
    "named", "hex-short", "hex-long", "rgb", "hsl", "auto", "original"
]
AlphaChannelMode: TypeAlias = Literal["percentage", "float"]
_Separator: TypeAlias = Literal[", ", ",", " "]
_BoolMode: TypeAlias = Literal["text", "number"]
_PathDataCoordinateMode: TypeAlias = Literal["relative", "absolute"]
_PathDataShorthandMode: TypeAlias = Literal["always", "never", "original"]
_PathDataCommandMode: TypeAlias = Literal["explicit", "implicit"]
_Xmlns: TypeAlias = Literal["always", "never", "original"]


Serializable: TypeAlias = (
    bool
    | int
    | float
    | str
    | protocols.CustomSerializable
    | Iterable["Serializable"]
)
""" Type for objects that can be serialized to a SVG-friendly string. """


def _is_serializable(value: object, /) -> TypeIs[Serializable]:
    return utils.is_type(value, Serializable)


@pydantic.dataclasses.dataclass(frozen=True, kw_only=True)
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

    `alpha_channel`: The mode to use when serializing the alpha
    channel of colors:
        - `percentage`: Serialize the alpha channel as a percentage
                    (for example, `rgba(255, 255, 255, 50%)`).
        - `float`: Serialize the alpha channel as a float
                    (for example, `hsla(0, 0%, 100%, 0.5)`).

    `show_decimal_part_if_int`: Whether to show the decimal part of a number
    even if it is an integer. For example, `1.0` instead of `1`.
    `max_precision`: The maximum number of digits
    after the decimal point to use when serializing numbers. Must be between 0
    and 15 (inclusive) due to the limitations of double-precision
    floating-point numbers (IEEE 754). The number is rounded to the nearest
    value.
    `small_number_scientific_threshold`: The magnitude threshold below which
    numbers are serialized using scientific notation.
    For example, `1e-06` instead of `0.000001`. If `None`, scientific notation
    is not used for small numbers. Must be between 0 (exclusive) and 0.1
    (inclusive). Scientific notation is never used for 0.
    `large_number_scientific_threshold`: The magnitude threshold above which
    numbers are serialized using scientific notation.
    For example, `1e+06` instead of `1000000`. If `None`, scientific notation
    is not used for large numbers. Must be greater than 0.
    `strip_leading_zero`: Whether to strip the leading zero from numbers
    between -1 and 1. For example, `.5` instead of `0.5`.

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

    `xmlns`: Whether to add, remove, or keep the `xmlns` attribute in the
    resulting SVG document:
        - `always`: Always add the `xmlns` attribute.
        - `never`: Always remove the `xmlns` attribute.
        - `original`: Serialize the `xmlns` attribute as-is.

    """

    # colors
    color_mode: _ColorMode = "auto"
    alpha_channel: AlphaChannelMode = "float"

    # numbers
    show_decimal_part_if_int: bool = False
    max_precision: int = pydantic.Field(default=15, ge=0, le=15)
    small_number_scientific_threshold: float | None = pydantic.Field(
        default=1e-6, gt=0, le=0.1
    )
    large_number_scientific_threshold: int | None = pydantic.Field(
        default=int(1e6), gt=0
    )
    strip_leading_zero: bool = True

    # path data
    path_data_coordinates: _PathDataCoordinateMode = "absolute"
    path_data_shorthand_line_commands: _PathDataShorthandMode = "always"
    path_data_shorthand_curve_commands: _PathDataShorthandMode = "always"
    path_data_commands: _PathDataCommandMode = "implicit"
    path_data_space_before_args: bool = False

    # separators
    list_separator: _Separator = " "
    point_separator: _Separator = ","

    # whitespace
    indent: int = pydantic.Field(default=2, ge=0)
    spaces_around_attrs: bool = False
    spaces_around_function_args: bool = False

    # misc
    xmlns: _Xmlns = "original"


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


def _serialize_number(number: float) -> str:
    """Format a number into a string based on current formatter settings.

    Args:
    number: The number to format.

    Returns:
    The formatted number as a string.

    Examples:
    >>> _serialize_number(42)
    '42'
    >>> _serialize_number(3.14)
    '3.14'
    >>> _serialize_number(1.0)
    '1'
    >>> _serialize_number(1e9)
    '1e+09'
    >>> _serialize_number(-0.1)
    '-.1'
    >>> _serialize_number(0.12345678912345679)
    '.123456789123457'
    >>> _serialize_number(1e-10)
    '1e-10'

    """
    formatter = get_current_formatter()

    # make sure the number is always a float and not an int, so that str()
    # always includes the decimal point
    number = float(number)

    number = round(float(number), formatter.max_precision)
    abs_value = abs(number)

    use_scientific = number != 0 and (
        (
            formatter.small_number_scientific_threshold is not None
            and abs_value <= formatter.small_number_scientific_threshold
        )
        or (
            formatter.large_number_scientific_threshold is not None
            and abs_value >= formatter.large_number_scientific_threshold
        )
    )

    exponent = 0

    # the mantissa gets formatted just like a regular number, at the end we add
    # the sign and the exponent
    if use_scientific:
        exponent = math.floor(math.log10(abs_value))
        number = abs_value / 10**exponent

    result = str(number)

    if not formatter.show_decimal_part_if_int:
        result = result.removesuffix(".0")

    sign = "-" if number < 0 else ""

    if formatter.strip_leading_zero and result.startswith(("0.", "-0.")):
        no_sign = result.removeprefix("-")
        result = sign + no_sign[1:]

    if use_scientific:
        exponent_sign = "-" if exponent < 0 else "+"
        exponent_str = str(abs(exponent)).zfill(2)
        result = f"{sign}{result}e{exponent_sign}{exponent_str}"

    return result


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


def _serialize(value: Serializable, /, *, bool_mode: _BoolMode) -> str:
    formatter = get_current_formatter()
    result: str

    match value:
        case protocols.CustomSerializable():
            result = value.serialize()

            if (
                formatter.spaces_around_function_args
                and (
                    fn_call := utils.extract_function_name_and_args(result)
                )
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


def serialize(
    *values: Serializable, bool_mode: _BoolMode = "text"
) -> str | tuple[str, ...]:
    """Return an SVG-friendly string representation of the given value(s)."""
    return utils.apply_single_or_many(
        functools.partial(_serialize, bool_mode=bool_mode), *values
    )


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
