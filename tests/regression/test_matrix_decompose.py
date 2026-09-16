import re

import hypothesis
import hypothesis.strategies as st
import pytest
from typing_extensions import Final

import svglab


@pytest.mark.parametrize(
    "matrix",
    [
        # 180 degree rotation (b == 0 and a < 0)
        svglab.Matrix(-1, 0, 0, -1, 0, 0),
        svglab.Matrix(-1, 0, 0, -1, 10, 20),
        # 180 degree rotation combined with a scale
        svglab.Matrix(-2, 0, 0, -2, 0, 0),
        # horizontal flip (b == 0 and a < 0, d > 0)
        svglab.Matrix(-1, 0, 0, 1, 0, 0),
        # a == 0 and b == 0, so the angle comes from c and d instead;
        # d == 0 is what broke the old formula
        svglab.Matrix(0, 0, 3, 4, 5, 6),
        svglab.Matrix(0, 0, 2, 0, 0, 0),
        svglab.Matrix(0, 0, -2, 0, 0, 0),
        # a == 0 and d != 0, which is handled by the LDU decomposition
        svglab.Matrix(0, 1, -1, 1, 0, 0),
        svglab.Matrix(0, 2, 3, 4, 5, 6),
        svglab.Matrix(0, 1.65, -2.65, -0.86, -0.23, 0.39),
        # degenerate linear part; the translation must still be preserved
        svglab.Matrix(0, 0, 0, 0, 10, 20),
        svglab.Matrix(0, 0, 0, 0, -3, 7),
        svglab.Matrix(0, 0, 0, 0, 0, 0),
        # transformations that were already decomposed correctly
        svglab.Matrix(1, 0, 0, 1, 10, 20),
        svglab.Matrix(0, 1, -1, 0, 0, 0),
        svglab.Matrix(2, 0, 0, 3, 0, 0),
        svglab.Matrix(1, 2, 3, 4, 5, 6),
        # a zero first column makes the matrix singular, and the
        # decomposition used to drop the second column with it
        svglab.Matrix(0, 0, 1, 1e12, 3, 5),
        svglab.Matrix(0, 0, 1e12, 1, 3, 5),
        svglab.Matrix(0, 0, -3, 1e7, 3, 5),
        svglab.Matrix(0, 0, 1e-7, 1e7, 3, 5),
        # wildly different magnitudes along the two axes
        svglab.Matrix(1e8, 0, 0, 1e-8, 0, 0),
        svglab.Matrix(1e-9, 1, 1, 1e-9, 0, 0),
    ],
)
def test_decompose_roundtrip(matrix: svglab.Matrix) -> None:
    assert svglab.compose(matrix.decompose()) == matrix


_NUMBERS: Final = st.floats(
    min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False
)
_DEGENERATE: Final = st.sampled_from(
    [0.0, 1.0, -1.0, 1e-9, 1e9, 0.5, -3.0]
)
_MATRICES: Final = st.builds(
    svglab.Matrix, *[st.one_of(_NUMBERS, _DEGENERATE)] * 6
)


@hypothesis.given(_MATRICES)
def test_every_matrix_comes_apart_exactly(matrix: svglab.Matrix) -> None:
    # unlike most of the properties around transformations, this one holds
    # for singular matrices too: the matrix itself is the last resort, so
    # there is always an exact answer
    assert svglab.compose(matrix.decompose()) == matrix


def _arguments(transformation: svglab.TransformFunction) -> int:
    """Count the numbers a transformation function writes out.

    Read off the serialization rather than the fields, because the
    serializers leave out what they can -- a translation with no vertical
    component, a scaling with one factor, a rotation about the origin.
    """
    arguments = transformation.serialize().partition("(")[2].rstrip(")")

    return len(re.findall(r"[-+0-9.eE]+", arguments))


@hypothesis.given(_MATRICES)
def test_decompose_never_writes_more_than_the_matrix(
    matrix: svglab.Matrix,
) -> None:
    # `matrix(a b c d e f)` is always available at six numbers in one
    # function, so a decomposition that took more room than that would be a
    # worse answer than leaving the matrix alone
    decomposition = matrix.decompose()
    arguments = sum(map(_arguments, decomposition))

    assert (arguments, len(decomposition)) <= (6, 1)


@pytest.mark.parametrize(
    ("transform", "expected"),
    [
        ([svglab.Translate(10, 20)], [svglab.Translate(10, 20)]),
        ([svglab.Scale(2, 3)], [svglab.Scale(2, 3)]),
        ([svglab.Rotate(45)], [svglab.Rotate(45)]),
        ([svglab.SkewX(30)], [svglab.SkewX(30)]),
        ([svglab.SkewY(30)], [svglab.SkewY(30)]),
        (
            [svglab.Translate(10, 20), svglab.Scale(2)],
            [svglab.Translate(10, 20), svglab.Scale(2)],
        ),
        # a rotation about a point is three functions written as one
        (
            [
                svglab.Translate(10, 20),
                svglab.Rotate(45),
                svglab.Translate(-10, -20),
            ],
            [svglab.Rotate(45, 10, 20)],
        ),
        ([svglab.Scale(1), svglab.Translate(0)], []),
    ],
)
def test_decompose_finds_the_shortest_form(
    transform: svglab.Transform, expected: svglab.Transform
) -> None:
    assert svglab.compose(transform).decompose() == expected
