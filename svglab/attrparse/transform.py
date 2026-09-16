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

import lark
import numpy as np
import numpy.typing as npt
from typing_extensions import (
    Annotated,
    Self,
    TypeAlias,
    final,
    overload,
    override,
)

from svglab import errors, mixins, models, protocols, serialize, utiltypes
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


class _TransformFunctionBase(
    protocols.CustomSerializable, metaclass=abc.ABCMeta
):
    @abc.abstractmethod
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
        ...

    def __array__(
        self,
        dtype: npt.DTypeLike | None = None,
        *,
        copy: bool | None = None,
    ) -> utiltypes.NpFloatArray:
        if copy is False:
            raise ValueError(
                "copy=False is not supported since the array is dynamically"
                " generated."
            )

        a, b, c, d, e, f = self.to_matrix().to_tuple()

        # fmt: off
        layout = [
            [a, c, e],
            [b, d, f],
            [0, 0, 1]
        ]
        # fmt: on

        return np.array(layout, dtype=dtype, copy=copy)

    @overload
    def __matmul__(  # type: ignore[reportOverlappingOverload]
        self, other: _TransformFunctionBase
    ) -> Matrix: ...

    @overload
    def __matmul__(self, other: object) -> NotImplementedType: ...

    def __matmul__(self, other: object) -> Matrix | NotImplementedType:
        if not isinstance(other, _TransformFunctionBase):
            return NotImplemented

        prod = np.array(self) @ np.array(other)

        return Matrix(
            a=prod[0, 0],
            b=prod[1, 0],
            c=prod[0, 1],
            d=prod[1, 1],
            e=prod[0, 2],
            f=prod[1, 2],
        )


@models.dataclass(frozen=True, config=models.DATACLASS_CONFIG)
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
    def to_matrix(self) -> Matrix:
        return Matrix(a=self.sx, b=0, c=0, d=self.sy, e=0, f=0)

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
    """A transformation that scales a shape by a given factor.

    Examples:
        >>> Scale(2).to_matrix()
        Matrix(a=2.0, b=0.0, c=0.0, d=2.0, e=0.0, f=0.0)
        >>> Scale(2, 3).to_matrix()
        Matrix(a=2.0, b=0.0, c=0.0, d=3.0, e=0.0, f=0.0)
        >>> Scale(2, 0).to_matrix()
        Matrix(a=2.0, b=0.0, c=0.0, d=0.0, e=0.0, f=0.0)

    """

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


@models.dataclass(frozen=True, config=models.DATACLASS_CONFIG)
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
    def to_matrix(self) -> Matrix:
        sin_a = mathutils.sin(self.angle)
        cos_a = mathutils.cos(self.angle)

        rot = Matrix(a=cos_a, b=sin_a, c=-sin_a, d=cos_a, e=0, f=0)

        if mathutils.is_close(self.cx, 0) and mathutils.is_close(
            self.cy, 0
        ):
            return rot

        # translate to origin, rotate, translate back
        return (
            Translate(self.cx, self.cy)
            @ rot
            @ Translate(-self.cx, -self.cy)
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
@models.dataclass(frozen=True, config=models.DATACLASS_CONFIG)
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
    def to_matrix(self) -> Matrix:
        return Matrix(a=1, b=mathutils.tan(self.angle), c=0, d=1, e=0, f=0)

    @override
    def __eq__(self, other: object, /) -> bool:
        if not miscutils.basic_compare(other, self=self):
            return False

        return mathutils.is_close(self.angle, other.angle)

    @override
    def __hash__(self) -> int:
        return hash((type(self), self.angle))


@final
@models.dataclass(frozen=True, config=models.DATACLASS_CONFIG)
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
    def to_matrix(self) -> Matrix:
        return Matrix(a=1, b=0, c=mathutils.tan(self.angle), d=1, e=0, f=0)

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


@models.dataclass(frozen=True, config=models.DATACLASS_CONFIG)
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
    def to_matrix(self) -> Matrix:
        return Matrix(a=1, b=0, c=0, d=1, e=self.tx, f=self.ty)

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
@models.dataclass(frozen=True, config=models.DATACLASS_CONFIG)
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
    def to_matrix(self) -> Matrix:
        return self

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
        The determinant of 0 means the transformation is degenerate.

        Returns:
            The determinant of the matrix.

        Examples:
            >>> m = Matrix(1, 2, 3, 4, 5, 6)
            >>> m.determinant()
            -2.0

        """
        return self.a * self.d - self.b * self.c

    def is_singular(self) -> bool:
        """Check whether the matrix collapses the plane onto a line or point.

        A singular transformation cannot be undone, so shapes transformed by
        it cannot be recovered.

        Returns:
            `True` if the determinant of the matrix is zero.

        Examples:
            >>> Scale(0).to_matrix().is_singular()
            True
            >>> Scale(2).to_matrix().is_singular()
            False

        """
        return mathutils.is_close(self.determinant(), 0)

    def inverse(self) -> Matrix:
        """Compute the inverse of the matrix.

        Returns:
            The matrix that undoes this transformation.

        Raises:
            SvgSingularMatrixError: If the matrix is singular.

        Examples:
            >>> Translate(10, 20).to_matrix().inverse()
            Matrix(a=1.0, b=0.0, c=0.0, d=1.0, e=-10.0, f=-20.0)
            >>> Scale(2).to_matrix().inverse()
            Matrix(a=0.5, b=0.0, c=0.0, d=0.5, e=0.0, f=0.0)

        """
        det = self.determinant()

        if mathutils.is_close(det, 0):
            raise errors.SvgSingularMatrixError(self)

        a, b, c, d, e, f = self.to_tuple()

        return Matrix(
            a=mathutils.normalize_zero(d / det),
            b=mathutils.normalize_zero(-b / det),
            c=mathutils.normalize_zero(-c / det),
            d=mathutils.normalize_zero(a / det),
            e=mathutils.normalize_zero((c * f - d * e) / det),
            f=mathutils.normalize_zero((b * e - a * f) / det),
        )

    def linear(self) -> Matrix:
        """Drop the translation, keeping only the linear part of the matrix.

        Examples:
            >>> Matrix(1, 2, 3, 4, 5, 6).linear()
            Matrix(a=1.0, b=2.0, c=3.0, d=4.0, e=0.0, f=0.0)

        """
        return Matrix(a=self.a, b=self.b, c=self.c, d=self.d, e=0, f=0)

    def translation(self) -> Translate:
        """Extract the translation applied after the linear part.

        Examples:
            >>> Matrix(1, 2, 3, 4, 5, 6).translation()
            Translate(tx=5.0, ty=6.0)

        """
        return Translate(self.e, self.f)

    def split_translation(self) -> tuple[Matrix, Translate]:
        """Split the matrix into a linear part and a trailing translation.

        The matrix is factored as `linear @ translate`, so that the
        translation is the *rightmost* factor and is therefore the part that
        an element can absorb into its coordinate attributes without
        disturbing anything that precedes it.

        Returns:
            A 2-tuple `(linear, translate)` whose composition equals this
            matrix.

        Raises:
            SvgSingularMatrixError: If the matrix is singular.

        Examples:
            >>> m = Matrix(2, 0, 0, 2, 10, 20)
            >>> linear, translate = m.split_translation()
            >>> linear
            Matrix(a=2.0, b=0.0, c=0.0, d=2.0, e=0.0, f=0.0)
            >>> translate
            Translate(tx=5.0, ty=10.0)
            >>> linear @ translate == m
            True

        """
        linear = self.linear()
        inv = linear.inverse()

        return linear, Translate(
            inv.a * self.e + inv.c * self.f,
            inv.b * self.e + inv.d * self.f,
        )

    def qr_decompose(self) -> tuple[Matrix, Matrix]:
        """Split the linear part of the matrix into a rotation and the rest.

        The linear part is factored as `q @ r`, where `q` is a pure rotation
        (never a reflection) and `r` is upper triangular. `r` describes the
        shape change that survives the rotation: its diagonal holds the scale
        factors along the two axes and its off-diagonal entry is non-zero
        exactly when the transformation shears.

        The translation of this matrix is not part of either factor.

        Returns:
            A 2-tuple `(q, r)` of matrices with no translation.

        Raises:
            SvgSingularMatrixError: If the matrix is singular.

        Examples:
            >>> q, r = (Rotate(90) @ Scale(2, 3)).qr_decompose()
            >>> q == Rotate(90).to_matrix()
            True
            >>> r == Scale(2, 3).to_matrix()
            True

        """
        if self.is_singular():
            raise errors.SvgSingularMatrixError(self)

        a, b, c, d = self.a, self.b, self.c, self.d

        # Gram-Schmidt on the columns; the first column fixes the rotation
        r11 = math.hypot(a, b)
        q1x, q1y = a / r11, b / r11

        # the second basis vector is the first one turned a quarter turn, so
        # that `q` is always a rotation and the reflection (if any) ends up in
        # the sign of `r22`
        q2x = mathutils.normalize_zero(-q1y)
        q2y = q1x

        r12 = q1x * c + q1y * d
        r22 = self.determinant() / r11

        q = Matrix(a=q1x, b=q1y, c=q2x, d=q2y, e=0, f=0)
        r = Matrix(a=r11, b=0, c=r12, d=r22, e=0, f=0)

        return q, r

    def svd_decompose(self) -> tuple[float, float, float]:
        """Split the linear part of the matrix into rotated axis scalings.

        The linear part is factored as `rotate(angle) @ scale(sx, sy) @ v`,
        where `v` is a rotation that is not reported because it only
        reparametrizes the unit circle: the image of the unit circle under
        this matrix is the ellipse with semi-axes `abs(sx)` and `abs(sy)`,
        the first of which points `angle` degrees away from the x-axis.

        This is the singular value decomposition, with the sign of the
        smaller singular value kept so that a reflection is not lost.

        Returns:
            A 3-tuple `(angle, sx, sy)`. `sx` is always non-negative and is
            the larger of the two; `sy` is negative exactly when the
            transformation reflects.

        Examples:
            >>> Scale(2, 3).to_matrix().svd_decompose()
            (90.0, 3.0, 2.0)
            >>> Scale(2).to_matrix().svd_decompose()
            (0.0, 2.0, 2.0)

        """
        a, b, c, d = self.a, self.b, self.c, self.d

        e = (a + d) / 2
        f = (a - d) / 2
        g = (b + c) / 2
        h = (b - c) / 2

        q = math.hypot(e, h)
        r = math.hypot(f, g)

        angle = (math.atan2(h, e) + math.atan2(g, f)) / 2

        return mathutils.degrees(angle), q + r, q - r

    def condition_number(self) -> float:
        """Measure how much the matrix distorts the plane.

        The condition number is the ratio between the longest and the
        shortest semi-axis of the ellipse the unit circle is mapped onto. It
        is 1 for a similarity and grows without bound as the matrix
        approaches a singular one, where the plane collapses onto a line.

        It also bounds how much precision is lost by undoing the matrix: a
        transformation with a large condition number cannot be split into
        factors accurately.

        Returns:
            The condition number, or infinity if the matrix is singular.

        Examples:
            >>> Rotate(30).to_matrix().condition_number()
            1.0
            >>> Scale(2, 4).to_matrix().condition_number()
            2.0
            >>> Scale(0).to_matrix().condition_number()
            inf

        """
        _, sx, sy = self.svd_decompose()

        if mathutils.is_close(sy, 0):
            return math.inf

        return abs(sx / sy)

    def rotation_angle(self) -> float:
        """Compute the angle, in degrees, of the rotation part of the matrix.

        Examples:
            >>> (Rotate(30) @ Scale(2)).rotation_angle()
            30.0
            >>> Translate(10, 20).to_matrix().rotation_angle()
            0.0

        """
        return mathutils.degrees(math.atan2(self.b, self.a))

    def __qr_decompose(self) -> Transform:
        result: Transform = []
        a, b, c, d, e, f = self.to_tuple()

        # we prefer to use r over s if possible
        if not mathutils.is_close(a, 0) or not mathutils.is_close(b, 0):
            result.append(Translate(e, f))

            r = math.hypot(a, b)
            # `atan2` is the closed form of the paper's sign(b) * arccos(a/r),
            # without the singularity at b == 0
            angle = mathutils.degrees(math.atan2(b, a))
            result.append(Rotate(angle))

            det = self.determinant()
            result.append(Scale(r, det / r))

            col_dot = _dot_product((a, b), (c, d))
            angle = mathutils.arctan(col_dot / r**2)
            result.append(SkewX(angle))

        # if r is unsuitable, we use s
        elif not mathutils.is_close(c, 0) or not mathutils.is_close(d, 0):
            result.append(Translate(e, f))

            s = math.hypot(c, d)
            angle = mathutils.degrees(math.atan2(-c, d))
            result.append(Rotate(angle))

            det = self.determinant()
            result.append(Scale(det / s, s))

            col_dot = _dot_product((a, b), (c, d))
            angle = mathutils.arctan(col_dot / s**2)
            result.append(SkewY(angle))

        # degenerate transformation; the translation must still be preserved
        else:
            result.append(Translate(e, f))
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
            result.append(SkewX(mathutils.arctan(d / b)))
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
