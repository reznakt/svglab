from __future__ import annotations

import abc
from collections.abc import Generator, Iterable, Iterator, MutableSequence

import pydantic
import pydantic_core
import svgpathtools
from typing_extensions import (
    Final,
    Literal,
    Self,
    SupportsIndex,
    TypeAlias,
    final,
    overload,
    override,
)

from svglab import constants, models, serialize, utils
from svglab.attrparse import point


_AbsolutePathCommandChar: TypeAlias = Literal[
    "M", "L", "H", "V", "C", "S", "Q", "T", "A", "Z"
]

_SvgPathToolsCommand: TypeAlias = (
    svgpathtools.Arc
    | svgpathtools.CubicBezier
    | svgpathtools.Line
    | svgpathtools.QuadraticBezier
)


@pydantic.dataclasses.dataclass
class _PathCommandBase:
    d: D = pydantic.Field(frozen=True, kw_only=True, repr=False)

    def prev(self) -> PathCommand:
        index = self.d.index(self)

        return self.d[index - 1]

    def next(self) -> PathCommand | None:
        index = self.d.index(self)

        return self.d[index + 1] if index + 1 < len(self.d) else None


class PhysicalPathCommand(
    _PathCommandBase,
    point.Supports2DMovement["PhysicalPathCommand"],
    metaclass=abc.ABCMeta,
):
    end: point.Point


class VirtualPathCommand(_PathCommandBase, metaclass=abc.ABCMeta):
    @property
    def end(self) -> point.Point:
        return self.prev().end


@final
@pydantic.dataclasses.dataclass
class ClosePath(VirtualPathCommand):
    pass


@final
@pydantic.dataclasses.dataclass
class HorizontalLineTo(VirtualPathCommand):
    x: float

    @property
    @override
    def end(self) -> point.Point:
        return point.Point(self.x, self.prev().end.y)


@final
@pydantic.dataclasses.dataclass
class VerticalLineTo(VirtualPathCommand):
    y: float

    @property
    @override
    def end(self) -> point.Point:
        return point.Point(self.prev().end.x, self.y)


@final
@pydantic.dataclasses.dataclass
class MoveTo(PhysicalPathCommand):
    end: point.Point

    @override
    def __add__(self, other: point.Point, /) -> Self:
        return type(self)(end=self.end + other, d=self.d)

    @override
    def __sub__(self, other: point.Point, /) -> Self:
        return type(self)(end=self.end - other, d=self.d)


@pydantic.dataclasses.dataclass
class LineTo(PhysicalPathCommand):
    end: point.Point

    @override
    def __add__(self, other: point.Point, /) -> Self:
        return type(self)(end=self.end + other, d=self.d)

    @override
    def __sub__(self, other: point.Point, /) -> Self:
        return type(self)(end=self.end - other, d=self.d)


@final
@pydantic.dataclasses.dataclass
class QuadraticBezierTo(PhysicalPathCommand):
    control: point.Point
    end: point.Point

    @override
    def __add__(self, other: point.Point, /) -> Self:
        return type(self)(
            control=self.control + other, end=self.end + other, d=self.d
        )

    @override
    def __sub__(self, other: point.Point, /) -> Self:
        return type(self)(
            control=self.control - other, end=self.end - other, d=self.d
        )


@final
@pydantic.dataclasses.dataclass
class CubicBezierTo(PhysicalPathCommand):
    control1: point.Point
    control2: point.Point
    end: point.Point

    @override
    def __add__(self, other: point.Point, /) -> Self:
        return type(self)(
            control1=self.control1 + other,
            control2=self.control2 + other,
            end=self.end + other,
            d=self.d,
        )

    @override
    def __sub__(self, other: point.Point, /) -> Self:
        return type(self)(
            control1=self.control1 - other,
            control2=self.control2 - other,
            end=self.end - other,
            d=self.d,
        )


@final
@pydantic.dataclasses.dataclass
class ArcTo(PhysicalPathCommand):
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
            d=self.d,
        )

    @override
    def __sub__(self, other: point.Point, /) -> Self:
        return type(self)(
            radius=self.radius - other,
            angle=self.angle,
            large=self.large,
            sweep=self.sweep,
            end=self.end - other,
            d=self.d,
        )


PathCommand: TypeAlias = (
    ArcTo
    | ClosePath
    | CubicBezierTo
    | HorizontalLineTo
    | LineTo
    | QuadraticBezierTo
    | VerticalLineTo
    | MoveTo
)


@final
class D(
    MutableSequence[PathCommand],
    point.Supports2DMovement["D"],
    models.CustomModel,
    serialize.CustomSerializable,
):
    def __init__(
        self,
        iterable: Iterable[PathCommand] = (),
        /,
        *,
        start: point.Point | None = constants.DEFAULT_PATH_START,
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
            if isinstance(command, PhysicalPathCommand)
            else command
            for command in self
        )

    @override
    def __sub__(self, other: point.Point) -> Self:
        return type(self)(
            command - other
            if isinstance(command, PhysicalPathCommand)
            else command
            for command in self
        )

    @override
    def __len__(self) -> int:
        return len(self.__commands)

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

    @property
    def start(self) -> point.Point:
        return next(
            (cmd.end for cmd in self if not isinstance(cmd, MoveTo)),
            point.Point.zero(),
        )

    @property
    def end(self) -> point.Point:
        if not self:
            return point.Point.zero()

        return self[-1].end

    def __add(
        self, command: PathCommand, *, relative: bool = False
    ) -> Self:
        if not self and not isinstance(command, MoveTo):
            raise ValueError("The first command must be a MoveTo command")

        if relative and isinstance(command, PhysicalPathCommand):
            command += self.end

        self.append(command)

        return self

    def move_to(
        self, end: point.Point, /, *, relative: bool = False
    ) -> Self:
        return self.__add(MoveTo(end=end, d=self), relative=relative)

    def line_to(
        self, end: point.Point, /, *, relative: bool = False
    ) -> Self:
        return self.__add(LineTo(end=end, d=self), relative=relative)

    def horizontal_line_to(
        self, x: float, /, *, relative: bool = False
    ) -> Self:
        return self.__add(HorizontalLineTo(x=x, d=self), relative=relative)

    def vertical_line_to(
        self, y: float, /, *, relative: bool = False
    ) -> Self:
        return self.__add(VerticalLineTo(y=y, d=self), relative=relative)

    def quadratic_bezier_to(
        self,
        control: point.Point,
        end: point.Point,
        *,
        relative: bool = False,
    ) -> Self:
        return self.__add(
            QuadraticBezierTo(control=control, end=end, d=self),
            relative=relative,
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
            CubicBezierTo(
                control1=control1, control2=control2, end=end, d=self
            ),
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
                d=self,
            ),
            relative=relative,
        )

    def close(self) -> Self:
        return self.__add(ClosePath(d=self))

    def is_continuous(self) -> bool:
        """Determine whether the path is continuous.

        A continuous path is a path that does not contain any `MoveTo`
        commands in between other commands. A continuous path may contain
        leading or trailing `MoveTo` commands.

        Returns:
            `True` if the path is continuous, `False` otherwise.

        Examples:
            >>> d = D()
            >>> d.is_continuous()
            True
            >>> _ = d.move_to(point.Point(0, 0)).line_to(point.Point(1, 1))
            >>> d.is_continuous()
            True
            >>> _ = d.move_to(point.Point(2, 2)).line_to(point.Point(3, 3))
            >>> d.is_continuous()
            False

        """
        return utils.length(self.continuous_subpaths()) <= 1

    def __continuous_subpaths(self) -> Generator[D, None, None]:
        subpath = D()

        for command in self:
            if isinstance(command, MoveTo):
                yield subpath
                subpath = D()
            else:
                subpath.append(command)

        yield subpath

    def continuous_subpaths(self) -> Iterator[D]:
        """Iterate over the continuous subpaths of the path.

        A continuous subpath is a sequence of commands that form a single
        path without any `MoveTo` commands in between.

        Returns:
            An iterator over the continuous subpaths of the path.

        Examples:
            >>> d = D()
            >>> list(d.continuous_subpaths())
            []
            >>> _ = d.move_to(point.Point(0, 0)).line_to(point.Point(1, 1))
            >>> list(d.continuous_subpaths())
            [D(LineTo(end=Point(x=1.0, y=1.0)))]
            >>> _ = d.move_to(point.Point(2, 2)).line_to(point.Point(3, 3))
            >>> for subpath in d.continuous_subpaths():
            ...     print(subpath)
            D(LineTo(end=Point(x=1.0, y=1.0)))
            D(LineTo(end=Point(x=3.0, y=3.0)))

        """
        return filter(None, self.__continuous_subpaths())

    @override
    def __repr__(self) -> str:
        name = type(self).__name__
        commands = ", ".join(repr(command) for command in self)
        return f"{name}({commands})"

    @staticmethod
    def __add_svgpathtools_command(
        *, d: D, command: _SvgPathToolsCommand
    ) -> None:
        match command:  # pyright: ignore[reportMatchNotExhaustive]
            case svgpathtools.Line(start=start, end=end):
                start = point.Point.from_complex(start)
                end = point.Point.from_complex(end)

                if start.x == end.x:
                    d.vertical_line_to(end.y)
                elif start.y == end.y:
                    d.horizontal_line_to(end.x)
                else:
                    d.line_to(end)
            case svgpathtools.QuadraticBezier(end=end, control=control):
                d.quadratic_bezier_to(
                    control=point.Point.from_complex(control),
                    end=point.Point.from_complex(end),
                )
            case svgpathtools.CubicBezier(
                end=end, control1=control1, control2=control2
            ):
                d.cubic_bezier_to(
                    control1=point.Point.from_complex(control1),
                    control2=point.Point.from_complex(control2),
                    end=point.Point.from_complex(end),
                )
            case svgpathtools.Arc(
                radius=radius,
                rotation=rotation,
                large_arc=large_arc,
                sweep=sweep,
                end=end,
            ):
                d.arc_to(
                    radius=point.Point.from_complex(radius),
                    angle=rotation,
                    large=large_arc,
                    sweep=sweep,
                    end=point.Point.from_complex(end),
                )

    @classmethod
    def __from_svgpathtools(cls, path: svgpathtools.Path) -> Self:
        d = cls()
        pos: point.Point | None = None

        for command_ in path:
            # help pyright resolve the type
            command: _SvgPathToolsCommand = command_

            if command.start == command.end:
                continue

            start = point.Point.from_complex(command.start)

            if start != pos:
                d.move_to(start)

            # a line with no end is always a close command
            if command.end is None:
                assert isinstance(
                    command, svgpathtools.Line
                ), "Command is not a line but has no end"

                d.close()
                continue

            pos = point.Point.from_complex(command.end)

            cls.__add_svgpathtools_command(d=d, command=command)

        return d

    @classmethod
    def from_str(cls, text: str) -> Self:
        """Create a `D` object from an SVG path data string.

        If the path data string is empty, or if it only contains `MoveTo` (`M`)
        commands, the resulting `D` object will be empty.

        `LineTo` (`L`) commands which only move along the x-axis or y-axis will
        be converted to `HorizontalLineTo` (`H`) and `VerticalLineTo` (`V`)
        commands, respectively.

        Per the SVG specification, a path data string must start with a
        `MoveTo` command. If the first command is not a `MoveTo` command,
        a `M 0,0` command will be prepended to the path data.

        Args:
            text: The SVG path data string.

        Returns:
            A `D` object representing the path data.

        Raises:
            ValueError: If the path data string is invalid.

        Examples:
        >>> D.from_str("M 10,10 M 20,20")
        D()
        >>> D.from_str("")
        D()
        >>> D.from_str("M 1,1 L 2,2")
        D(MoveTo(end=Point(x=1.0, y=1.0)), LineTo(end=Point(x=2.0, y=2.0)))
        >>> D.from_str("Z")
        D(MoveTo(end=Point(x=0.0, y=0.0)), ClosePath())

        """
        path = svgpathtools.parse_path(text)
        return cls.__from_svgpathtools(path)

    @override
    @classmethod
    def _validate(
        cls, value: object, info: pydantic_core.core_schema.ValidationInfo
    ) -> Self:
        del info

        match value:
            case str():
                return cls.from_str(value)
            case d if isinstance(d, cls):
                return d
            case _:
                msg = f"Expected a string or {cls.__name__}"
                raise TypeError(msg)

    def __apply_mode(self) -> Generator[PathCommand, None, None]:
        formatter = serialize.get_current_formatter()
        pos = point.Point.zero()

        for command in self:
            match formatter.path_data_mode:
                case "relative":
                    if isinstance(command, PhysicalPathCommand):
                        yield command - pos
                    else:
                        yield command
                case "absolute":
                    yield command

            pos = command.end

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

    def __serialize_commands(self) -> Generator[str, None, None]:
        for command in self.__apply_mode():
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
                case CubicBezierTo(control1, control2, end):
                    yield self.__format_command(
                        control1, control2, end, char="C"
                    )
                case ArcTo(radius, angle, large, sweep, end):
                    yield self.__format_command(
                        radius, angle, large, sweep, end, char="A"
                    )
                case ClosePath():
                    yield self.__format_command(char="Z")

    @override
    def serialize(self) -> str:
        return serialize.serialize(self.__serialize_commands())


DType: TypeAlias = D
