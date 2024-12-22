from __future__ import annotations

from collections.abc import Iterable, MutableSequence
from typing import Final, SupportsIndex, TypeAlias, cast, final, overload

import pydantic
import pydantic_core
import svgpathtools
from typing_extensions import Self, override

from svglab import models, serialize
from svglab.attrs import point


__all__ = [
    "ArcTo",
    "CubicBezierTo",
    "D",
    "DType",
    "LineTo",
    "PathCommand",
    "QuadraticBezierTo",
]


@final
@pydantic.dataclasses.dataclass
class MoveTo(serialize.CustomSerializable):
    end: point.Point

    @override
    def serialize(self) -> str:
        end = serialize.serialize(self.end)

        return f"M {end}"

    def __add__(self, other: point.Point, /) -> Self:
        return MoveTo(end=self.end + other)

    def __sub__(self, other: point.Point, /) -> Self:
        return MoveTo(end=self.end - other)


@pydantic.dataclasses.dataclass
class LineTo(serialize.CustomSerializable):
    end: point.Point

    @override
    def serialize(self) -> str:
        end = serialize.serialize(self.end)

        return f"L {end}"

    def __add__(self, other: point.Point, /) -> Self:
        return type(self)(end=self.end + other)

    def __sub__(self, other: point.Point, /) -> Self:
        return type(self)(end=self.end - other)


@final
@pydantic.dataclasses.dataclass
class QuadraticBezierTo(serialize.CustomSerializable):
    control: point.Point
    end: point.Point

    @override
    def serialize(self) -> str:
        control, end = serialize.serialize(self.control, self.end)

        return f"Q {control} {end}"

    def __add__(self, other: point.Point, /) -> Self:
        return QuadraticBezierTo(
            control=self.control + other, end=self.end + other
        )

    def __sub__(self, other: point.Point, /) -> Self:
        return QuadraticBezierTo(
            control=self.control - other, end=self.end - other
        )


@final
@pydantic.dataclasses.dataclass
class CubicBezierTo(serialize.CustomSerializable):
    control1: point.Point
    control2: point.Point
    end: point.Point

    @override
    def serialize(self) -> str:
        control1, control2, end = serialize.serialize(
            self.control1, self.control2, self.end
        )

        return f"C {control1} {control2} {end}"

    def __add__(self, other: point.Point, /) -> Self:
        return CubicBezierTo(
            control1=self.control1 + other,
            control2=self.control2 + other,
            end=self.end + other,
        )

    def __sub__(self, other: point.Point, /) -> Self:
        return CubicBezierTo(
            control1=self.control1 - other,
            control2=self.control2 - other,
            end=self.end - other,
        )


@final
@pydantic.dataclasses.dataclass
class ArcTo(serialize.CustomSerializable):
    radius: point.Point
    angle: float
    large: bool
    sweep: bool
    end: point.Point

    @override
    def serialize(self) -> str:
        radius, angle, large, sweep, end = serialize.serialize(
            self.radius, self.angle, self.large, self.sweep, self.end
        )

        return f"A {radius} {angle} {large} {sweep} {end}"

    def __add__(self, other: point.Point, /) -> Self:
        return ArcTo(
            radius=self.radius + other,
            angle=self.angle,
            large=self.large,
            sweep=self.sweep,
            end=self.end + other,
        )

    def __sub__(self, other: point.Point, /) -> Self:
        return ArcTo(
            radius=self.radius - other,
            angle=self.angle,
            large=self.large,
            sweep=self.sweep,
            end=self.end - other,
        )


@final
@pydantic.dataclasses.dataclass
class ClosePath(LineTo):
    @override
    def serialize(self) -> str:
        return "Z"


PathCommand: TypeAlias = (
    MoveTo | LineTo | QuadraticBezierTo | CubicBezierTo | ArcTo | ClosePath
)


@final
class D(
    MutableSequence[PathCommand],
    models.CustomModel,
    serialize.CustomSerializable,
):
    def __init__(
        self, iterable: Iterable[PathCommand] | None = None, /
    ) -> None:
        self.__commands: Final[list[PathCommand]] = list(iterable or [])

    @override
    def __len__(self) -> int:
        return len(self.__commands)

    @overload
    def __getitem__(self, index: SupportsIndex, /) -> PathCommand: ...

    @overload
    def __getitem__(self, slice: slice, /) -> Self: ...

    @override
    def __getitem__(
        self, index_or_slice: SupportsIndex | slice, /
    ) -> PathCommand | Self:
        if isinstance(index_or_slice, SupportsIndex):
            return self.__commands[index_or_slice]

        return D(self.__commands[index_or_slice])

    @overload
    def __delitem__(self, index: SupportsIndex, /) -> None: ...

    @overload
    def __delitem__(self, slice: slice, /) -> None: ...

    @override
    def __delitem__(
        self, index_or_slice: SupportsIndex | slice, /
    ) -> None:
        if isinstance(index_or_slice, SupportsIndex):
            del self.__commands[index_or_slice]
        else:
            del self.__commands[index_or_slice]

    @overload
    def __setitem__(
        self, index: SupportsIndex, value: PathCommand, /
    ) -> None: ...

    @overload
    def __setitem__(
        self, slice: slice, values: Iterable[PathCommand], /
    ) -> None: ...

    @override
    def __setitem__(
        self,
        index_or_slice: SupportsIndex | slice,
        value_or_values: PathCommand | Iterable[PathCommand],
        /,
    ) -> None:
        if isinstance(index_or_slice, SupportsIndex):
            assert isinstance(value_or_values, PathCommand)
            self.__commands[index_or_slice] = value_or_values
        else:
            assert isinstance(value_or_values, Iterable)
            self.__commands[index_or_slice] = value_or_values

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
        return self.__add(ClosePath(end=self.start))

    @override
    def __repr__(self) -> str:
        name = type(self).__name__
        commands = ", ".join(repr(command) for command in self)
        return f"{name}({commands})"

    @classmethod
    def __from_svgpathtools(cls, path: svgpathtools.Path) -> Self:
        d = cls()

        for command in path:
            match command:
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
            case D():
                if not all(
                    isinstance(command, PathCommand) for command in value
                ):
                    msg = "All commands must be instances of PathCommand"
                    raise TypeError(msg)

                return value
            case _:
                msg = f"Expected a string or {cls.__name__}"
                raise TypeError(msg)

    @override
    def serialize(self) -> str:
        return serialize.serialize(
            cast(list[serialize.Serializable], self.__commands)
        )


DType: TypeAlias = D
