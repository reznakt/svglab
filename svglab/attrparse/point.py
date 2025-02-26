from __future__ import annotations

from collections.abc import Iterator

import lark
import numpy as np
import numpy.typing as npt
import pydantic
from typing_extensions import (
    Annotated,
    Self,
    SupportsComplex,
    TypeAlias,
    final,
    override,
)

from svglab import mixins, protocols, serialize, utils, utiltypes
from svglab.attrparse import parse, transform


@pydantic.dataclasses.dataclass(frozen=True)
class _Point(
    SupportsComplex,
    mixins.FloatMulDiv,
    transform.PointAddSubWithTranslateRMatmul,
    protocols.PointLike,
    protocols.SupportsNpArray,
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

    @override
    @override
    def __array__(
        self, dtype: npt.DTypeLike = None, *, copy: bool | None = None
    ) -> utiltypes.NpFloatArray:
        del dtype, copy

        return np.array([self.x, self.y, 1])

    @classmethod
    def from_array(cls, array: utiltypes.NpFloatArray, /) -> Self:
        """Create a `Point` instance from a NumPy array.

        The array must be a 3-element vector, representing a cartesian point
        in the real projective plane using homogeneous coordinates.

        The last element of the array must be non-zero (i.e., the point must
        not be at infinity).

        Args:
            array: The array to convert to a point.

        Returns:
            The point represented by the array.

        Raises:
            ValueError: If the array is not a 3-element vector or if the last
                element of the array is zero.

        """
        if array.shape != (3,):
            raise ValueError("The array must be a 3-element vector")

        x, y, z = array

        try:
            return cls(x / z, y / z)
        except ZeroDivisionError as e:
            # if z is zero, the point is at infinity
            raise ValueError(
                "The last element of the array cannot be zero"
            ) from e

    def __iter__(self) -> Iterator[float]:
        return iter((self.x, self.y))

    @override
    def __mul__(self, scalar: float) -> Self:
        return type(self)(self.x * scalar, self.y * scalar)

    def __rmatmul__(self, other: protocols.SupportsNpArray) -> Self:
        return self.from_array(np.array(other) @ np.array(self))

    @override
    def __eq__(self, other: object) -> bool:
        if not utils.basic_compare(other, self=self):
            return False

        return utils.is_close(self.x, other.x) and utils.is_close(
            self.y, other.y
        )

    def __bool__(self) -> bool:
        return self != self.zero()

    def __complex__(self) -> complex:
        return complex(self.x, self.y)


@final
class Point(_Point):
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
    number = float
    point = Point


PointType: TypeAlias = Annotated[
    Point,
    parse.get_validator(grammar="point.lark", transformer=_Transformer()),
]
