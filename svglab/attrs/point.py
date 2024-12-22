from __future__ import annotations

from typing import Annotated, SupportsComplex, TypeAlias, final

import lark
import pydantic
from typing_extensions import override

from svglab import serialize
from svglab.attrs import utils


__all__ = ["Point", "PointType"]


@final
@pydantic.dataclasses.dataclass
class Point(SupportsComplex, serialize.CustomSerializable):
    """A point in a 2D plane.

    Attributes:
        x: The x-coordinate of the point.
        y: The y-coordinate of the point.

    Examples:
        >>> point = Point(1, 2)
        >>> point.x
        1.0
        >>> point.y
        2.0
        >>> point == Point(1, 2)
        True
        >>> point == Point(1, 3)
        False
        >>> point += Point(2, 3)
        >>> point
        Point(x=3.0, y=5.0)
        >>> point -= Point(1, 2)
        >>> point
        Point(x=2.0, y=3.0)
        >>> point *= 2
        >>> point
        Point(x=4.0, y=6.0)
        >>> point /= 2
        >>> point
        Point(x=2.0, y=3.0)
        >>> point + point
        Point(x=4.0, y=6.0)

    """

    x: float
    y: float

    @override
    def serialize(self) -> str:
        formatter = serialize.get_current_formatter()
        x, y = serialize.format_number(self.x, self.y)

        return f"{x}{formatter.point_separator}{y}"

    def __add__(self, other: Point) -> Point:
        return Point(self.x + other.x, self.y + other.y)

    def __neg__(self) -> Point:
        return self * -1

    def __sub__(self, other: Point) -> Point:
        return self + -other

    def __mul__(self, scalar: float) -> Point:
        return Point(self.x * scalar, self.y * scalar)

    def __truediv__(self, scalar: float) -> Point:
        return Point(self.x / scalar, self.y / scalar)

    def __complex__(self) -> complex:
        return complex(self.x, self.y)

    @classmethod
    def from_complex(cls, value: complex, /) -> Point:
        return cls(value.real, value.imag)

    @classmethod
    def zero(cls) -> Point:
        return cls(0, 0)


@lark.v_args(inline=True)
class Transformer(lark.Transformer[object, Point]):
    number = float
    point = Point


PointType: TypeAlias = Annotated[
    Point,
    utils.get_validator(grammar="point.lark", transformer=Transformer()),
]
