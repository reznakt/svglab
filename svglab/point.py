from __future__ import annotations

from typing import final

import pydantic
from typing_extensions import override

from svglab import serialize


@final
@pydantic.dataclasses.dataclass
class Point(serialize.Serializable):
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
        x, y = serialize.format_number(self.x, self.y)

        return f"{x},{y}"

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
