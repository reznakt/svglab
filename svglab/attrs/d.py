import abc

import pydantic

from svglab import models, serialize
from svglab.attrs import point


@pydantic.dataclasses.dataclass
class PathCommand(serialize.Serializable, metaclass=abc.ABCMeta):
    # TODO: figure out how to make KwOnly work with default_factory
    start: point.Point = pydantic.Field(
        default_factory=point.Point.zero, kw_only=True
    )
    relative: models.KwOnly[bool] = pydantic.Field(
        default=False, frozen=True
    )


class Line(PathCommand):
    end: point.Point

    def serialize(self) -> str:
        end = serialize.serialize(self.end)

        return f"L {end}"


class QuadraticBezier(PathCommand):
    control: point.Point
    end: point.Point

    def serialize(self) -> str:
        control, end = serialize.serialize(self.control, self.end)

        return f"Q {control} {end}"


class CubicBezier(PathCommand):
    control1: point.Point
    control2: point.Point
    end: point.Point

    def serialize(self) -> str:
        control1, control2, end = serialize.serialize(
            self.control1, self.control2, self.end
        )

        return f"C {control1} {control2} {end}"


class Arc(PathCommand):
    radius: point.Point
    angle: float
    large: bool
    sweep: bool
    end: point.Point

    def serialize(self) -> str:
        radius, angle, large, sweep, end = serialize.serialize(
            self.radius, self.angle, self.large, self.sweep, self.end
        )

        return f"A {radius} {angle} {large} {sweep} {end}"
