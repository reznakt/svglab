from __future__ import annotations

import abc
import functools
import math
import operator
from collections.abc import Iterable, Iterator
from types import NotImplementedType

import affine
import lark
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

from svglab import mixins, protocols, serialize, utils, utiltypes
from svglab.attrparse import parse


_Vector: TypeAlias = tuple[float, float]
"""A 2D vector."""


def _dot_product(u: _Vector, v: _Vector, /) -> float:
    """Calculate the dot product of two vectors.

    Args:
        u: The first vector.
        v: The second vector.

    Returns:
        The dot product of the two vectors.

    Examples:
        >>> _dot_product((1.0, 2.0), (3.0, 4.0))
        11.0
        >>> _dot_product((1.0, 2.0), (1.0, 2.0))
        5.0
        >>> _dot_product((1.0, 2.0), (0.0, 0.0))
        0.0

    """
    u1, u2 = u
    v1, v2 = v

    return u1 * v1 + u2 * v2


def _magnitude(u: _Vector, /) -> float:
    """Calculate the magnitude of a vector.

    Args:
        u: The vector.

    Returns:
        The magnitude of the vector.

    Examples:
        >>> _magnitude((3, 4))
        5.0
        >>> _magnitude((0, 0))
        0.0
        >>> _magnitude((1, 2))
        2.23606797749979

    """
    return math.sqrt(_dot_product(u, u))


class _TransformFunctionBase(
    protocols.CustomSerializable, metaclass=abc.ABCMeta
):
    @abc.abstractmethod
    def to_affine(self) -> affine.Affine:
        """Convert the transformation to an `affine.Affine` instance."""
        ...

    def to_matrix(self) -> Matrix:
        """Convert the transformation to a `Matrix` instance.

        Returns:
            The transformation as a matrix.

        Examples:
            >>> t = Translate(10, 20)
            >>> t.to_matrix()
            Matrix(a=1.0, b=0.0, c=0.0, d=1.0, e=10.0, f=20.0)
            >>> Matrix(1, 2, 3, 4, 5, 6).to_matrix()
            Matrix(a=1.0, b=2.0, c=3.0, d=4.0, e=5.0, f=6.0)

        """
        return Matrix.from_affine(self.to_affine())

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


@pydantic.dataclasses.dataclass(frozen=True)
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

    def __eq__(self, other: object, /) -> bool:
        if not utils.basic_compare(other, self=self):
            return False

        return utils.is_close(self.tx, other.tx) and utils.is_close(
            self.ty, other.ty
        )


@final
class Translate(_Translate):
    @overload
    def __init__(self, tx: float, /) -> None: ...

    @overload
    def __init__(self, tx: float, ty: float, /) -> None: ...

    def __init__(self, tx: float, ty: float = 0, /) -> None:
        super().__init__(tx, ty)


@pydantic.dataclasses.dataclass(frozen=True)
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

    def __eq__(self, other: object, /) -> bool:
        if not utils.basic_compare(other, self=self):
            return False

        return utils.is_close(self.sx, other.sx) and utils.is_close(
            self.sy, other.sy
        )


@final
class Scale(_Scale):
    @overload
    def __init__(self, sx: float, /) -> None: ...

    @overload
    def __init__(self, sx: float, sy: float, /) -> None: ...

    def __init__(self, sx: float, sy: float | None = None, /) -> None:
        super().__init__(sx, sy if sy is not None else sx)


@pydantic.dataclasses.dataclass(frozen=True)
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

    def __eq__(self, other: object, /) -> bool:
        if not utils.basic_compare(other, self=self):
            return False

        return (
            utils.is_close(self.angle, other.angle)
            and utils.is_close(self.cx, other.cx)
            and utils.is_close(self.cy, other.cy)
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
@pydantic.dataclasses.dataclass(frozen=True)
class SkewY(_TransformFunctionBase):
    angle: float

    @override
    def serialize(self) -> str:
        return serialize.serialize_function_call("skewY", self.angle)

    @override
    def to_affine(self) -> affine.Affine:
        return affine.Affine.shear(y_angle=self.angle)

    def __eq__(self, other: object, /) -> bool:
        if not utils.basic_compare(other, self=self):
            return False

        return utils.is_close(self.angle, other.angle)


@final
@pydantic.dataclasses.dataclass(frozen=True)
class SkewX(_TransformFunctionBase):
    angle: float

    @override
    def serialize(self) -> str:
        return serialize.serialize_function_call("skewX", self.angle)

    @override
    def to_affine(self) -> affine.Affine:
        return affine.Affine.shear(x_angle=self.angle)

    def __eq__(self, other: object, /) -> bool:
        if not utils.basic_compare(other, self=self):
            return False

        return utils.is_close(self.angle, other.angle)


def _remove_redundant_transformations(
    transform: Iterable[TransformFunction],
) -> Iterator[TransformFunction]:
    for t in transform:
        match t:
            case Translate(tx, ty) if utils.is_close(
                tx, 0
            ) and utils.is_close(ty, 0):
                continue
            case Scale(sx, sy) if utils.is_close(sx, 1) and utils.is_close(
                sy, 1
            ):
                continue
            case Rotate(angle) | SkewX(angle) | SkewY(angle) if (
                utils.is_close(angle, 0)
            ):
                continue
            case _:
                yield t


@final
@pydantic.dataclasses.dataclass(frozen=True)
class Matrix(_TransformFunctionBase):
    a: float
    b: float
    c: float
    d: float
    e: float
    f: float

    @classmethod
    def identity(cls) -> Self:
        """Create an identity matrix."""
        return cls(1, 0, 0, 1, 0, 0)

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

    def to_tuple(self) -> tuple[float, float, float, float, float, float]:
        """Convert the matrix to a tuple.

        Returns:
            The matrix as a tuple.

        Examples:
            >>> m = Matrix(1, 2, 3, 4, 5, 6)
            >>> m.to_tuple()
            (1.0, 2.0, 3.0, 4.0, 5.0, 6.0)

        """
        return self.a, self.b, self.c, self.d, self.e, self.f

    def determinant(self) -> float:
        """Calculate the determinant of the matrix.

        The determinant shows how the matrix scales the area of a shape.
        For example, a determinant of 1 means the area is unchanged.
        The determinant of 0 means the transformation is degenrate.

        Returns:
            The determinant of the matrix.

        Examples:
            >>> m = Matrix(1, 2, 3, 4, 5, 6)
            >>> m.determinant()
            -2.0

        """
        return self.to_affine().determinant

    def __qr_decompose(self) -> Iterator[TransformFunction]:
        a, b, c, d, e, f = self.to_tuple()

        # we prefer to use r over s if possible
        if not utils.is_close(a, 0) or not utils.is_close(b, 0):
            yield Translate(e, f)

            r = _magnitude((a, b))
            angle = utils.signum(b) * utils.arccos(a / r)
            yield Rotate(angle)

            det = self.determinant()
            yield Scale(r, det / r)

            col_dot = _dot_product((a, b), (c, d))
            angle = utils.arctan(col_dot / r**2)
            yield SkewX(angle)

        # if r is unsuitable, we use s
        elif not utils.is_close(c, 0) or not utils.is_close(d, 0):
            yield Translate(e, f)

            s = _magnitude((c, d))
            angle = 90 - utils.signum(d) * utils.arccos(-c / s)

            yield Rotate(angle)

            det = self.determinant()
            yield Scale(det / s, s)

            col_dot = _dot_product((a, b), (c, d))
            angle = utils.arctan(col_dot / s**2)
            yield SkewY(angle)

        # degenrate transformation
        else:
            yield Scale(0)

    def __ldu_decompose(self) -> Iterator[TransformFunction]:
        a, b, c, d, e, f = self.to_tuple()

        yield Translate(e, f)

        if not utils.is_close(a, 0):
            yield SkewY(utils.arctan(b / a))
            yield Scale(a, self.determinant() / a)
            yield SkewX(utils.arctan(c / a))
        elif not utils.is_close(b, 0):
            yield Rotate(90)
            yield Scale(b, self.determinant() / b)
            yield SkewY(utils.arctan(d / b))
        else:
            yield Scale(c, d)
            yield SkewX(45)
            yield Scale(0, 1)

    def decompose(self) -> Iterator[TransformFunction]:
        if self == Matrix.identity():
            return

        ldu = _remove_redundant_transformations(self.__ldu_decompose())
        qr = _remove_redundant_transformations(self.__qr_decompose())

        ldu_length, ldu = utils.length(ldu)
        qr_length, qr = utils.length(qr)

        if ldu_length < qr_length:
            yield from ldu
        else:
            yield from qr

    def __eq__(self, other: object, /) -> bool:
        if not utils.basic_compare(other, self=self):
            return False

        for x1, x2 in zip(self.to_tuple(), other.to_tuple(), strict=True):
            if not utils.is_close(x1, x2):
                return False

        return True


TransformFunction: TypeAlias = (
    Translate | Scale | Rotate | SkewX | SkewY | Matrix
)
"""A function that represents a transformation."""

Reifiable: TypeAlias = Translate | Scale
"""A transformation that can be reified."""

Transform: TypeAlias = list[TransformFunction]
"""A list of transformations."""


def compose(transforms: Iterable[TransformFunction], /) -> Matrix:
    """Compose a series of transformations into a single matrix.

    The transformations are applied in the order they are given.

    If no transformations are given, the identity matrix is returned.

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
        >>> compose([m1]) == m1
        True
        >>> compose([]) == Matrix.identity()
        True

    """
    return functools.reduce(operator.matmul, transforms, Matrix.identity())


class PointAddSubWithTranslateRMatmul(
    protocols.SupportsRMatmul["Translate"],
    mixins.AddSub[protocols.PointLike],
    metaclass=abc.ABCMeta,
):
    @override
    def __add__(self, other: protocols.PointLike, /) -> Self:
        return Translate(other.x, other.y) @ self


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
