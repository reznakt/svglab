import pytest

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
    ],
)
def test_decompose_roundtrip(matrix: svglab.Matrix) -> None:
    assert svglab.compose(matrix.decompose()) == matrix
