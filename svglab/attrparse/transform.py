from __future__ import annotations

import abc
import functools
import math
import operator
from collections.abc import Iterable

import lark
import numpy as np
import numpy.typing as npt
import pydantic
from typing_extensions import (
    Annotated,
    Self,
    TypeAlias,
    final,
    overload,
    override,
)

from svglab import mixins, protocols, serialize, utiltypes
from svglab.attrparse import parse


class _TransformFunctionBase(
    protocols.CustomSerializable, protocols.SupportsNpArray
):
    def __rmatmul__(self, other: protocols.SupportsNpArray) -> Matrix:
        product = np.array(self) @ np.array(other)

        return Matrix.from_array(product)


@final
@pydantic.dataclasses.dataclass
class Matrix(_TransformFunctionBase, mixins.FloatMulDiv):
    a: float
    b: float
    c: float
    d: float
    e: float
    f: float

    @override
    def serialize(self) -> str:
        return serialize.serialize_function_call(
            "matrix", self.a, self.b, self.c, self.d, self.e, self.f
        )

    @override
    def __array__(
        self, dtype: npt.DTypeLike = None, *, copy: bool | None = None
    ) -> utiltypes.NpFloatArray:
        del dtype, copy

        full_matrix = [
            [self.a, self.c, self.e],
            [self.b, self.d, self.f],
            [0, 0, 1],
        ]

        return np.array(full_matrix)

    @classmethod
    def from_array(cls, array: utiltypes.NpFloatArray, /) -> Matrix:
        """Create a `Matrix` instance from a NumPy array.

        The array must be a 3x3 matrix with the last row equal to [0, 0, 1],
        thus representing a 2D transformation matrix in homogeneous
        coordinates.

        Args:
            array: The array to convert to a matrix.

        Returns:
            The matrix represented by the array.

        Raises:
            ValueError: If the array is not a 3x3 matrix or if the last row of
                the array is not equal to [0, 0, 1].

        """
        if array.shape != (3, 3):
            raise ValueError("The array must be a 3x3 matrix")

        (a, c, e), (b, d, f), last_row = array

        if not np.array_equal(last_row, [0, 0, 1]):
            raise ValueError(
                "The last row of the matrix must be [0, 0, 1]"
            )

        return cls(a, b, c, d, e, f)

    @override
    def __mul__(self, other: float) -> Self:
        return type(self)(
            a=self.a * other,
            b=self.b * other,
            c=self.c * other,
            d=self.d * other,
            e=self.e * other,
            f=self.f * other,
        )


def compose(transforms: Iterable[protocols.SupportsNpArray], /) -> Matrix:
    """Compose a series of transformations into a single matrix.

    The transformations are applied in the order they are given.

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
    return functools.reduce(operator.matmul, transforms)


@pydantic.dataclasses.dataclass
class _Translate(_TransformFunctionBase):
    tx: float
    ty: float | None = None

    @override
    def serialize(self) -> str:
        return serialize.serialize_function_call(
            "translate", self.tx, self.ty
        )

    @override
    def __array__(
        self, dtype: npt.DTypeLike = None, *, copy: bool | None = None
    ) -> utiltypes.NpFloatArray:
        del dtype, copy

        tx = self.tx
        ty = self.ty if self.ty is not None else 0

        return np.array(Matrix(1, 0, 0, 1, tx, ty or 0))


@final
class Translate(_Translate):
    @overload
    def __init__(self, tx: float, /) -> None: ...

    @overload
    def __init__(self, tx: float, ty: float, /) -> None: ...

    def __init__(self, tx: float, ty: float | None = None, /) -> None:
        super().__init__(tx, ty)


class PointAddSubWithTranslateRMatmul(
    protocols.SupportsRMatmul["Translate"],
    mixins.AddSub[protocols.PointLike],
    metaclass=abc.ABCMeta,
):
    @override
    def __add__(self, other: protocols.PointLike, /) -> Self:
        return Translate(other.x, other.y) @ self


@pydantic.dataclasses.dataclass
class _Scale(_TransformFunctionBase):
    sx: float
    sy: float | None = None

    @override
    def serialize(self) -> str:
        return serialize.serialize_function_call("scale", self.sx, self.sy)

    @override
    def __array__(
        self, dtype: npt.DTypeLike = None, *, copy: bool | None = None
    ) -> utiltypes.NpFloatArray:
        del dtype, copy

        sx = self.sx
        sy = self.sy if self.sy is not None else self.sx

        return np.array(Matrix(sx, 0, 0, sy, 0, 0))


@final
class Scale(_Scale):
    @overload
    def __init__(self, sx: float, /) -> None: ...

    @overload
    def __init__(self, sx: float, sy: float, /) -> None: ...

    def __init__(self, sx: float, sy: float | None = None, /) -> None:
        super().__init__(sx, sy)


@pydantic.dataclasses.dataclass
class _Rotate(_TransformFunctionBase):
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
        return serialize.serialize_function_call(
            "rotate", self.angle, self.cx, self.cy
        )

    @override
    def __array__(
        self, dtype: npt.DTypeLike = None, *, copy: bool | None = None
    ) -> utiltypes.NpFloatArray:
        del dtype, copy

        a = math.radians(self.angle)

        cos_a = math.cos(a)
        sin_a = math.sin(a)

        rotation = Matrix(cos_a, sin_a, -sin_a, cos_a, 0, 0)

        if self.cx is None:
            return np.array(rotation)

        assert self.cy is not None

        return np.array(
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
        super().__init__(angle, cx, cy)


@final
@pydantic.dataclasses.dataclass
class SkewX(_TransformFunctionBase):
    angle: float

    @override
    def serialize(self) -> str:
        return serialize.serialize_function_call("skewX", self.angle)

    @override
    def __array__(
        self, dtype: npt.DTypeLike = None, *, copy: bool | None = None
    ) -> utiltypes.NpFloatArray:
        del dtype, copy

        a = math.radians(self.angle)

        return np.array(Matrix(1, 0, math.tan(a), 1, 0, 0))


@final
@pydantic.dataclasses.dataclass
class SkewY(_TransformFunctionBase):
    angle: float

    @override
    def serialize(self) -> str:
        return serialize.serialize_function_call("skewY", self.angle)

    @override
    def __array__(
        self, dtype: npt.DTypeLike = None, *, copy: bool | None = None
    ) -> utiltypes.NpFloatArray:
        del dtype, copy

        a = math.radians(self.angle)

        return np.array(Matrix(1, math.tan(a), 0, 1, 0, 0))


TransformFunction: TypeAlias = (
    Translate | Scale | Rotate | SkewX | SkewY | Matrix
)
Transform: TypeAlias = list[TransformFunction]


@lark.v_args(inline=True)
class _Transformer(lark.Transformer[object, Transform]):
    number = float

    translate = Translate
    scale = Scale
    rotate = Rotate
    skew_x = SkewX
    skew_y = SkewY
    matrix = Matrix

    transform_ = parse.v_args_to_list


TransformType: TypeAlias = Annotated[
    Transform,
    parse.get_validator(
        grammar="transform.lark", transformer=_Transformer()
    ),
]
