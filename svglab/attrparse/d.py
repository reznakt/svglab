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

from svglab import models, serialize, utils
from svglab.attrparse import point


_AbsolutePathCommandChar: TypeAlias = Literal[
    "M", "L", "H", "V", "C", "S", "Q", "T", "A", "Z"
]


class PathCommand(
    point.Supports2DMovement["PathCommand"], metaclass=abc.ABCMeta
):
    end: point.Point


@final
@pydantic.dataclasses.dataclass
class MoveTo(PathCommand):
    end: point.Point

    @override
    def __add__(self, other: point.Point, /) -> Self:
        return type(self)(end=self.end + other)

    @override
    def __sub__(self, other: point.Point, /) -> Self:
        return type(self)(end=self.end - other)


@pydantic.dataclasses.dataclass
class LineTo(PathCommand):
    end: point.Point

    @override
    def __add__(self, other: point.Point, /) -> Self:
        return type(self)(end=self.end + other)

    @override
    def __sub__(self, other: point.Point, /) -> Self:
        return type(self)(end=self.end - other)


@final
@pydantic.dataclasses.dataclass
class QuadraticBezierTo(PathCommand):
    control: point.Point
    end: point.Point

    @override
    def __add__(self, other: point.Point, /) -> Self:
        return type(self)(
            control=self.control + other, end=self.end + other
        )

    @override
    def __sub__(self, other: point.Point, /) -> Self:
        return type(self)(
            control=self.control - other, end=self.end - other
        )


@final
@pydantic.dataclasses.dataclass
class CubicBezierTo(PathCommand):
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

    @override
    def __sub__(self, other: point.Point, /) -> Self:
        return type(self)(
            control1=self.control1 - other,
            control2=self.control2 - other,
            end=self.end - other,
        )


@final
@pydantic.dataclasses.dataclass
class ArcTo(PathCommand):
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

    @override
    def __sub__(self, other: point.Point, /) -> Self:
        return type(self)(
            radius=self.radius - other,
            angle=self.angle,
            large=self.large,
            sweep=self.sweep,
            end=self.end - other,
        )


@final
@pydantic.dataclasses.dataclass
class ClosePath(LineTo):
    pass


@final
class D(
    MutableSequence[PathCommand],
    point.Supports2DMovement["D"],
    models.CustomModel,
    serialize.CustomSerializable,
):
    def __init__(
        self, iterable: Iterable[PathCommand] | None = None, /
    ) -> None:
        self.__commands: Final[list[PathCommand]] = list(iterable or [])

    @override
    def __add__(self, other: point.Point) -> Self:
        return type(self)(command + other for command in self)

    @override
    def __sub__(self, other: point.Point) -> Self:
        return type(self)(command - other for command in self)

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
        if relative:
            command += self.end

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

    def quadratic_bezier_to(
        self,
        control: point.Point,
        end: point.Point,
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

    def close(self) -> Self:
        last_continuous_subpath = utils.take_last(
            self.__continuous_subpaths()
        )

        end = (
            self.start
            if last_continuous_subpath is None
            else last_continuous_subpath.start
        )

        return self.__add(ClosePath(end=end))

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

    def __continuous_subpaths(self) -> Generator[D]:
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

    @classmethod
    def __from_svgpathtools(cls, path: svgpathtools.Path) -> Self:
        d = cls()

        for command in path:
            match command:  # pyright: ignore[reportMatchNotExhaustive]
                case svgpathtools.Line():
                    d.line_to(point.Point.from_complex(command.end))
                case svgpathtools.QuadraticBezier():
                    d.quadratic_bezier_to(
                        control=point.Point.from_complex(command.control),
                        end=point.Point.from_complex(command.end),
                    )
                case svgpathtools.CubicBezier():
                    d.cubic_bezier_to(
                        control1=point.Point.from_complex(
                            command.control1
                        ),
                        control2=point.Point.from_complex(
                            command.control2
                        ),
                        end=point.Point.from_complex(command.end),
                    )
                case svgpathtools.Arc():
                    d.arc_to(
                        radius=point.Point.from_complex(command.radius),
                        angle=command.rotation,
                        large=command.large_arc,
                        sweep=command.sweep,
                        end=point.Point.from_complex(command.end),
                    )

        return d

    @classmethod
    def from_str(cls, value: str) -> Self:
        path = svgpathtools.parse_path(value)
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

    def __apply_mode(self) -> Generator[PathCommand]:
        formatter = serialize.get_current_formatter()
        pos = point.Point.zero()

        for command in self:
            match formatter.path_data_mode:
                case "relative":
                    yield command - pos
                case "absolute":
                    yield command

            pos = command.end

    @staticmethod
    def __format_command(
        *args: serialize.Serializable,
        absolute_char: _AbsolutePathCommandChar,
    ) -> str:
        formatter = serialize.get_current_formatter()

        char = (
            absolute_char
            if formatter.path_data_mode == "absolute"
            else absolute_char.lower()
        )

        if not args:
            return char

        args_str = serialize.serialize(args, bool_mode="number")
        return f"{char} {args_str}"

    def __serialize_commands(self) -> Generator[str]:
        for command in self.__apply_mode():
            match command:
                case MoveTo(end):
                    yield self.__format_command(end, absolute_char="M")
                case ClosePath(end):  # has to be before LineTo
                    yield self.__format_command(absolute_char="Z")
                case LineTo(end):
                    yield self.__format_command(end, absolute_char="L")
                case QuadraticBezierTo(control, end):
                    yield self.__format_command(
                        control, end, absolute_char="Q"
                    )
                case CubicBezierTo(control1, control2, end):
                    yield self.__format_command(
                        control1, control2, end, absolute_char="C"
                    )
                case ArcTo(radius, angle, large, sweep, end):
                    yield self.__format_command(
                        radius, angle, large, sweep, end, absolute_char="A"
                    )
                case _:
                    msg = f"Unsupported command type: {type(command)}"
                    raise TypeError(msg)

    @override
    def serialize(self) -> str:
        return serialize.serialize(self.__serialize_commands())


DType: TypeAlias = D
