from __future__ import annotations

import abc
from collections.abc import Generator, Iterable, MutableSequence
from typing import (
    Final,
    Protocol,
    SupportsIndex,
    TypeAlias,
    final,
    overload,
    runtime_checkable,
)

import pydantic
import svgpathtools
from pydantic_core import core_schema
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


@runtime_checkable
class HasEnd(Protocol):
    end: point.Point


@pydantic.dataclasses.dataclass
class PathCommandBase(
    HasEnd, serialize.Serializable, metaclass=abc.ABCMeta
):
    # can't use KwOnly here because pydantic.mypy won't infer the kw_only=True
    start: point.Point = pydantic.Field(
        default_factory=point.Point.zero, kw_only=True
    )


@final
@pydantic.dataclasses.dataclass
class LineTo(PathCommandBase):
    end: point.Point

    @override
    def serialize(self) -> str:
        end = serialize.serialize(self.end)

        return f"L {end}"


@final
@pydantic.dataclasses.dataclass
class QuadraticBezierTo(PathCommandBase):
    control: point.Point
    end: point.Point

    @override
    def serialize(self) -> str:
        control, end = serialize.serialize(self.control, self.end)

        return f"Q {control} {end}"


@final
@pydantic.dataclasses.dataclass
class CubicBezierTo(PathCommandBase):
    control1: point.Point
    control2: point.Point
    end: point.Point

    @override
    def serialize(self) -> str:
        control1, control2, end = serialize.serialize(
            self.control1, self.control2, self.end
        )

        return f"C {control1} {control2} {end}"


@final
@pydantic.dataclasses.dataclass
class ArcTo(PathCommandBase):
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


PathCommand: TypeAlias = LineTo | QuadraticBezierTo | CubicBezierTo | ArcTo


# internal helper to represent and serialize a MoveTo command
# not a part of PathCommand and not for export
@final
@pydantic.dataclasses.dataclass
class _MoveTo(PathCommandBase):
    end: point.Point

    @override
    def serialize(self) -> str:
        end = serialize.serialize(self.end)

        return f"M {end}"


@final
class D(
    MutableSequence[PathCommand],
    models.CustomModel,
    serialize.Serializable,
):
    def __init__(self, *commands: PathCommand) -> None:
        self.__commands: Final[list[PathCommand]] = list(commands)

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

        return D(*self.__commands[index_or_slice])

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
        # this is going to need to be a bit more complex
        # so leave it for now
        # TODO: implement
        del index, value
        raise NotImplementedError

    def __resolve_moves(
        self,
    ) -> Generator[PathCommand | _MoveTo, None, None]:
        pos = point.Point.zero()

        for cmd in self:
            if cmd.start != pos:
                yield _MoveTo(end=cmd.start)

            yield cmd

    @override
    def serialize(self) -> str:
        return serialize.serialize(list(self.__resolve_moves()))

    def add(self, *commands: PathCommand) -> Self:
        self.__commands.extend(commands)

        return self

    @property
    def end(self) -> point.Point:
        if not self:
            return point.Point.zero()

        return self[-1].end

    def line(self, end: point.Point) -> Self:
        return self.add(LineTo(start=self.end, end=end))

    def quadratic_bezier(
        self, control: point.Point, end: point.Point
    ) -> Self:
        return self.add(
            QuadraticBezierTo(start=self.end, control=control, end=end)
        )

    def cubic_bezier(
        self,
        control1: point.Point,
        control2: point.Point,
        end: point.Point,
    ) -> Self:
        return self.add(
            CubicBezierTo(
                start=self.end,
                control1=control1,
                control2=control2,
                end=end,
            )
        )

    def arc(
        self,
        radius: point.Point,
        angle: float,
        large: bool,  # noqa: FBT001
        sweep: bool,  # noqa: FBT001
        end: point.Point,
    ) -> Self:
        return self.add(
            ArcTo(
                start=self.end,
                radius=radius,
                angle=angle,
                large=large,
                sweep=sweep,
                end=end,
            )
        )

    def __repr__(self) -> str:
        name = type(self).__name__
        commands = ", ".join(repr(command) for command in self)
        return f"{name}({commands})"

    def is_closed(self) -> bool:
        if not self:
            return False

        first = self[0]
        last = self[-1]

        return first.start == last.end

    def close(self) -> Self:
        if self.is_closed():
            raise ValueError("Path is already closed")

        first = self.__commands[0]

        return self.add(LineTo(end=first.start))

    @classmethod
    def __from_svgpathtools(cls, path: svgpathtools.Path) -> Self:
        d = cls()

        for command in path:
            match command:
                case svgpathtools.Line():
                    d.line(end=point.Point.from_complex(command.end))
                case svgpathtools.QuadraticBezier():
                    d.quadratic_bezier(
                        control=point.Point.from_complex(command.control),
                        end=point.Point.from_complex(command.end),
                    )
                case svgpathtools.CubicBezier():
                    d.cubic_bezier(
                        control1=point.Point.from_complex(
                            command.control1
                        ),
                        control2=point.Point.from_complex(
                            command.control2
                        ),
                        end=point.Point.from_complex(command.end),
                    )
                case svgpathtools.Arc():
                    d.arc(
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
        cls, value: object, info: core_schema.ValidationInfo
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


DType: TypeAlias = D
