"""Definition of the SVG `<transform-list>` type and transformation functions.

Use `Transform` to represent transform lists in SVG.
Use `TransformType` in Pydantic fields.

Use `Translate`, `Scale`, `Rotate`, `SkewX`, `SkewY`, and `Matrix` to represent
transformations. Use `TransformFunction` to represent any transformation.
"""

from __future__ import annotations

import abc
import functools
import math
import operator
from collections.abc import Generator, Iterable
from types import NotImplementedType

import lark
import numpy as np
import numpy.typing as npt
from typing_extensions import (
    Annotated,
    Self,
    TypeAlias,
    cast,
    final,
    overload,
    override,
)

from svglab import errors, mixins, models, protocols, serialize, utiltypes
from svglab.attrparse import parse
from svglab.utils import mathutils, miscutils


_Vector: TypeAlias = tuple[float, float]
"""A 2D vector."""


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

        # an affine matrix has a constant bottom row, so the product is
        # twelve multiplications; going through numpy for a 3x3 costs more in
        # building the arrays than the arithmetic saves
        a1, b1, c1, d1, e1, f1 = self.to_matrix().to_tuple()
        a2, b2, c2, d2, e2, f2 = other.to_matrix().to_tuple()

        return Matrix(
            a=a1 * a2 + c1 * b2,
            b=b1 * a2 + d1 * b2,
            c=a1 * c2 + c1 * d2,
            d=b1 * c2 + d1 * d2,
            e=a1 * e2 + c1 * f2 + e1,
            f=b1 * e2 + d1 * f2 + f1,
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


def _argument_count(transformation: TransformFunction, /) -> int:
    """Count the numbers a transformation function serializes to.

    The serializers leave out what they can -- a translation with no vertical
    component, a scaling with one factor, a rotation about the origin -- so
    this is the length of the output, not of the tuple.

    The transformation functions are final classes, and they inherit a
    protocol, which makes `isinstance` on them go the long way round. Their
    exact type is a pointer comparison and says the same thing.
    """
    kind = type(transformation)

    if kind is Translate:
        translate = cast("Translate", transformation)
        return 1 if mathutils.is_close(translate.ty, 0) else 2

    if kind is Scale:
        scale = cast("Scale", transformation)
        return 1 if mathutils.is_close(scale.sx, scale.sy) else 2

    if kind is Rotate:
        rotate = cast("Rotate", transformation)
        return (
            1
            if mathutils.is_close(rotate.cx, 0)
            and mathutils.is_close(rotate.cy, 0)
            else 3
        )

    if kind in {SkewX, SkewY}:
        return 1

    return 6


def _transform_cost(
    transform: Iterable[TransformFunction], /
) -> tuple[int, int]:
    """Measure how much output a transformation list takes up.

    Decompositions are compared by this, smallest first: the numbers that
    have to be written out, and then the number of functions to break the
    ties. Nothing reads the shape of a decomposition any more -- it is
    composed straight back into a matrix -- so the only thing left to
    optimize for is how it reads and how much room it takes.

    Args:
        transform: The transformation list to measure.

    Returns:
        A 2-tuple of the number of arguments and the number of functions.

    Examples:
        >>> _transform_cost([Rotate(45, 10, 20)])
        (3, 1)
        >>> _transform_cost([Translate(10, 20), Rotate(45)])
        (3, 2)
        >>> _transform_cost([Matrix(1, 2, 3, 4, 5, 6)])
        (6, 1)

    """
    functions = list(transform)

    return sum(map(_argument_count, functions)), len(functions)


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
    """Drop the transformations in a list that do nothing.

    Exact types rather than `isinstance`, for the reason given in
    `_argument_count`.
    """
    result: Transform = []

    for transformation in transform:
        kind = type(transformation)

        if kind is Translate:
            translate = cast("Translate", transformation)
            if mathutils.is_close(translate.tx, 0) and mathutils.is_close(
                translate.ty, 0
            ):
                continue
        elif kind is Scale:
            scale = cast("Scale", transformation)
            if mathutils.is_close(scale.sx, 1) and mathutils.is_close(
                scale.sy, 1
            ):
                continue
        elif kind in {Rotate, SkewX, SkewY}:
            turn = cast("Rotate | SkewX | SkewY", transformation)
            if mathutils.is_close(turn.angle, 0):
                continue

        result.append(transformation)

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

        The determinant grows with the square of the entries, so it is
        judged against them rather than against zero outright: a matrix that
        merely makes everything very small is not one that collapses the
        plane. `matrix(6.9e-06 0 0 6.9e-06 0 0)` has a determinant of
        4.8e-11 and is a perfectly ordinary uniform scale.

        Returns:
            `True` if the determinant of the matrix is zero next to the size
            of the matrix itself.

        Examples:
            >>> Scale(0).to_matrix().is_singular()
            True
            >>> Scale(2).to_matrix().is_singular()
            False
            >>> Scale(6.9e-06).to_matrix().is_singular()
            False

        """
        magnitude = max(abs(self.a), abs(self.b), abs(self.c), abs(self.d))

        if magnitude == 0:
            return True

        # scale the entries down to at most one before taking the
        # determinant, rather than dividing the determinant by the square of
        # the magnitude afterwards, which underflows for extreme matrices
        a, b, c, d = (
            self.a / magnitude,
            self.b / magnitude,
            self.c / magnitude,
            self.d / magnitude,
        )

        return mathutils.is_close(a * d - b * c, 0)

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
        if self.is_singular():
            raise errors.SvgSingularMatrixError(self)

        det = self.determinant()
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

    def svd_decompose(self) -> tuple[float, float, float, float]:
        """Split the linear part of the matrix into rotated axis scalings.

        The linear part is factored as
        `rotate(angle) @ scale(sx, sy) @ rotate(pre)`. Every matrix has such a
        factorization, singular ones included, which is what makes it the one
        decomposition that never fails.

        Geometrically, the image of the unit circle under this matrix is the
        ellipse with semi-axes `abs(sx)` and `abs(sy)`, the first of which
        points `angle` degrees away from the x-axis. `pre` only says where a
        point of the circle starts out, so anything describing the ellipse
        alone -- an elliptical arc, say -- can ignore it.

        This is the singular value decomposition, with the sign of the smaller
        singular value kept so that a reflection is not lost.

        Returns:
            A 4-tuple `(angle, sx, sy, pre)`. `sx` is always non-negative and
            is the larger of the two; `sy` is negative exactly when the
            transformation reflects.

        Examples:
            >>> angle, sx, sy, pre = (
            ...     Scale(2, 3).to_matrix().svd_decompose()
            ... )
            >>> angle, sx, sy
            (90.0, 3.0, 2.0)
            >>> rebuilt = Rotate(angle) @ Scale(sx, sy) @ Rotate(pre)
            >>> rebuilt == Scale(2, 3).to_matrix()
            True

        """
        a, b, c, d = self.a, self.b, self.c, self.d

        e = (a + d) / 2
        f = (a - d) / 2
        g = (b + c) / 2
        h = (b - c) / 2

        q = math.hypot(e, h)
        r = math.hypot(f, g)

        sum_of_angles = math.atan2(h, e)
        difference = math.atan2(g, f)

        return (
            mathutils.degrees((sum_of_angles + difference) / 2),
            q + r,
            q - r,
            mathutils.degrees((sum_of_angles - difference) / 2),
        )

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
        _, sx, sy, _pre = self.svd_decompose()

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

    def __rotation_centre(self) -> _Vector | None:
        """Find the point a rotation leaves where it is, if this is one.

        A rotation about a point is a rotation about the origin surrounded by
        a pair of translations, and `rotate(a cx cy)` writes all three in one
        function. The centre is the matrix's fixed point: the `c` that solves
        `(I - R) c = v`.
        """
        a, b, _, _, e, f = self.to_tuple()
        determinant = (1 - a) ** 2 + b**2

        if mathutils.is_close(determinant, 0):
            # the rotation is by a whole turn, so every point is fixed
            return None

        return (
            ((1 - a) * e - b * f) / determinant,
            (b * e + (1 - a) * f) / determinant,
        )

    def __qr_candidate(self, prefix: Transform, /) -> Transform | None:
        """Factor as a rotation, an axis scaling and a skew along x.

        Gram-Schmidt on the columns; the shape that survives the rotation is
        upper triangular, and an upper triangular matrix is a scaling
        followed by a skew along x.
        """
        try:
            rotation, rest = self.qr_decompose()
        except errors.SvgSingularMatrixError:
            return None

        return [
            *prefix,
            Rotate(rotation.rotation_angle()),
            Scale(rest.a, rest.d),
            SkewX(mathutils.arctan(rest.c / rest.a)),
        ]

    def __ldu_candidate(self, prefix: Transform, /) -> Transform | None:
        """Factor as a skew along y, an axis scaling and a skew along x."""
        a, b, c, *_ = self.to_tuple()

        if mathutils.is_close(a, 0):
            return None

        return [
            *prefix,
            SkewY(mathutils.arctan(b / a)),
            Scale(a, self.determinant() / a),
            SkewX(mathutils.arctan(c / a)),
        ]

    def __svd_candidate(self, prefix: Transform, /) -> Transform:
        """Factor as a rotation, an axis scaling and another rotation.

        Every matrix has this factorization, singular ones included, which is
        what makes it the one that is always available.
        """
        angle, sx, sy, pre = self.svd_decompose()

        return [*prefix, Rotate(angle), Scale(sx, sy), Rotate(pre)]

    def __candidates(self) -> Generator[Transform]:
        """Propose ways of writing the matrix as elementary transformations.

        A proposal need not be correct: `decompose` composes each one back and
        keeps only those that reconstruct the matrix exactly, so a candidate
        can be offered on a hunch and rejected on the arithmetic. What the
        guards below are for is not correctness but cost -- every function
        built here is a model that has to be validated, and the guesses that
        cannot possibly hold are not worth building.

        The matrix itself is always among the candidates, so there is always
        an answer.
        """
        a, b, c, d, e, f = self.to_tuple()

        moves = not mathutils.is_close(e, 0) or not mathutils.is_close(
            f, 0
        )
        # a guess is worth making in one arrangement only: with the move if
        # there is one to make, without it if there is not
        prefix: Transform = [self.translation()] if moves else []

        yield [self]

        if mathutils.is_close(b, 0) and mathutils.is_close(c, 0):
            yield [*prefix, Scale(a, d)]

        if (
            mathutils.is_close(a, 1)
            and mathutils.is_close(d, 1)
            and mathutils.is_close(b, 0)
        ):
            yield [*prefix, SkewX(mathutils.arctan(c))]

        if (
            mathutils.is_close(a, 1)
            and mathutils.is_close(d, 1)
            and mathutils.is_close(c, 0)
        ):
            yield [*prefix, SkewY(mathutils.arctan(b))]

        if (
            mathutils.is_close(a, d)
            and mathutils.is_close(b, -c)
            and mathutils.is_close(math.hypot(a, b), 1)
        ):
            angle = self.rotation_angle()

            yield [*prefix, Rotate(angle)]

            # a rotation about a point says the same as a rotation between
            # two moves, in one function instead of three
            centre = self.__rotation_centre()

            if moves and centre is not None:
                yield [Rotate(angle, *centre)]

        for candidate in (
            self.__qr_candidate(prefix),
            self.__ldu_candidate(prefix),
            self.__svd_candidate(prefix),
        ):
            if candidate is not None:
                yield candidate

    def decompose(self) -> Transform:
        """Decompose the matrix into elementary transformations.

        The result is a list of transformations that, composed, are equal to
        the original matrix -- always, since the matrix itself is a last
        resort. Of the candidates that reconstruct it exactly, the one that
        writes out the fewest numbers wins.

        Several factorizations are tried. Three are general: QR, which is a
        rotation, an axis scaling and a skew along x; LDU, which is a skew
        along y, an axis scaling and a skew along x; and the singular value
        decomposition, which is a rotation, an axis scaling and a rotation,
        and which is the only one that survives a singular matrix. The rest
        are guesses at the matrix being something simpler -- a scaling, a
        skew, a rotation about a point -- that are kept only if they turn out
        to be right.

        The two general non-singular factorizations are those of Frédéric
        Wang's [Decomposition of 2D-transform
        matrices](https://frederic-wang.fr/2013/12/01/decomposition-of-2d-transform-matrices/).

        Returns:
            A transformation list composed of elementary transformations.

        Examples:
            >>> Translate(10, 20).to_matrix().decompose()
            [Translate(tx=10.0, ty=20.0)]
            >>> SkewY(45).to_matrix().decompose()
            [SkewY(angle=45.0)]
            >>> (Translate(10, 20) @ Scale(2, 2)).decompose()
            [Translate(tx=10.0, ty=20.0), Scale(sx=2.0, sy=2.0)]

            A rotation about a point is written as one function, not three:

            >>> m = Translate(10, 20) @ Rotate(45) @ Translate(-10, -20)
            >>> m.decompose()
            [Rotate(angle=45.0, cx=10.0, cy=20.0)]

            A singular matrix still comes apart, where it used to lose a
            column:

            >>> decomposition = Matrix(0, 0, 3, 4, 0, 0).decompose()
            >>> compose(decomposition) == Matrix(0, 0, 3, 4, 0, 0)
            True

        """
        candidates = sorted(
            map(_remove_redundant_transformations, self.__candidates()),
            key=_transform_cost,
        )

        # cheapest first, so the first one that reconstructs the matrix is
        # the cheapest one that does; composing is the expensive part, and
        # this way it usually happens once or twice
        for candidate in candidates:
            if compose(candidate) == self:
                return candidate

        raise AssertionError("the matrix itself always reconstructs")

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
