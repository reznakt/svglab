from __future__ import annotations

from collections.abc import Iterator

import lark
import pydantic
from typing_extensions import (
    Annotated,
    Self,
    SupportsComplex,
    TypeAlias,
    final,
    override,
)

from svglab import mixins, protocols, serialize, utils
from svglab.attrparse import parse


@final
@pydantic.dataclasses.dataclass(frozen=True)
class Point(
    SupportsComplex,
    mixins.FloatMulDiv,
    mixins.AddSub["Point"],
    protocols.PointLike,
    protocols.CustomSerializable,
):
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
        x, y = serialize.serialize(self.x, self.y)

        return f"{x}{formatter.point_separator}{y}"

    @classmethod
    def from_complex(cls, value: complex, /) -> Self:
        return cls(value.real, value.imag)

    @classmethod
    def zero(cls) -> Self:
        return cls(0, 0)

    def line_reflect(self, center: Self) -> Self:
        """Reflect this point across a line defined by a center point.

        Given a center point, this method returns a new point such that:
        - this point, the center point, and the new point are collinear, and
        - the distance between this point and the center point is equal to the
          distance between the center point and the new point.

        Args:
            center: The center of the reflection.

        Returns:
            The reflected point.

        Examples:
        >>> Point(1, 1).line_reflect(Point(0, 0))
        Point(x=-1.0, y=-1.0)
        >>> Point(0, 0).line_reflect(Point(10, 10))
        Point(x=20.0, y=20.0)

        """
        return center + (center - self)

    def __iter__(self) -> Iterator[float]:
        return iter((self.x, self.y))

    @override
    def __add__(self, other: Self) -> Self:
        return type(self)(self.x + other.x, self.y + other.y)

    @override
    def __mul__(self, scalar: float) -> Self:
        return type(self)(self.x * scalar, self.y * scalar)

    @override
    def __eq__(self, other: object) -> bool:
        if not utils.basic_compare(other, self=self):
            return False

        return utils.is_close(self.x, other.x) and utils.is_close(
            self.y, other.y
        )

    def __bool__(self) -> bool:
        return self == self.zero()

    def __complex__(self) -> complex:
        return complex(self.x, self.y)


@lark.v_args(inline=True)
class _Transformer(lark.Transformer[object, Point]):
    number = float
    point = Point


PointType: TypeAlias = Annotated[
    Point,
    parse.get_validator(grammar="point.lark", transformer=_Transformer()),
]
