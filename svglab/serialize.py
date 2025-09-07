"""Serialization of Python objects into SVG-friendly strings.

This module provides mechanisms to serialize various Python objects into
SVG-friendly strings.

The main components of this module are:
- `Formatter`: A dataclass for configuring the serialization settings.
- `serialize()`: A function that serializes a single value or multiple
  values into SVG-friendly strings.
- `get_current_formatter()` and `set_formatter()`: Functions to manage the
    current formatter.
"""

from __future__ import annotations

import functools
import math
import operator
import threading
from collections.abc import Iterable, Mapping, Sequence
from types import TracebackType

import pydantic
from typing_extensions import (
    Annotated,
    Final,
    Literal,
    Self,
    TypeAlias,
    cast,
    final,
    overload,
)

from svglab import constants, models, protocols, utiltypes
from svglab.attrs import names as attrs_names
from svglab.elements import names as elements_names
from svglab.utils import iterutils, miscutils


AlphaChannelMode: TypeAlias = Literal["percentage", "float"]

_BoolMode: TypeAlias = Literal["text", "number"]
_ColorMode: TypeAlias = Literal[
    "named", "hex-short", "hex-long", "rgb", "hsl", "auto", "original"
]
_PathDataShorthandMode: TypeAlias = Literal["always", "never", "original"]
_LengthUnitMode: TypeAlias = Literal["preserve"] | utiltypes.LengthUnit
_Separator: TypeAlias = Literal[", ", ",", " "]


_Interval: TypeAlias = tuple[float, float]
_Precision: TypeAlias = Annotated[int, pydantic.Field(le=15)]
_PrecisionGroup: TypeAlias = Literal[
    "general", "coordinate", "opacity", "angle", "scale"
]
_PrecisionTable: TypeAlias = Mapping[_Interval, _Precision]
_SortedPrecisionTable: TypeAlias = Iterable[tuple[_Interval, _Precision]]

_FORMATTER_LOCK: Final = threading.RLock()


@pydantic.dataclasses.dataclass(
    frozen=True, kw_only=True, config=models.DATACLASS_CONFIG
)
class FloatPrecisionSettings:
    """Settings regarding float precision.

    This class is used to define the precision settings for floating-point
    numbers in SVG serialization.

    If you don't need to define a precision table, you can just use the
    more convenient `float_precision()` function.
    """

    precision_table: _PrecisionTable = pydantic.Field(default_factory=dict)

    fallback: _Precision = math.ceil(
        math.log10(1 / constants.FLOAT_ABSOLUTE_TOLERANCE)
    )
    """
    A dictionary mapping intervals of floating-point
    numbers to their respective precision settings. The keys are tuples
    representing the start and end of the interval, and the values are
    integers representing the precision settings for that interval.
    The intervals are inclusive on the left and exclusive on the right.
    For example, it is possible to define a precision table like this:
    ```
    precision_table = {(0, 1): 2, (1, 10): 3}
    ```
    This means that numbers in the interval [0, 1) will be serialized with
    a precision of 2 digits, numbers in the interval [1, 10) will be
    serialized with a precision of 3 digits. All other numbers will be
    serialized with the fallback precision.
    """
    """The fallback precision setting to use when the value
    does not fall within any of the specified intervals."""

    @pydantic.model_validator(mode="after")
    def __validate_precision_table(self) -> Self:  # type: ignore[reportUnusedFunction]
        for start, end in self.precision_table:
            if not (0 <= start < end):
                msg = f"Invalid interval: {(start, end)}"
                raise ValueError(msg)

        for fst, snd in iterutils.pairwise(
            sorted(self.precision_table.keys())
        ):
            if fst is None:
                continue

            if fst[1] > snd[0]:
                msg = f"Overlapping intervals: {fst} and {snd}"
                raise ValueError(msg)

        return self

    @functools.cached_property
    def __sorted_precision_table(self) -> _SortedPrecisionTable:
        return sorted(
            self.precision_table.items(), key=operator.itemgetter(0)
        )

    def get_precision(self, value: float) -> int:
        """Get the number of decimal places to use for a given number.

        Args:
            value: The number to get the precision for.

        Returns:
            The number of decimal places to use when serializing the number.

        """
        return next(
            (
                precision
                for (
                    start,
                    end,
                ), precision in self.__sorted_precision_table
                if start <= abs(value) < end
            ),
            self.fallback,
        )


_FloatPrecisionSettingsType: TypeAlias = Annotated[
    FloatPrecisionSettings | _Precision | None,
    pydantic.AfterValidator(
        lambda v: v
        if v is None or isinstance(v, FloatPrecisionSettings)
        else FloatPrecisionSettings(fallback=v)
    ),
]


@final
@pydantic.dataclasses.dataclass(
    frozen=True, kw_only=True, config=models.DATACLASS_CONFIG
)
class Formatter:
    """Formatter for serializing SVG elements.

    This class, together with `set_formatter()` and `get_current_formatter()`,
    can be used to customize the serialization of SVG elements.

    The formatter can also be used with a context manager to temporarily
    change the serialization settings.
    """

    color_mode: _ColorMode = "auto"
    """
    The color serialization mode (`hsl`, `rgb`, ...) to use when serializing
    colors:
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
    """

    alpha_channel: AlphaChannelMode = "float"
    """
    The mode to use when serializing the alpha channel of colors:
    - `percentage`: Serialize the alpha channel as a percentage
                (for example, `rgba(255, 255, 255, 50%)`).
    - `float`: Serialize the alpha channel as a float
                (for example, `hsla(0, 0%, 100%, 0.5)`).
    """

    show_decimal_part_if_int: bool = False
    """
    Whether to show the decimal part of a number even if it is an integer.
    For example, `1.0` instead of `1`.
    """

    small_number_scientific_threshold: float | None = pydantic.Field(
        default=1e-6, gt=0, le=0.1
    )
    """The magnitude threshold below which numbers are serialized using
    scientific notation. For example, `1e-06` instead of `0.000001`. If
    `None`, scientific notation is not used for small numbers. Must be between
    0 (exclusive) and 0.1 (inclusive). Scientific notation is never used for 0.
    """

    large_number_scientific_threshold: int | None = pydantic.Field(
        default=int(1e6), gt=0
    )
    """
    The magnitude threshold above which numbers are serialized using
    scientific notation. For example, `1e+06` instead of `1000000`. If
    `None`, scientific notation is not used for large numbers. Must be greater
    than 0.
    """

    strip_leading_zero: bool = True
    """
    Whether to strip the leading zero from numbers between -1 and 1.
    For example, `.5` instead of `0.5`.
    """

    general_precision: _FloatPrecisionSettingsType = (
        FloatPrecisionSettings()
    )
    """
    The precision settings to use when serializing general numbers. This can be
    an integer that specifies the number of decimal places to use, or a
    `FloatPrecisionSettings` object.
    """

    coordinate_precision: _FloatPrecisionSettingsType = None
    """
    Settings to use when serializing coordinates. See `general_precision` for
    more details.
    """

    opacity_precision: _FloatPrecisionSettingsType = None
    """
    Settings to use when serializing opacity values. See `general_precision`
    for more details.
    """

    angle_precision: _FloatPrecisionSettingsType = None
    """
    Settings to use when serializing angles. See `general_precision` for more
    details.
    """

    scale_precision: _FloatPrecisionSettingsType = None
    """
    Settings to use when serializing scale values. See `general_precision` for
    more details.
    """

    path_data_coordinates: Literal["relative", "absolute"] = "absolute"
    """
    The coordinate mode to use when serializing path data coordinates:
    - `relative`: Serialize coordinates as relative values (e.g. use relative
                commands, for example, `l 10 10`).
    - `absolute`: Serialize coordinates as absolute values (e.g., use
                absolute commands, for example, `L 10 10`).
    """

    path_data_commands: Literal["explicit", "implicit"] = "implicit"
    """
    The command mode to use when serializing path data:
    - `implicit`: Serialize path data using implicit commands, if possible. For
                example, `M 0 0 10 10` instead of `M 0 0 L 10 10`.
    - `explicit`: Always list the commands explicitly.
    """

    path_data_shorthand_line_commands: _PathDataShorthandMode = "always"
    """
    Whether to use shorthand commands for line segments in path data:
    - `always`: Always use shorthand commands (e.g., `H` instead of `L`).
    - `never`: Never use shorthand commands.
    - `original`: Use the original commands.
    """

    path_data_shorthand_curve_commands: _PathDataShorthandMode = "always"
    """
    Whether to use shorthand commands for curve segments in path data:
    - `always`: Always use shorthand commands (e.g., `S` instead of `C`).
    - `never`: Never use shorthand commands.
    - `original`: Use the original commands.
    """

    path_data_space_before_args: bool = False
    """
    Whether to add a space before the arguments in path data commands. For
    example, `M 0 0` instead of `M0 0`.
    """

    list_separator: _Separator = " "
    """The separator to use when serializing lists of values."""

    point_separator: _Separator = ","
    """The separator to use when serializing points."""

    indent: int = pydantic.Field(default=2, ge=0)
    """
    The number of spaces to use for indentation in the resulting SVG document.
    """

    spaces_around_attrs: bool = False
    """
    Whether to add spaces around attribute values. For example,
    `fill=" red "` instead of `fill="red"`.
    """

    spaces_around_function_args: bool = False
    """
    Whether to add spaces around function arguments. For example,
    `rotate( 45 )` instead of `rotate(45)`.
    """

    xmlns: Literal["always", "never", "original"] = "original"
    """
    Whether to add, remove, or keep the `xmlns` attribute in the resulting SVG
    document:
    - `always`: Always add the `xmlns` attribute.
    - `never`: Always remove the `xmlns` attribute.
    - `original`: Serialize the `xmlns` attribute as-is.
    """

    length_unit: _LengthUnitMode | Iterable[_LengthUnitMode] = "preserve"
    """
    The length unit(s) to use when serializing lengths. If set to `preserve`,
    the original unit is used. If set to a specific unit, the length is
    converted to that unit. If set to an iterable of units, each unit is tried
    in order until one succeeds. If the length cannot be converted to any of
    the specified units, the original unit is used.
    """

    attribute_order: Mapping[
        elements_names.ElementName | Literal["*"],
        Sequence[attrs_names.AttributeName | str],
    ] = pydantic.Field(default_factory=dict)
    """
    How to order attributes in the resulting SVG document. The keys are the
    element names of the elements, and the values are lists of attribute names.
    The attributes are ordered in the order they appear in the lists. If an
    element name is `*`, the attribute order applies to all elements. If there
    is no configuration for a specific element-attribute pair, the default
    order (alphabetical) is used.
    """

    def get_precision(
        self, value: float, *, precision_group: _PrecisionGroup
    ) -> int:
        """Get the number of decimal places to use for a given number.

        The value is determined by the relevant settings in the formatter (
        `general_precision`, `coordinate_precision`, etc.), the precision group
        and the value itself.

        Args:
            value: The number to get the precision for.
            precision_group: The precision group to use when formatting
            the number.

        Returns:
            The number of decimal places to use when serializing the number.

        """
        settings: _FloatPrecisionSettingsType = None

        for group in precision_group, "general":
            name = f"{group}_precision"

            if (
                hasattr(self, name)
                and (attr := getattr(self, name)) is not None
            ):
                settings = attr
                break

        if settings is None:
            msg = (
                "Cannot determine floating point precision for "
                f"{value=}, {precision_group=}"
            )
            raise TypeError(msg)

        return cast(FloatPrecisionSettings, settings).get_precision(value)

    def __enter__(self) -> None:
        _FORMATTER_LOCK.acquire()

        try:
            object.__setattr__(
                self, "__original_formatter", get_current_formatter()
            )
            set_formatter(self)
        except:
            _FORMATTER_LOCK.release()
            raise

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        del exc_type, exc_val, exc_tb

        try:
            original_formatter: Formatter = object.__getattribute__(
                self, "__original_formatter"
            )
            set_formatter(original_formatter)
        finally:
            _FORMATTER_LOCK.release()


DEFAULT_FORMATTER: Final = Formatter()
"""The default formatter used by the library.
Use `set_formatter()` to set a custom one."""

MINIMAL_FORMATTER: Final = Formatter(
    color_mode="original",
    indent=4,
    large_number_scientific_threshold=None,
    path_data_coordinates="absolute",
    path_data_shorthand_curve_commands="original",
    path_data_shorthand_line_commands="original",
    small_number_scientific_threshold=None,
    spaces_around_attrs=False,
    spaces_around_function_args=False,
    strip_leading_zero=False,
    xmlns="always",
)
"""Formatter aimed at compatibility and performance."""


_formatter = DEFAULT_FORMATTER


def get_current_formatter() -> Formatter:
    """Obtain a reference to the current formatter."""
    with _FORMATTER_LOCK:
        return _formatter


def set_formatter(formatter: Formatter, /) -> None:
    """Set the current formatter."""
    with _FORMATTER_LOCK:
        global _formatter  # noqa: PLW0603
        _formatter = formatter


def _serialize_number(
    number: float, /, *, precision_group: _PrecisionGroup = "general"
) -> str:
    """Format a number into a string based on current formatter settings.

    Args:
    number: The number to format.
    precision_group: The precision group to use when formatting the number.

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
    >>> _serialize_number(0.123456789)
    '.123456789'
    >>> _serialize_number(1e-7)
    '1e-07'

    """
    formatter = get_current_formatter()

    # make sure the number is always a float and not an int, so that str()
    # always includes the decimal point
    number = float(number)
    number = round(
        number,
        formatter.get_precision(number, precision_group=precision_group),
    )

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


def _serialize(
    value: object,
    /,
    *,
    bool_mode: _BoolMode,
    precision_group: _PrecisionGroup,
) -> str:
    formatter = get_current_formatter()
    result: str

    match value:
        case protocols.CustomSerializable():
            result = value.serialize()
            formatter = get_current_formatter()

            if (
                formatter.spaces_around_function_args
                and (
                    fn_call := miscutils.extract_function_name_and_args(
                        result
                    )
                )
                is not None
            ):
                fn, args = fn_call
                result = f"{fn}( {args} )"
        # needs to be before int (bool is a subclass of int)
        case bool():
            result = _serialize_bool(value, mode=bool_mode)
        case int() | float():
            result = _serialize_number(
                value, precision_group=precision_group
            )
        case str():
            result = value
        case bytes():
            result = value.decode()
        # this should go last to avoid classifying strings as iterables, etc.
        case Iterable():
            formatter = get_current_formatter()
            result = formatter.list_separator.join(
                _serialize(
                    v, bool_mode=bool_mode, precision_group=precision_group
                )
                for v in value
            )
        case _:
            msg = f"Values of type {type(value)} are not serializable"
            raise TypeError(msg)

    return result


@overload
def serialize(
    value: object,
    /,
    *,
    bool_mode: _BoolMode = "text",
    precision_group: _PrecisionGroup = "general",
) -> str: ...


@overload
def serialize(
    first: object,
    second: object,
    /,
    *values: object,
    bool_mode: _BoolMode = "text",
    precision_group: _PrecisionGroup = "general",
) -> tuple[str, ...]: ...


def serialize(
    *values: object,
    bool_mode: _BoolMode = "text",
    precision_group: _PrecisionGroup = "general",
) -> str | tuple[str, ...]:
    """Return an SVG-friendly string representation of the given value(s)."""
    results = tuple(
        _serialize(
            value, bool_mode=bool_mode, precision_group=precision_group
        )
        for value in values
    )

    return results[0] if len(results) == 1 else results


def _get_attr_precision_group(
    name: attrs_names.AttributeName | str,
) -> _PrecisionGroup:
    match name:
        case (
            "opacity"
            | "fill-opacity"
            | "stroke-opacity"
            | "stop-opacity"
            | "flood-opacity"
        ):
            return "opacity"
        case _:
            return "general"


def serialize_attr(name: str, value: object) -> str:
    """Serialize an attribute into its SVG representation.

    Args:
    name: The name of the attribute.
    value: The value to serialize.

    Returns:
    The SVG representation of the value.

    """
    result = serialize(
        value, precision_group=_get_attr_precision_group(name)
    )
    formatter = get_current_formatter()

    if formatter.spaces_around_attrs:
        result = f" {result} "

    return result


def serialize_function_call(
    name: str, *args: object, precision_group: _PrecisionGroup = "general"
) -> str:
    """Serialize a function call into its SVG representation.

    Args:
    name: The name of the function.
    args: The arguments to pass to the function. If an argument is `None`,
    it is omitted.
    precision_group: The precision group to use when formatting the arguments.

    Returns:
    The SVG representation of the function call.

    Examples:
    >>> serialize_function_call("rotate", 45)
    'rotate(45)'
    >>> serialize_function_call("translate", 10, 20)
    'translate(10 20)'
    >>> serialize_function_call("rgb", 255, None, 0, 128)
    'rgb(255 0 128)'

    """
    args_str = serialize(
        (arg for arg in args if arg is not None),
        precision_group=precision_group,
    )

    return f"{name}({args_str})"


def serialize_path_command(
    *args: object,
    char: Literal["M", "L", "H", "V", "C", "S", "Q", "T", "A", "Z"],
    implicit: bool,
) -> str:
    """Serialize a path command.

    Args:
        args: The arguments of the command.
        char: The command character, in uppercase.
        implicit: Whether the command is implicit (i.e., the command character
        is omitted).

    Returns:
        The serialized command.

    Examples:
    >>> from svglab import Point
    >>> serialize_path_command(Point(10, 10), char="M", implicit=False)
    'M10,10'
    >>> serialize_path_command(Point(100, 100), char="L", implicit=True)
    '100,100'

    """
    formatter = get_current_formatter()
    parts: list[str] = []

    if not implicit:
        cmd = (
            char
            if formatter.path_data_coordinates == "absolute"
            else char.lower()
        )
        parts.append(cmd)

    if args:
        args_str = serialize(args, bool_mode="number")
        parts.append(args_str)

    sep = " " if formatter.path_data_space_before_args else ""

    return sep.join(parts)
