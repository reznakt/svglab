from __future__ import annotations

import functools
import math
import operator
from collections.abc import Iterable, Iterator

import lark
import pydantic
from typing_extensions import (
    Annotated,
    Protocol,
    Self,
    TypeAlias,
    final,
    overload,
    override,
    runtime_checkable,
)

from svglab import serialize
from svglab.attrparse import point, utils


def compose(transforms: Iterable[_SupportsToMatrix], /) -> Matrix:
    """Compose a series of transformations into a single matrix.

    Args:
        transforms: The transformations to compose.

    Returns:
        The result of composing the transformations.

    Examples:
        >>> m1 = Matrix(1, 0, 0, 1, 2, 3)
        >>> m2 = Matrix(1, 0, 0, 1, 4, 5)
        >>> m3 = Matrix(1, 0, 0, 1, 6, 7)
        >>> compose([m1, m2, m3])
        Matrix(a=1.0, b=0.0, c=0.0, d=1.0, e=12.0, f=15.0)

    """
    return functools.reduce(
        operator.matmul,
        (transform.to_matrix() for transform in transforms),
    )


@runtime_checkable
class _SupportsToMatrix(Protocol):
    def to_matrix(self) -> Matrix: ...

    @overload
    def __matmul__(self, other: _SupportsToMatrix) -> Matrix: ...

    @overload
    def __matmul__(self, other: point.Point) -> point.Point: ...

    @overload
    def __matmul__(
        self, other: Iterable[point.Point]
    ) -> Iterator[point.Point]: ...

    def __matmul__(
        self,
        other: _SupportsToMatrix | point.Point | Iterable[point.Point],
    ) -> Matrix | point.Point | Iterator[point.Point]:
        matrix = self.to_matrix()

        match other:
            case point.Point(x, y):
                return point.Point(
                    x=matrix.a * x + matrix.c * y + matrix.e,
                    y=matrix.b * x + matrix.d * y + matrix.f,
                )
            case Matrix():
                return Matrix(
                    a=matrix.a * other.a + matrix.c * other.b,
                    b=matrix.b * other.a + matrix.d * other.b,
                    c=matrix.a * other.c + matrix.c * other.d,
                    d=matrix.b * other.c + matrix.d * other.d,
                    e=matrix.a * other.e + matrix.c * other.f + matrix.e,
                    f=matrix.b * other.e + matrix.d * other.f + matrix.f,
                )
            case _SupportsToMatrix():
                return matrix @ other.to_matrix()
            case Iterable():
                return (matrix @ p for p in other)


class _TransformActionBase(
    serialize.CustomSerializable, _SupportsToMatrix
):
    pass


@pydantic.dataclasses.dataclass
class _Translate(_TransformActionBase):
    x: float
    y: float | None = None

    @override
    def serialize(self) -> str:
        x = serialize.serialize(self.x)

        if self.y is None:
            return f"translate({x})"

        y = serialize.serialize(self.y)

        return f"translate({x}, {y})"

    @override
    def to_matrix(self) -> Matrix:
        tx = self.x
        ty = self.y if self.y is not None else 0

        return Matrix(1, 0, 0, 1, tx, ty or 0)


@final
class Translate(_Translate):
    @overload
    def __init__(self, x: float, /) -> None: ...

    @overload
    def __init__(self, x: float, y: float, /) -> None: ...

    def __init__(self, x: float, y: float | None = None, /) -> None:
        super().__init__(x=x, y=y)


@pydantic.dataclasses.dataclass
class _Scale(_TransformActionBase):
    x: float
    y: float | None = None

    @override
    def serialize(self) -> str:
        x = serialize.serialize(self.x)

        if self.y is None:
            return f"scale({x})"

        y = serialize.serialize(self.y)

        return f"scale({x}, {y})"

    @override
    def to_matrix(self) -> Matrix:
        sx = self.x
        sy = self.y if self.y is not None else self.x

        return Matrix(sx, 0, 0, sy, 0, 0)


@final
class Scale(_Scale):
    @overload
    def __init__(self, x: float, /) -> None: ...

    @overload
    def __init__(self, x: float, y: float, /) -> None: ...

    def __init__(self, x: float, y: float | None = None, /) -> None:
        super().__init__(x=x, y=y)


@pydantic.dataclasses.dataclass
class _Rotate(_TransformActionBase):
    angle: float
    cx: float | None
    cy: float | None

    @pydantic.model_validator(mode="after")
    def __check_cx_cy(self) -> Self:  # pyright: ignore[reportUnusedFunction]
        cx_is_none = self.cx is None
        cy_is_none = self.cy is None

        if cx_is_none != cy_is_none:
            raise ValueError(
                "Both cx and cy must either be provided or omitted"
            )

        return self

    @override
    def serialize(self) -> str:
        angle = serialize.serialize(self.angle)

        if self.cx is None:
            return f"rotate({angle})"

        assert self.cy is not None

        cx, cy = serialize.serialize(self.cx, self.cy)

        return f"rotate({angle} {cx} {cy})"

    @override
    def to_matrix(self) -> Matrix:
        a = math.radians(self.angle)

        cos_a = math.cos(a)
        sin_a = math.sin(a)

        rotation = Matrix(cos_a, sin_a, -sin_a, cos_a, 0, 0)

        if self.cx is None:
            return rotation

        assert self.cy is not None

        return (
            Translate(self.cx, self.cy)
            @ rotation
            @ Translate(-self.cx, -self.cy)
        )


@final
class Rotate(_Rotate):
    @overload
    def __init__(self, angle: float, /) -> None: ...

    @overload
    def __init__(self, angle: float, /, cx: float, cy: float) -> None: ...

    def __init__(
        self,
        angle: float,
        /,
        cx: float | None = None,
        cy: float | None = None,
    ) -> None:
        super().__init__(angle=angle, cx=cx, cy=cy)


@final
@pydantic.dataclasses.dataclass
class SkewX(_TransformActionBase):
    angle: float

    @override
    def serialize(self) -> str:
        angle = serialize.serialize(self.angle)

        return f"skewX({angle})"

    @override
    def to_matrix(self) -> Matrix:
        a = math.radians(self.angle)

        return Matrix(1, 0, math.tan(a), 1, 0, 0)


@final
@pydantic.dataclasses.dataclass
class SkewY(_TransformActionBase):
    angle: float

    @override
    def serialize(self) -> str:
        angle = serialize.serialize(self.angle)

        return f"skewY({angle})"

    @override
    def to_matrix(self) -> Matrix:
        a = math.radians(self.angle)

        return Matrix(1, math.tan(a), 0, 1, 0, 0)


@final
@pydantic.dataclasses.dataclass
class Matrix(_TransformActionBase):
    a: float
    b: float
    c: float
    d: float
    e: float
    f: float

    @override
    def serialize(self) -> str:
        a, b, c, d, e, f = serialize.serialize(
            self.a, self.b, self.c, self.d, self.e, self.f
        )

        return f"matrix({a} {b} {c} {d} {e} {f})"

    @override
    def to_matrix(self) -> Matrix:
        return self


TransformAction: TypeAlias = (
    Translate | Scale | Rotate | SkewX | SkewY | Matrix
)

Transform: TypeAlias = list[TransformAction]


@lark.v_args(inline=True)
class _Transformer(lark.Transformer[object, Transform]):
    number = float

    translate = Translate
    scale = Scale
    rotate = Rotate
    skew_x = SkewX
    skew_y = SkewY
    matrix = Matrix

    transform_ = utils.v_args_to_list


TransformType: TypeAlias = Annotated[
    Transform,
    utils.get_validator(
        grammar="transform.lark", transformer=_Transformer()
    ),
]
