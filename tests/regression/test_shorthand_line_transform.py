import pytest
from typing_extensions import Final

from svglab import (
    Length,
    Matrix,
    Path,
    PathData,
    Rotate,
    Scale,
    SkewX,
    SkewY,
    Svg,
    TransformFunction,
    Translate,
)
from tests.conftest import assert_svg_visually_equal


_D: Final = "M 60,60 H 140 V 140 H 60 Z"


def _svg(path: Path) -> Svg:
    # the viewBox is centered on the origin so that rotated and skewed
    # paths stay inside the viewport
    return Svg(
        width=Length(400),
        height=Length(400),
        viewBox=(-200, -200, 400, 400),
    ).add_child(path)


@pytest.mark.parametrize(
    "transformation",
    [
        Rotate(45),
        Rotate(90),
        SkewX(20),
        SkewY(-20),
        Matrix(1, 0.3, -0.3, 1, 5, -5),
        Translate(10, 20),
        Scale(0.5, 1.5),
    ],
)
def test_transformed_shorthand_lines_are_visually_equal(
    transformation: TransformFunction,
) -> None:
    original = _svg(
        Path(d=PathData.from_str(_D), transform=[transformation])
    )
    transformed = _svg(Path(d=transformation @ PathData.from_str(_D)))

    assert_svg_visually_equal(original, transformed)
