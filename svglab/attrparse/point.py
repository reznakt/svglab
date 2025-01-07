from __future__ import annotations

from typing import (
    Annotated,
    Protocol,
    SupportsComplex,
    TypeAlias,
    TypeVar,
    final,
    runtime_checkable,
)

import lark
import pydantic
from typing_extensions import Self, override

from svglab import protocols, serialize
from svglab.attrparse import utils


_Supports2DMovementT_co = TypeVar(
    "_Supports2DMovementT_co", covariant=True, bound="Point"
)


@runtime_checkable
class Supports2DMovement(
    protocols.SupportsAddSub["Point", _Supports2DMovementT_co], Protocol
):
    pass


@final
@pydantic.dataclasses.dataclass(frozen=True)
class Point(
    SupportsComplex,
    Supports2DMovement,
    protocols.SupportsMul[float, "Point"],
    serialize.CustomSerializable,
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

    @override
    def __add__(self, other: Self) -> Self:
        return type(self)(self.x + other.x, self.y + other.y)

    @override
    def __sub__(self, other: Self) -> Self:
        return self + -other

    def __neg__(self) -> Self:
        return self * -1

    @override
    def __mul__(self, scalar: float) -> Self:
        return type(self)(self.x * scalar, self.y * scalar)

    def __truediv__(self, scalar: float) -> Self:
        return type(self)(self.x / scalar, self.y / scalar)

    def __complex__(self) -> complex:
        return complex(self.x, self.y)

    @classmethod
    def from_complex(cls, value: complex, /) -> Self:
        return cls(value.real, value.imag)

    @classmethod
    def zero(cls) -> Self:
        return cls(0, 0)


@lark.v_args(inline=True)
class _Transformer(lark.Transformer[object, Point]):
    number = float
    point = Point


PointType: TypeAlias = Annotated[
    Point,
    utils.get_validator(grammar="point.lark", transformer=_Transformer()),
]
