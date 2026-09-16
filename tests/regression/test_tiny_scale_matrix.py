"""A matrix that makes everything small is not a matrix that flattens it."""

import pytest

import svglab
from svglab.attrparse import transform


# an Inkscape drawing in the freesvg corpus carries this on a group: the
# document is authored in millions of units and scaled back down to fit
_TINY = transform.Matrix(
    6.9177836e-06, 0.0, 0.0, 6.9177836e-06, 434.119595, 268.24060115
)


def test_a_uniform_scale_is_never_singular_however_small() -> None:
    # the determinant grows with the square of the entries, so judging it
    # against zero outright calls an ordinary scale degenerate: this one has
    # a determinant of 4.8e-11 and a condition number of exactly 1
    assert not _TINY.is_singular()
    assert _TINY.condition_number() == pytest.approx(1.0)


@pytest.mark.parametrize(
    "matrix",
    [
        transform.Matrix(0, 0, 0, 0, 0, 0),
        transform.Matrix(1, 0, 0, 0, 0, 0),
        transform.Matrix(0, 0, 0, 2.0440994942599483e-196, 0, 0),
        transform.Scale(1, 0).to_matrix(),
    ],
    ids=["zero", "flat", "subnormal", "collapsed"],
)
def test_a_matrix_that_really_collapses_is_still_singular(
    matrix: transform.Matrix,
) -> None:
    assert matrix.is_singular()


def test_reifying_a_tiny_scale_does_not_raise() -> None:
    svg = svglab.parse_svg(
        '<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100">'
        '<g transform="matrix(6.9177836e-06 0 0 6.9177836e-06 434.1 268.2)">'
        '<path d="M0,0 L1000000,1000000 Z" fill="red"/>'
        "</g></svg>"
    )

    svg.reify()

    assert svg.find(svglab.G).transform is None
    assert svg.find(svglab.Path).d is not None
