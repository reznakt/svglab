"""Representation of a point in 2D space.

This module defines the `Point` class, which represents a point in 2D space.

The `Point` class is used to define the `<list-of-points>` type in SVG.

Use the `Point` class to represent points in SVG. Use `PointType` in Pydantic
fields.
"""

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

from svglab import mixins, protocols, serialize
from svglab.attrparse import parse, transform
from svglab.utils import mathutils, miscutils


@pydantic.dataclasses.dataclass(frozen=True)
class _Point(
    SupportsComplex,
    mixins.FloatMulDiv,
    transform.PointAddSubWithTranslateRMatmul,
    protocols.PointLike,
    protocols.CustomSerializable,
):
    x: float
    y: float

    @override
    def serialize(self) -> str:
        x, y = serialize.serialize(
            self.x, self.y, precision_group="coordinate"
        )
        formatter = serialize.get_current_formatter()

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
        yield self.x
        yield self.y

    @override
    def __mul__(self, scalar: float) -> Self:
        return type(self)(self.x * scalar, self.y * scalar)

    def __rmatmul__(self, other: transform.TransformFunction) -> Self:
        as_tuple = tuple(self)
        transformed = other.to_affine() @ as_tuple

        return type(self)(*transformed)

    @override
    def __eq__(self, other: object) -> bool:
        if not miscutils.basic_compare(other, self=self):
            return False

        return mathutils.is_close(self.x, other.x) and mathutils.is_close(
            self.y, other.y
        )

    @override
    def __hash__(self) -> int:
        return hash((type(self), self.x, self.y))

    def __bool__(self) -> bool:
        return self != self.zero()

    def __complex__(self) -> complex:
        return complex(self.x, self.y)


@final
class Point(_Point):
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

    @override
    def __init__(
        self,
        x: protocols.SupportsFloatOrIndex,
        y: protocols.SupportsFloatOrIndex,
        /,
    ) -> None:
        super().__init__(float(x), float(y))


@lark.v_args(inline=True)
class _Transformer(lark.Transformer[object, Point]):
    number = parse.FiniteFloat
    point = Point


PointType: TypeAlias = Annotated[
    Point,
    parse.get_validator(grammar="point.lark", transformer=_Transformer()),
]
