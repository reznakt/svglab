from __future__ import annotations

import abc
from collections.abc import Generator, Iterable, MutableSequence

import lark
import pydantic
import pydantic_core
from typing_extensions import (
    Annotated,
    Final,
    Literal,
    Protocol,
    Self,
    SupportsIndex,
    TypeAlias,
    cast,
    final,
    overload,
    override,
    runtime_checkable,
)

from svglab import models, serialize, utils
from svglab.attrparse import point
from svglab.attrparse import utils as parse_utils


_AbsolutePathCommandChar: TypeAlias = Literal[
    "M", "L", "H", "V", "C", "S", "Q", "T", "A", "Z"
]

_Flag: TypeAlias = Literal["0", "1"]


@pydantic.dataclasses.dataclass
class PathCommand:
    pass


@runtime_checkable
class _HasEnd(Protocol):
    end: point.Point


class _PhysicalPathCommand(
    PathCommand,
    _HasEnd,
    point.TwoDimensionalMovement["_PhysicalPathCommand"],
    metaclass=abc.ABCMeta,
):
    pass


@final
@pydantic.dataclasses.dataclass
class ClosePath(PathCommand):
    pass


@final
@pydantic.dataclasses.dataclass
class HorizontalLineTo(PathCommand):
    x: float


@final
@pydantic.dataclasses.dataclass
class VerticalLineTo(PathCommand):
    y: float


@final
@pydantic.dataclasses.dataclass
class SmoothQuadraticBezierTo(_PhysicalPathCommand):
    end: point.Point

    @override
    def __add__(self, other: point.Point, /) -> Self:
        return type(self)(end=self.end + other)


@final
@pydantic.dataclasses.dataclass
class SmoothCubicBezierTo(_PhysicalPathCommand):
    control2: point.Point
    end: point.Point

    @override
    def __add__(self, other: point.Point, /) -> Self:
        return type(self)(
            control2=self.control2 + other, end=self.end + other
        )


@final
@pydantic.dataclasses.dataclass
class MoveTo(_PhysicalPathCommand):
    end: point.Point

    @override
    def __add__(self, other: point.Point, /) -> Self:
        return type(self)(end=self.end + other)


@pydantic.dataclasses.dataclass
class LineTo(_PhysicalPathCommand):
    end: point.Point

    @override
    def __add__(self, other: point.Point, /) -> Self:
        return type(self)(end=self.end + other)


@final
@pydantic.dataclasses.dataclass
class QuadraticBezierTo(_PhysicalPathCommand):
    control: point.Point
    end: point.Point

    @override
    def __add__(self, other: point.Point, /) -> Self:
        return type(self)(
            control=self.control + other, end=self.end + other
        )


@final
@pydantic.dataclasses.dataclass
class CubicBezierTo(_PhysicalPathCommand):
    control1: point.Point
    control2: point.Point
    end: point.Point

    @override
    def __add__(self, other: point.Point, /) -> Self:
        return type(self)(
            control1=self.control1 + other,
            control2=self.control2 + other,
            end=self.end + other,
        )


@final
@pydantic.dataclasses.dataclass
class ArcTo(_PhysicalPathCommand):
    radius: point.Point
    angle: float
    large: bool
    sweep: bool
    end: point.Point

    @override
    def __add__(self, other: point.Point, /) -> Self:
        return type(self)(
            radius=self.radius + other,
            angle=self.angle,
            large=self.large,
            sweep=self.sweep,
            end=self.end + other,
        )


def _get_end(d: D, command: PathCommand) -> point.Point:
    """Get the end point of a path command.

    For commands that have a set end point, this function returns the end
    point. For commands that do not have a set end point, this function
    calculates the end point based on the previous command.

    Args:
        d: The path containing the command.
        command: The command to get the end point of.

    Returns:
        The end point of the command.

    Examples:
    >>> d = D().from_str("M 10,10 H 100 V 100 Z")
    >>> _get_end(d, d[0])
    Point(x=10.0, y=10.0)
    >>> _get_end(d, d[1])
    Point(x=100.0, y=10.0)

    """
    match command:
        case _PhysicalPathCommand(end=end):
            return end
        case ClosePath():
            return _get_end(d, utils.prev(d, command))
        case HorizontalLineTo(x=x):
            end = _get_end(d, utils.prev(d, command))
            return point.Point(x=x, y=end.y)
        case VerticalLineTo(y=y):
            end = _get_end(d, utils.prev(d, command))
            return point.Point(x=end.x, y=y)
        case _:
            raise AssertionError  # this should never happen


def _quadratic_control(
    d: D, command: SmoothQuadraticBezierTo
) -> point.Point:
    """Compute the control point for a smooth quadratic Bézier command (`T`).

    The control point is calculated based on the previous command. If the
    previous command is a quadratic Bézier command (`Q`), the control point
    is the reflection of the previous control point across the end point of
    the previous command. If the previous command is of any other type, the
    control point is coincident with the end point of the previous command.

    Args:
        d: The path containing the command.
        command: The smooth quadratic Bézier command.

    Returns:
        The control point for the command.

    Examples:
    >>> d = D().from_str("M 0,0 Q 20,0 20,20 T 40,40")
    >>> _quadratic_control(d, d[2])
    Point(x=20.0, y=40.0)

    """
    prev = utils.prev(d, command)
    end = _get_end(d, prev)

    match prev:
        case QuadraticBezierTo(control=control):
            pass
        case SmoothQuadraticBezierTo():
            control = _quadratic_control(d, prev)
        case _:
            return end

    return control.line_reflect(end)


def _cubic_control(d: D, command: SmoothCubicBezierTo) -> point.Point:
    """Compute the first control point for a smooth cubic Bézier command (`S`).

    The control point is calculated based on the previous command. If the
    previous command is a cubic Bézier command (`C`), the control point is the
    reflection of the second control point of the previous command across the
    end point of the previous command. If the previous command is of any other
    type, the control point is coincident with the end point of the previous
    command.

    Args:
        d: The path containing the command.
        command: The smooth cubic Bézier command.

    Returns:
        The first control point for the command.

    Examples:
    >>> d = D().from_str("M 0,0 C 20,0 20,20 40,40 S 100,100 50,50")
    >>> _cubic_control(d, d[2])
    Point(x=60.0, y=60.0)

    """
    prev = utils.prev(d, command)
    end = _get_end(d, prev)

    if isinstance(prev, CubicBezierTo | SmoothCubicBezierTo):
        return prev.control2.line_reflect(end)

    return end


def _apply_mode(d: D) -> D:
    formatter = serialize.get_current_formatter()
    result = D()
    pos = point.Point.zero()

    for command in d:
        match formatter.path_data_mode:
            case "relative":
                if isinstance(command, _PhysicalPathCommand):
                    # TODO: this cast can be removed fairly easily
                    result.append(cast(PathCommand, command - pos))
                else:
                    result.append(command)
            case "absolute":
                result.append(command)

        pos = _get_end(d, command)

    return result


@final
class D(
    MutableSequence[PathCommand],
    point.TwoDimensionalMovement["D"],
    models.CustomModel,
    serialize.CustomSerializable,
):
    """A class representing the `d` attribute of a path element.

    The `d` attribute is used to define a path in SVG. This class provides
    methods for building a path by adding commands. `D` is also
    a `MutableSequence` of `PathCommand` instances.

    Args:
        iterable: An iterable of `PathCommand` instances (for example,
        another `D` instance).
        start: The starting point of the path. If `start` is not `None`, a
        `MoveTo` command is automatically added to the path, moving the "pen"
        to the starting point.

    Examples:
    >>> d = (
    ...     D()
    ...     .move_to(point.Point(10, 10))
    ...     .line_to(point.Point(100, 100), relative=True)
    ... )
    >>> d
    D(MoveTo(end=Point(x=10.0, y=10.0)), LineTo(end=Point(x=110.0, y=110.0)))
    >>> len(d)
    2
    >>> bool(d)
    True
    >>> d[0]
    MoveTo(end=Point(x=10.0, y=10.0))
    >>> d.pop()
    LineTo(end=Point(x=110.0, y=110.0))
    >>> d.close()
    D(MoveTo(end=Point(x=10.0, y=10.0)), ClosePath())
    >>> d.serialize()
    'M 10,10 Z'

    """

    def __init__(
        self,
        iterable: Iterable[PathCommand] = (),
        /,
        *,
        start: point.Point | None = None,
    ) -> None:
        self.__commands: Final[list[PathCommand]] = []

        if start is not None:
            self.move_to(start)

        for command in iterable:
            self.__add(command)

    @override
    def __add__(self, other: point.Point) -> Self:
        return type(self)(
            command + other
            if isinstance(command, _PhysicalPathCommand)
            else command
            for command in self
        )

    @override
    def __len__(self) -> int:
        return len(self.__commands)

    @override
    def __eq__(self, other: object) -> bool:
        if not utils.basic_compare(other, self=self):
            return False

        if len(self) != len(other):
            return False

        return all(c1 == c2 for c1, c2 in zip(self, other, strict=True))

    @overload
    def __getitem__(self, index: int) -> PathCommand: ...

    @overload
    def __getitem__(self, index: slice) -> Self: ...

    @override
    def __getitem__(self, index: int | slice) -> PathCommand | Self:
        if isinstance(index, SupportsIndex):
            return self.__commands[index]

        return type(self)(self.__commands[index])

    @overload
    def __delitem__(self, index: int) -> None: ...

    @overload
    def __delitem__(self, index: slice) -> None: ...

    @override
    def __delitem__(self, index: int | slice) -> None:
        if isinstance(index, SupportsIndex):
            del self.__commands[index]
        else:
            del self.__commands[index]

    @overload
    def __setitem__(self, index: int, values: PathCommand) -> None: ...

    @overload
    def __setitem__(
        self, index: slice, values: Iterable[PathCommand]
    ) -> None: ...

    @override
    def __setitem__(
        self,
        index: int | slice,
        values: PathCommand | Iterable[PathCommand],
    ) -> None:
        if isinstance(index, SupportsIndex):
            assert isinstance(values, PathCommand)
            self.__commands[index] = values
        else:
            assert isinstance(values, Iterable)
            self.__commands[index] = values

    @override
    def insert(self, index: SupportsIndex, value: PathCommand) -> None:
        self.__commands.insert(index, value)

    def __add(
        self, command: PathCommand, *, relative: bool = False
    ) -> Self:
        if not self and not isinstance(command, MoveTo):
            raise ValueError("The first command must be a MoveTo command")

        if relative and isinstance(command, _PhysicalPathCommand):
            command += _get_end(self, self[-1])

        self.append(command)

        return self

    def move_to(
        self, end: point.Point, /, *, relative: bool = False
    ) -> Self:
        return self.__add(MoveTo(end=end), relative=relative)

    def line_to(
        self, end: point.Point, /, *, relative: bool = False
    ) -> Self:
        return self.__add(LineTo(end=end), relative=relative)

    def horizontal_line_to(
        self, x: float, /, *, relative: bool = False
    ) -> Self:
        return self.__add(HorizontalLineTo(x=x), relative=relative)

    def vertical_line_to(
        self, y: float, /, *, relative: bool = False
    ) -> Self:
        return self.__add(VerticalLineTo(y=y), relative=relative)

    def quadratic_bezier_to(
        self,
        control: point.Point,
        end: point.Point,
        /,
        *,
        relative: bool = False,
    ) -> Self:
        return self.__add(
            QuadraticBezierTo(control=control, end=end), relative=relative
        )

    def cubic_bezier_to(
        self,
        control1: point.Point,
        control2: point.Point,
        end: point.Point,
        *,
        relative: bool = False,
    ) -> Self:
        return self.__add(
            CubicBezierTo(control1=control1, control2=control2, end=end),
            relative=relative,
        )

    def arc_to(  # noqa: PLR0913
        self,
        radius: point.Point,
        angle: float,
        end: point.Point,
        *,
        large: bool,
        sweep: bool,
        relative: bool = False,
    ) -> Self:
        return self.__add(
            ArcTo(
                radius=radius,
                angle=angle,
                large=large,
                sweep=sweep,
                end=end,
            ),
            relative=relative,
        )

    def smooth_quadratic_bezier_to(
        self, end: point.Point, /, *, relative: bool = False
    ) -> Self:
        return self.__add(
            SmoothQuadraticBezierTo(end=end), relative=relative
        )

    def smooth_cubic_bezier_to(
        self,
        control2: point.Point,
        end: point.Point,
        /,
        *,
        relative: bool = False,
    ) -> Self:
        return self.__add(
            SmoothCubicBezierTo(control2=control2, end=end),
            relative=relative,
        )

    def close(self) -> Self:
        return self.__add(ClosePath())

    @override
    def __repr__(self) -> str:
        name = type(self).__name__
        commands = ", ".join(repr(command) for command in self)
        return f"{name}({commands})"

    @classmethod
    def from_str(cls, text: str) -> Self:
        d = parse_utils.parse(
            text, grammar="d.lark", transformer=_Transformer()
        )

        assert isinstance(d, cls), f"Expected {cls}, got {type(d)}"
        return d

    @classmethod
    def _validate(
        cls, value: object, info: pydantic_core.core_schema.ValidationInfo
    ) -> Self:
        del info

        match value:
            case str():
                return cls.from_str(value)
            case D():
                return cast(cls, value)
            case _:
                msg = f"Expected str or D, got {type(value)}"
                raise TypeError(msg)

    @staticmethod
    def __format_command(
        *args: serialize.Serializable, char: _AbsolutePathCommandChar
    ) -> str:
        formatter = serialize.get_current_formatter()

        cmd = (
            char
            if formatter.path_data_mode == "absolute"
            else char.lower()
        )

        if not args:
            return cmd

        args_str = serialize.serialize(args, bool_mode="number")
        return f"{cmd} {args_str}"

    def __apply_shorthand_formatting(self) -> D:
        formatter = serialize.get_current_formatter()
        line = formatter.path_data_use_shorthand_line_commands
        curve = formatter.path_data_use_shorthand_curve_commands

        d = self

        if "never" in (line, curve):
            d = d.resolve_shorthands(
                lines=line == "never", curves=curve == "never"
            )

        if "always" in (line, curve):
            d = d.apply_shorthands(
                lines=line == "always", curves=curve == "always"
            )

        return d

    def __serialize_commands(self) -> Generator[str, None, None]:  # noqa: C901
        d = self.__apply_shorthand_formatting()

        for command in _apply_mode(d):
            match command:
                case MoveTo(end):
                    yield self.__format_command(end, char="M")
                case LineTo(end):
                    yield self.__format_command(end, char="L")
                case HorizontalLineTo(x):
                    yield self.__format_command(x, char="H")
                case VerticalLineTo(y):
                    yield self.__format_command(y, char="V")
                case QuadraticBezierTo(control, end):
                    yield self.__format_command(control, end, char="Q")
                case SmoothQuadraticBezierTo(end):
                    yield self.__format_command(end, char="T")
                case CubicBezierTo(control1, control2, end):
                    yield self.__format_command(
                        control1, control2, end, char="C"
                    )
                case SmoothCubicBezierTo(control2, end):
                    yield self.__format_command(control2, end, char="S")
                case ArcTo(radius, angle, large, sweep, end):
                    yield self.__format_command(
                        radius, angle, large, sweep, end, char="A"
                    )
                case ClosePath():
                    yield self.__format_command(char="Z")
                case _:
                    msg = f"Unsupported command type: {type(command)}"
                    raise TypeError(msg)

    @override
    def serialize(self) -> str:
        return serialize.serialize(self.__serialize_commands())

    def resolve_shorthands(
        self, *, lines: bool = True, curves: bool = True
    ) -> Self:
        """Resolve shorthand commands into their full-length equivalents.

        Args:
            lines: Whether to resolve shorthand line commands (`H`, `V`) into
            the full-length equivalent (`L`).
            curves: Whether to resolve shorthand curve commands (`S`, `T`) into
            the full-length equivalent (`C`, `Q`).

        Returns:
            A new `D` instance with the shorthand commands (`H`, `V`, `S`, `T`)
            replaced by their full-length equivalents (`L`, `C`, `Q`).

        Examples:
        >>> d = D().from_str("M 10,10 H 100 V 100 S 100,100 50,50")
        >>> d.resolve_shorthands().serialize()
        'M 10,10 L 100,10 L 100,100 C 100,100 100,100 50,50'
        >>> d = D().from_str("M 0,0 Q 20,0 20,20 T 40,40")
        >>> d.resolve_shorthands().serialize()
        'M 0,0 Q 20,0 20,20 Q 20,40 40,40'

        """
        d = type(self)()

        for command in self:
            match command:
                case SmoothQuadraticBezierTo(end=end) if curves:
                    control = _quadratic_control(self, command)
                    d.quadratic_bezier_to(control, end)
                case SmoothCubicBezierTo(
                    control2=control2, end=end
                ) if curves:
                    control1 = _cubic_control(self, command)
                    d.cubic_bezier_to(control1, control2, end)
                case HorizontalLineTo(x=x) if lines:
                    end = _get_end(d, d[-1])
                    d.line_to(point.Point(x=x, y=end.y))
                case VerticalLineTo(y=y) if lines:
                    end = _get_end(d, d[-1])
                    d.line_to(point.Point(x=end.x, y=y))
                case _:
                    d.append(command)
        return d

    def apply_shorthands(
        self, *, lines: bool = True, curves: bool = True
    ) -> Self:
        """Convert full-length commands into shorthand commands where possible.

        Args:
            lines: Whether to convert line commands (`L`) to shorthand
            (`H`, `V`) where possible.
            curves: Whether to convert curve commands (`Q`, `C`) to shorthand
            (`T`, `S`) where possible.

        Returns:
            A new `D` instance with the full-length commands (`L`, `C`, `Q`)
            replaced by their shorthand equivalents (`H`, `V`, `S`, `T`).

        Examples:
        >>> d = D().from_str(
        ...     "M 10,10 L 100,10 L 100,100 C 100,100 100,100 50,50"
        ... )
        >>> d.apply_shorthands().serialize()
        'M 10,10 H 100 V 100 S 100,100 50,50'
        >>> d = D().from_str("M 0,0 Q 20,0 20,20 Q 20,40 40,40")
        >>> d.apply_shorthands().serialize()
        'M 0,0 Q 20,0 20,20 T 40,40'

        """
        d = type(self)()

        for command in self:
            match command:
                case LineTo(end=end) if lines and end.x == (
                    _get_end(d, d[-1]).x
                ):
                    d.vertical_line_to(end.y)
                case LineTo(end=end) if lines and end.y == (
                    _get_end(d, d[-1]).y
                ):
                    d.horizontal_line_to(end.x)
                case QuadraticBezierTo(control=control, end=end) if curves:
                    d.smooth_quadratic_bezier_to(end)

                    shorthand = d[-1]
                    assert isinstance(shorthand, SmoothQuadraticBezierTo)

                    # try to replace the command with a shorthand
                    auto_control = _quadratic_control(d, shorthand)

                    # if the shorthand turns out not to be compatible, revert
                    # to the original command
                    if control != auto_control:
                        d[-1] = command

                case CubicBezierTo(
                    control1=control1, control2=control2, end=end
                ) if curves:
                    d.smooth_cubic_bezier_to(control2, end)

                    shorthand = d[-1]
                    assert isinstance(shorthand, SmoothCubicBezierTo)

                    auto_control = _cubic_control(d, shorthand)

                    if control1 != auto_control:
                        d[-1] = command

                case _:
                    d.append(command)

        return d


@lark.v_args(inline=True)
@parse_utils.visit_tokens  # there are a few terminals we want to parse
class _Transformer(lark.Transformer[object, D]):
    point = point.Point
    NUMBER = float

    def FLAG(self, value: _Flag) -> bool:  # noqa: N802
        return value == "1"

    def arc(
        self,
        radius: point.Point,
        angle: float,
        large: bool,  # noqa: FBT001
        sweep: bool,  # noqa: FBT001
        end: point.Point,
    ) -> ArcTo:
        return ArcTo(
            radius=radius, angle=angle, large=large, sweep=sweep, end=end
        )

    cubic_bezier = CubicBezierTo
    horizontal_line = HorizontalLineTo
    line = LineTo
    move = MoveTo
    quadratic_bezier = QuadraticBezierTo
    smooth_cubic_bezier = SmoothCubicBezierTo
    smooth_quadratic_bezier = SmoothQuadraticBezierTo
    vertical_line = VerticalLineTo
    z = ClosePath

    segment_sequence = parse_utils.v_args_to_list

    a = parse_utils.v_args_to_list
    c = parse_utils.v_args_to_list
    h = parse_utils.v_args_to_list
    l = parse_utils.v_args_to_list
    m = parse_utils.v_args_to_list
    q = parse_utils.v_args_to_list
    s = parse_utils.v_args_to_list
    t = parse_utils.v_args_to_list
    v = parse_utils.v_args_to_list

    @lark.v_args(inline=False)
    def path(self, commands: list[PathCommand | lark.Tree[object]]) -> D:
        # our grammar is not set up ideally, so we need to filter out
        # some garbage
        # TODO: try to improve the grammar
        return D(
            command
            for command in utils.flatten(commands)
            if isinstance(command, PathCommand)
        )


DType: TypeAlias = Annotated[
    D,
    parse_utils.get_validator(
        grammar="d.lark", transformer=_Transformer()
    ),
]
