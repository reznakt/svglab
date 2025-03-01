from __future__ import annotations

import abc
import functools
import math
import operator
from collections.abc import Iterable
from types import NotImplementedType

import affine  # TODO: set appropriate epsilon
import lark
import numpy.typing as npt
import pydantic
from typing_extensions import (
    Annotated,
    Self,
    TypeAlias,
    TypeVar,
    final,
    overload,
    override,
)

from svglab import mixins, protocols, serialize, utils, utiltypes
from svglab.attrparse import parse


class _TransformFunctionBase(
    protocols.CustomSerializable, metaclass=abc.ABCMeta
):
    @abc.abstractmethod
    def to_affine(self) -> affine.Affine:
        """Convert the transformation to an `affine.Affine` instance."""
        ...

    def __array__(
        self, dtype: npt.DTypeLike = None, *, copy: bool | None = None
    ) -> utiltypes.NpFloatArray:
        return self.to_affine().__array__(dtype=dtype, copy=copy)

    @overload
    def __matmul__(  # type: ignore[reportOverlappingOverload]
        self, other: _TransformFunctionBase
    ) -> Matrix: ...

    @overload
    def __matmul__(self, other: object) -> NotImplementedType: ...

    def __matmul__(self, other: object) -> Matrix | NotImplementedType:
        if not isinstance(other, _TransformFunctionBase):
            return NotImplemented

        product = self.to_affine() @ other.to_affine()
        assert isinstance(product, affine.Affine)

        return Matrix.from_affine(product)


@final
@pydantic.dataclasses.dataclass
class Matrix(_TransformFunctionBase):
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
    def to_affine(self) -> affine.Affine:
        # ! affine uses different labels for the matrix elements

        return affine.Affine(
            self.a, self.c, self.e, self.b, self.d, self.f
        )

    @classmethod
    def from_affine(cls, matrix: affine.Affine, /) -> Self:
        """Create a `Matrix` instance from an `affine.Affine` instance."""
        # ! affine uses different labels for the matrix elements

        return cls(
            matrix.a, matrix.d, matrix.b, matrix.e, matrix.c, matrix.f
        )


@pydantic.dataclasses.dataclass
class _Translate(_TransformFunctionBase):
    tx: float
    ty: float

    @override
    def serialize(self) -> str:
        args = [self.tx]

        if not utils.is_close(self.ty, 0):
            args.append(self.ty)

        return serialize.serialize_function_call("translate", *args)

    @override
    def to_affine(self) -> affine.Affine:
        return affine.Affine.translation(self.tx, self.ty or 0)


@final
class Translate(_Translate):
    @overload
    def __init__(self, tx: float, /) -> None: ...

    @overload
    def __init__(self, tx: float, ty: float, /) -> None: ...

    def __init__(self, tx: float, ty: float = 0, /) -> None:
        super().__init__(tx, ty)


@pydantic.dataclasses.dataclass
class _Scale(_TransformFunctionBase):
    sx: float
    sy: float

    @override
    def serialize(self) -> str:
        args = [self.sx]

        if not utils.is_close(self.sx, self.sy):
            args.append(self.sy)

        return serialize.serialize_function_call("scale", *args)

    @override
    def to_affine(self) -> affine.Affine:
        return affine.Affine.scale(self.sx, self.sy or self.sx)


@final
class Scale(_Scale):
    @overload
    def __init__(self, sx: float, /) -> None: ...

    @overload
    def __init__(self, sx: float, sy: float, /) -> None: ...

    def __init__(self, sx: float, sy: float | None = None, /) -> None:
        super().__init__(sx, sy if sy is not None else sx)


@pydantic.dataclasses.dataclass
class _Rotate(_TransformFunctionBase):
    angle: float
    cx: float
    cy: float

    @override
    def serialize(self) -> str:
        args = [self.angle]

        if not utils.is_close(self.cx, 0) or not utils.is_close(
            self.cy, 0
        ):
            args.extend([self.cx, self.cy])

        return serialize.serialize_function_call("rotate", *args)

    @override
    def to_affine(self) -> affine.Affine:
        return affine.Affine.rotation(
            self.angle, (self.cx or 0, self.cy or 0)
        )


@final
class Rotate(_Rotate):
    @overload
    def __init__(self, angle: float, /) -> None: ...

    @overload
    def __init__(self, angle: float, /, cx: float, cy: float) -> None: ...

    def __init__(
        self, angle: float, /, cx: float = 0, cy: float = 0
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
    def to_affine(self) -> affine.Affine:
        return affine.Affine.shear(x_angle=self.angle)


@final
@pydantic.dataclasses.dataclass
class SkewY(_TransformFunctionBase):
    angle: float

    @override
    def serialize(self) -> str:
        return serialize.serialize_function_call("skewY", self.angle)

    @override
    def to_affine(self) -> affine.Affine:
        return affine.Affine.shear(y_angle=self.angle)


TransformFunction: TypeAlias = (
    Translate | Scale | Rotate | SkewX | SkewY | Matrix
)


def compose(transforms: Iterable[TransformFunction], /) -> Matrix:
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


class PointAddSubWithTranslateRMatmul(
    protocols.SupportsRMatmul["Translate"],
    mixins.AddSub[protocols.PointLike],
    metaclass=abc.ABCMeta,
):
    @override
    def __add__(self, other: protocols.PointLike, /) -> Self:
        return Translate(other.x, other.y) @ self


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

_TransformT1 = TypeVar("_TransformT1", bound=TransformFunction)
_TransformT2 = TypeVar("_TransformT2", bound=TransformFunction)


def _tan(angle: float, /) -> float:
    return math.tan(math.radians(angle))


def _arctan(tan: float, /) -> float:
    return math.degrees(math.atan(tan))


def _swap_transforms(  # noqa: C901, PLR0911
    a: _TransformT1, b: _TransformT2, /
) -> tuple[_TransformT2, _TransformT1]:
    """Swap transforms, adjusting parameters so that the result is equal.

    Args:
        a: The first transform.
        b: The second transform.

    Returns:
        A 2-tuple (b', a') where b' and a' are the adjusted transforms.

    Raises:
        ValueError: If the transforms cannot be swapped.

    Examples:
        >>> _swap_transforms(Translate(10, 20), Scale(2, 3))
        (Scale(sx=2.0, sy=3.0), Translate(tx=5.0, ty=6.666666666666667))
        >>> _swap_transforms(Scale(2, 3), SkewX(45))
        (SkewX(angle=33.690067525979785), Scale(sx=2.0, sy=3.0))
        >>> _swap_transforms(SkewX(45), Translate(10, 20))
        (Translate(tx=-9.999999999999996, ty=20.0), SkewX(angle=45.0))

    """
    if type(a) is type(b):
        return b, a

    match a, b:
        case Translate(tx, ty), Scale(sx, sy) as scale:
            return scale, type(a)(tx / sx, ty / sy)

        case Scale(sx, sy) as scale, Translate(tx, ty):
            return type(b)(sx * tx, sy * ty), scale

        case SkewX(angle) as skew_x, Translate(tx, ty):
            return type(b)(tx - ty * _tan(angle), ty), skew_x

        case Translate(tx, ty), SkewX(angle) as skew_x:
            return skew_x, type(a)(tx + ty * _tan(angle), ty)

        case Scale(sx, sy) as scale, SkewX(angle):
            angle = _arctan(sx / sy * _tan(angle))
            return type(b)(angle), scale

        case SkewX(angle), Scale(sx, sy) as scale:
            angle = _arctan(sy / sx * _tan(angle))
            return scale, type(a)(angle)

        case SkewY(angle) as skew_y, Translate(tx, ty):
            return type(b)(tx, ty - tx * _tan(angle)), skew_y

        case Translate(tx, ty), SkewY(angle) as skew_y:
            return skew_y, type(a)(tx, ty + tx * _tan(angle))

        case Scale(sx, sy) as scale, SkewY(angle):
            angle = _arctan(sy / sx * _tan(angle))
            return type(b)(angle), scale

        case SkewY(angle), Scale(sx, sy) as scale:
            angle = _arctan(sx / sy * _tan(angle))

            return scale, type(a)(angle)
        case _:
            msg = f"Swapping {type(a)} and {type(b)} is not supported"
            raise ValueError(msg)


def prepend_transform_list(
    transform: Iterable[TransformFunction], func: TransformFunction
) -> list[TransformFunction]:
    """Prepend a transformation to a list of transformations.

    The parameters of the transformations are adjusted so that the result is
    visually equivalent to appending the original transformation to the list.

    Args:
        transform: A sequence of transformations.
        func: The transformation to prepend.

    Returns:
        A new list of transformations with the transformation prepended.

    Examples:
        >>> prepend_transform_list([Translate(10, 20)], Scale(2, 3))
        [Scale(sx=2.0, sy=3.0), Translate(tx=5.0, ty=6.666666666666667)]

    """
    result = [*transform, func]

    for i in range(len(result) - 1, 0, -1):
        result[i - 1], result[i] = _swap_transforms(
            result[i - 1], result[i]
        )

    return result
