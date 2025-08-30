"""Definition of the SVG `<transform-list>` type and transformation functions.

Use `Transform` to represent transform lists in SVG.
Use `TransformType` in Pydantic fields.

Use `Translate`, `Scale`, `Rotate`, `SkewX`, `SkewY`, and `Matrix` to represent
transformations. Use `TransformFunction` to represent any transformation. Use
`Reifiable` to represent transformations that can be reified.
"""

from __future__ import annotations

import abc
import functools
import math
import operator
from collections.abc import Iterable
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

from svglab import mixins, protocols, serialize, utiltypes
from svglab.attrparse import parse
from svglab.utils import mathutils, miscutils


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
class _Scale(_TransformFunctionBase):
    sx: float
    sy: float

    @override
    def serialize(self) -> str:
        args = [self.sx]

        if not mathutils.is_close(self.sx, self.sy):
            args.append(self.sy)

        return serialize.serialize_function_call(
            "scale", *args, precision_group="scale"
        )

    @override
    def to_affine(self) -> affine.Affine:
        return affine.Affine.scale(self.sx, self.sy or self.sx)

    @override
    def __eq__(self, other: object, /) -> bool:
        if not miscutils.basic_compare(other, self=self):
            return False

        return mathutils.is_close(
            self.sx, other.sx
        ) and mathutils.is_close(self.sy, other.sy)

    @override
    def __hash__(self) -> int:
        return hash((type(self), self.sx, self.sy))


@final
class Scale(_Scale):
    """A transformation that scales a shape by a given factor."""

    @overload
    def __init__(self, sx: float, /) -> None: ...

    @overload
    def __init__(self, sx: float, sy: float, /) -> None: ...

    def __init__(self, sx: float, sy: float | None = None, /) -> None:
        """Initialize a `Scale` transformation.

        Args:
            sx: The scaling factor on the x-axis.
            sy: The scaling factor on the y-axis. If not given, is assumed to
                be equal to `sx`.

        """
        super().__init__(sx, sy if sy is not None else sx)


@pydantic.dataclasses.dataclass(frozen=True)
class _Rotate(_TransformFunctionBase):
    angle: float
    cx: float
    cy: float

    @override
    def serialize(self) -> str:
        angle = serialize.serialize(self.angle, precision_group="angle")
        origin = []

        if not mathutils.is_close(self.cx, 0) or not mathutils.is_close(
            self.cy, 0
        ):
            origin.extend([self.cx, self.cy])

        return serialize.serialize_function_call("rotate", angle, *origin)

    @override
    def to_affine(self) -> affine.Affine:
        return affine.Affine.rotation(
            self.angle, (self.cx or 0, self.cy or 0)
        )

    @override
    def __eq__(self, other: object, /) -> bool:
        if not miscutils.basic_compare(other, self=self):
            return False

        return (
            mathutils.is_close(self.angle, other.angle)
            and mathutils.is_close(self.cx, other.cx)
            and mathutils.is_close(self.cy, other.cy)
        )

    @override
    def __hash__(self) -> int:
        return hash((type(self), self.angle, self.cx, self.cy))


@final
class Rotate(_Rotate):
    """A transformation that rotates a shape by a given angle."""

    @overload
    def __init__(self, angle: float, /) -> None: ...

    @overload
    def __init__(self, angle: float, /, cx: float, cy: float) -> None: ...

    def __init__(
        self, angle: float, /, cx: float = 0, cy: float = 0
    ) -> None:
        """Initialize a `Rotate` transformation.

        Args:
            angle: The angle to rotate the shape by, in degrees. The rotation
                is counter-clockwise.
            cx: The x-coordinate of the point to rotate around. If not given,
                is assumed to be 0.
            cy: The y-coordinate of the point to rotate around. If not given,
                is assumed to be 0.

        """
        super().__init__(angle, cx, cy)


@final
@pydantic.dataclasses.dataclass(frozen=True)
class SkewY(_TransformFunctionBase):
    """A transformation that skews a shape along the y-axis.

    The shape is skewed by `angle` degrees along the y-axis.
    """

    angle: float

    @override
    def serialize(self) -> str:
        return serialize.serialize_function_call(
            "skewY", self.angle, precision_group="angle"
        )

    @override
    def to_affine(self) -> affine.Affine:
        return affine.Affine.shear(y_angle=self.angle)

    @override
    def __eq__(self, other: object, /) -> bool:
        if not miscutils.basic_compare(other, self=self):
            return False

        return mathutils.is_close(self.angle, other.angle)

    @override
    def __hash__(self) -> int:
        return hash((type(self), self.angle))


@final
@pydantic.dataclasses.dataclass(frozen=True)
class SkewX(_TransformFunctionBase):
    """A transformation that skews a shape along the x-axis.

    The shape is skewed by `angle` degrees along the x-axis.
    """

    angle: float

    @override
    def serialize(self) -> str:
        return serialize.serialize_function_call(
            "skewX", self.angle, precision_group="angle"
        )

    @override
    def to_affine(self) -> affine.Affine:
        return affine.Affine.shear(x_angle=self.angle)

    @override
    def __eq__(self, other: object, /) -> bool:
        if not miscutils.basic_compare(other, self=self):
            return False

        return mathutils.is_close(self.angle, other.angle)

    @override
    def __hash__(self) -> int:
        return hash((type(self), self.angle))


def _transform_weight(transform: Iterable[TransformFunction], /) -> int:
    """Calculate the weight of a transformation.

    The weight is used to determine the best decomposition of a matrix.

    Args:
        transform: The transformation to calculate the weight of.

    Returns:
        The weight of the transformation - the higher the weight, the more
        complex the transformation.

    """
    weight = 0

    for t in transform:
        match t:
            case SkewX() | SkewY():
                weight += 1_000_000
            case Scale(sx, sy) if not mathutils.is_close(sx, sy):
                weight += 1_000_000
            case Rotate():
                weight += 1_000
            case _:
                weight += 1

    return weight


@pydantic.dataclasses.dataclass(frozen=True)
class _Translate(_TransformFunctionBase):
    tx: float
    ty: float

    @override
    def serialize(self) -> str:
        args = [self.tx]

        if not mathutils.is_close(self.ty, 0):
            args.append(self.ty)

        return serialize.serialize_function_call("translate", *args)

    @override
    def to_affine(self) -> affine.Affine:
        return affine.Affine.translation(self.tx, self.ty or 0)

    @override
    def __eq__(self, other: object, /) -> bool:
        if not miscutils.basic_compare(other, self=self):
            return False

        return mathutils.is_close(
            self.tx, other.tx
        ) and mathutils.is_close(self.ty, other.ty)

    @override
    def __hash__(self) -> int:
        return hash((type(self), self.tx, self.ty))


@final
class Translate(_Translate):
    """A transformation that translates a shape by a given distance."""

    @overload
    def __init__(self, tx: float, /) -> None: ...

    @overload
    def __init__(self, tx: float, ty: float, /) -> None: ...

    def __init__(self, tx: float, ty: float = 0, /) -> None:
        """Initialize a `Translate` transformation.

        Args:
            tx: The distance to translate the shape by on the x-axis.
            ty: The distance to translate the shape by on the y-axis. If not
                given, is assumed to be equal to 0.

        """
        super().__init__(tx, ty)


def _remove_redundant_transformations(
    transform: Iterable[TransformFunction],
) -> Transform:
    result: Transform = []

    for t in transform:
        match t:
            case Translate(tx, ty) if mathutils.is_close(
                tx, 0
            ) and mathutils.is_close(ty, 0):
                continue
            case Scale(sx, sy) if mathutils.is_close(
                sx, 1
            ) and mathutils.is_close(sy, 1):
                continue
            case Rotate(angle) | SkewX(angle) | SkewY(angle) if (
                mathutils.is_close(angle, 0)
            ):
                continue
            case _:
                result.append(t)

    return result


@final
@pydantic.dataclasses.dataclass(frozen=True)
class Matrix(_TransformFunctionBase):
    """An arbitrary affine transformation.

    The transformation is represented by a 3x3 matrix in homogeneous
    coordinates:
    ```
    | a c e |
    | b d f |
    | 0 0 1 |
    ```
    """

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

    def __qr_decompose(self) -> Transform:
        result: Transform = []
        a, b, c, d, e, f = self.to_tuple()

        # we prefer to use r over s if possible
        if not mathutils.is_close(a, 0) or not mathutils.is_close(b, 0):
            result.append(Translate(e, f))

            r = _magnitude((a, b))
            angle = mathutils.signum(b) * mathutils.arccos(a / r)
            result.append(Rotate(angle))

            det = self.determinant()
            result.append(Scale(r, det / r))

            col_dot = _dot_product((a, b), (c, d))
            angle = mathutils.arctan(col_dot / r**2)
            result.append(SkewX(angle))

        # if r is unsuitable, we use s
        elif not mathutils.is_close(c, 0) or not mathutils.is_close(d, 0):
            result.append(Translate(e, f))

            s = _magnitude((c, d))
            angle = 90 - mathutils.signum(d) * mathutils.arccos(-c / s)
            result.append(Rotate(angle))

            det = self.determinant()
            result.append(Scale(det / s, s))

            col_dot = _dot_product((a, b), (c, d))
            angle = mathutils.arctan(col_dot / s**2)
            result.append(SkewY(angle))

        # degenrate transformation
        else:
            result.append(Scale(0))

        return result

    def __ldu_decompose(self) -> Transform:
        result: Transform = []
        a, b, c, d, e, f = self.to_tuple()

        result.append(Translate(e, f))

        if not mathutils.is_close(a, 0):
            result.append(SkewY(mathutils.arctan(b / a)))
            result.append(Scale(a, self.determinant() / a))
            result.append(SkewX(mathutils.arctan(c / a)))
        elif not mathutils.is_close(b, 0):
            result.append(Rotate(90))
            result.append(Scale(b, self.determinant() / b))
            result.append(SkewY(mathutils.arctan(d / b)))
        else:
            result.append(Scale(c, d))
            result.append(SkewX(45))
            result.append(Scale(0, 1))

        return result

    def decompose(self) -> Transform:
        """Decompose the matrix into elementary transformations.

        The result is a list of transformations that, when composed, are
        equivalent to the original matrix.

        The algorithm is based on Frédéric Wang's [Decomposition of
        2D-transform matrices](https://frederic-wang.fr/2013/12/01/decomposition-of-2d-transform-matrices/).

        Two decomposition methods are used: QR and LDU. The
        final decomposition is chosen based on which method produces the
        transformation with the lowest complexity.

        Returns:
            A transformation list composed of elementary transformations.

        Examples:
        >>> m = Translate(10, 20).to_matrix()
        >>> m.decompose()
        [Translate(tx=10.0, ty=20.0)]
        >>> m = SkewY(45).to_matrix()
        >>> m.decompose()
        [SkewY(angle=45.0)]
        >>> m = Translate(10, 20) @ Scale(2, 2)
        >>> m.decompose()
        [Translate(tx=10.0, ty=20.0), Scale(sx=2.0, sy=2.0)]

        """
        decompositions = [self.__ldu_decompose(), self.__qr_decompose()]

        return min(
            map(_remove_redundant_transformations, decompositions),
            key=_transform_weight,
        )

    @override
    def __eq__(self, other: object, /) -> bool:
        if not miscutils.basic_compare(other, self=self):
            return False

        return all(
            mathutils.is_close(x1, x2)
            for x1, x2 in zip(
                self.to_tuple(), other.to_tuple(), strict=True
            )
        )

    @override
    def __hash__(self) -> int:
        return hash((type(self), self.to_tuple()))


TransformFunction: TypeAlias = (
    Translate | Scale | Rotate | SkewX | SkewY | Matrix
)
"""A function that represents a transformation."""

Transform: TypeAlias = list[TransformFunction]
"""A list of transformations."""

Reifiable: TypeAlias = Translate | Scale
"""A transformation that can be reified."""


def decompose_matrices(transform: Transform) -> None:
    """Decompose matrices in a transformation list into elementary transforms.

    See `Matrix.decompose` for more information.

    Args:
        transform: The transformation list to decompose.

    Examples:
        >>> transform = [Matrix(1, 0, 0, 1, 10, 20)]
        >>> decompose_matrices(transform)
        >>> transform
        [Translate(tx=10.0, ty=20.0)]

    """
    i = 0

    while i < len(transform):
        transformation = transform[i]

        if not isinstance(transformation, Matrix):
            i += 1
            continue

        decomposition = transformation.decompose()
        transform[i : i + 1] = decomposition

        i += len(decomposition)


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
    """Implement moving by a vector using multiplication with `Translate`."""

    @override
    def __add__(self, other: protocols.PointLike, /) -> Self:
        return Translate(other.x, other.y) @ self


@lark.v_args(inline=True)
class _Transformer(lark.Transformer[object, Transform]):
    number = parse.FiniteFloat

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
