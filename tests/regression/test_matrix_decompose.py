import pytest

from svglab import Matrix, compose


@pytest.mark.parametrize(
    "matrix",
    [
        # 180 degree rotation (b == 0 and a < 0)
        Matrix(-1, 0, 0, -1, 0, 0),
        Matrix(-1, 0, 0, -1, 10, 20),
        # 180 degree rotation combined with a scale
        Matrix(-2, 0, 0, -2, 0, 0),
        # horizontal flip (b == 0 and a < 0, d > 0)
        Matrix(-1, 0, 0, 1, 0, 0),
        # a == 0 and b == 0, so the angle comes from c and d instead;
        # d == 0 is what broke the old formula
        Matrix(0, 0, 3, 4, 5, 6),
        Matrix(0, 0, 2, 0, 0, 0),
        Matrix(0, 0, -2, 0, 0, 0),
        # a == 0 and d != 0, which is handled by the LDU decomposition
        Matrix(0, 1, -1, 1, 0, 0),
        Matrix(0, 2, 3, 4, 5, 6),
        Matrix(0, 1.65, -2.65, -0.86, -0.23, 0.39),
        # degenerate linear part; the translation must still be preserved
        Matrix(0, 0, 0, 0, 10, 20),
        Matrix(0, 0, 0, 0, -3, 7),
        Matrix(0, 0, 0, 0, 0, 0),
        # transformations that were already decomposed correctly
        Matrix(1, 0, 0, 1, 10, 20),
        Matrix(0, 1, -1, 0, 0, 0),
        Matrix(2, 0, 0, 3, 0, 0),
        Matrix(1, 2, 3, 4, 5, 6),
    ],
)
def test_decompose_roundtrip(matrix: Matrix) -> None:
    assert compose(matrix.decompose()) == matrix
