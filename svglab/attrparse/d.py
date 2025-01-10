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
    Self,
    SupportsIndex,
    TypeAlias,
    cast,
    final,
    overload,
    override,
)

import svglab.utils
from svglab import models, serialize
from svglab.attrparse import point, utils


_AbsolutePathCommandChar: TypeAlias = Literal[
    "M", "L", "H", "V", "C", "S", "Q", "T", "A", "Z"
]


@pydantic.dataclasses.dataclass
class _PathCommandBase:
    pass


class PhysicalPathCommand(
    _PathCommandBase,
    point.TwoDimensionalMovement["PhysicalPathCommand"],
    metaclass=abc.ABCMeta,
):
    end: point.Point


@final
@pydantic.dataclasses.dataclass
class ClosePath(_PathCommandBase):
    pass


@final
@pydantic.dataclasses.dataclass
class HorizontalLineTo(_PathCommandBase):
    x: float


@final
@pydantic.dataclasses.dataclass
class VerticalLineTo(_PathCommandBase):
    y: float


@final
@pydantic.dataclasses.dataclass
class MoveTo(PhysicalPathCommand):
    end: point.Point

    @override
    def __add__(self, other: point.Point, /) -> Self:
        return type(self)(end=self.end + other)


@pydantic.dataclasses.dataclass
class LineTo(PhysicalPathCommand):
    end: point.Point

    @override
    def __add__(self, other: point.Point, /) -> Self:
        return type(self)(end=self.end + other)


@final
@pydantic.dataclasses.dataclass
class QuadraticBezierTo(PhysicalPathCommand):
    control: point.Point
    end: point.Point

    @override
    def __add__(self, other: point.Point, /) -> Self:
        return type(self)(
            control=self.control + other, end=self.end + other
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
            if isinstance(command, PhysicalPathCommand)
            else command
            for command in self
        )

    @override
    def __len__(self) -> int:
        return len(self.__commands)

    @override
    def __eq__(self, other: object) -> bool:
        if not svglab.utils.basic_compare(other, self=self):
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

    def __prev_command(self, command: PathCommand) -> PathCommand:
        index = self.index(command)
        return self[index - 1]

    def __get_end(self, command: PathCommand) -> point.Point:
        match command:
            case PhysicalPathCommand(end=end):
                return end
            case ClosePath():
                # TODO: Actually implement this
                return self.__get_end(self.__prev_command(command))
            case HorizontalLineTo(x=x):
                end = self.__get_end(self.__prev_command(command))
                return point.Point(x=x, y=end.y)
            case VerticalLineTo(y=y):
                end = self.__get_end(self.__prev_command(command))
                return point.Point(x=end.x, y=y)
            case _:
                msg = f"Unsupported command: {type(command)}"
                raise ValueError(msg)

    def __add(
        self, command: PathCommand, *, relative: bool = False
    ) -> Self:
        if not self and not isinstance(command, MoveTo):
            raise ValueError("The first command must be a MoveTo command")

        if relative and isinstance(command, PhysicalPathCommand):
            command += self.__get_end(self[-1])

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
        return self.__add(ClosePath())

    @override
    def __repr__(self) -> str:
        name = type(self).__name__
        commands = ", ".join(repr(command) for command in self)
        return f"{name}({commands})"

    @classmethod
    def from_str(cls, text: str) -> Self:
        d = utils.parse(text, grammar="d.lark", transformer=_Transformer())

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

    def __apply_mode(self) -> Generator[PathCommand, None, None]:
        formatter = serialize.get_current_formatter()
        pos = point.Point.zero()

        for command in self:
            match formatter.path_data_mode:
                case "relative":
                    if isinstance(command, PhysicalPathCommand):
                        # TODO: this cast can be removed fairly easily
                        yield cast(PathCommand, command - pos)
                    else:
                        yield command
                case "absolute":
                    yield command

            pos = self.__get_end(command)

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


@lark.v_args(inline=True)
class _Transformer(lark.Transformer[object, D]):
    __d: D

    @property
    def _d(self) -> D:
        try:
            return self.__d
        except AttributeError:
            self.__d = D()
            return self.__d

    number = float
    point = point.Point

    def move(self, end: point.Point) -> D:
        return self._d.move_to(end)

    def line(self, end: point.Point) -> D:
        return self._d.line_to(end)

    def horizontal_line(self, x: float) -> D:
        return self._d.horizontal_line_to(x)

    def vertical_line(self, y: float) -> D:
        return self._d.vertical_line_to(y)

    def quadratic_bezier(
        self, control: point.Point, end: point.Point
    ) -> D:
        return self._d.quadratic_bezier_to(control, end)

    def cubic_bezier(
        self,
        control1: point.Point,
        control2: point.Point,
        end: point.Point,
    ) -> D:
        return self._d.cubic_bezier_to(control1, control2, end)

    def arc(
        self,
        radius: point.Point,
        angle: lark.Token,
        large: bool,  # noqa: FBT001
        sweep: bool,  # noqa: FBT001
        end: point.Point,
    ) -> D:
        return self._d.arc_to(
            radius, float(angle), end, large=large, sweep=sweep
        )

    def smooth_quadratic_bezier(self, end: point.Point) -> D:
        del end
        raise NotImplementedError  # TODO: Implement this

    def smooth_cubic_bezier(
        self, control2: point.Point, end: point.Point
    ) -> D:
        del control2, end
        raise NotImplementedError  # TODO: Implement this

    def z(self) -> D:
        return self._d.close()

    @lark.v_args(inline=False)
    def path(self, args: list[object]) -> D:
        del args
        return self._d


DType: TypeAlias = Annotated[
    D, utils.get_validator(grammar="d.lark", transformer=_Transformer())
]
