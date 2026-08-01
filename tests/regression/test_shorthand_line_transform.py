import pytest
from typing_extensions import Final

import svglab
from svglab.attrparse import path_data
from tests import conftest


_D: Final = "M 60,60 H 140 V 140 H 60 Z"


def _svg(path: svglab.Path) -> svglab.Svg:
    # the viewBox is centered on the origin so that rotated and skewed
    # paths stay inside the viewport
    return svglab.Svg(
        width=svglab.Length(400),
        height=svglab.Length(400),
        viewBox=(-200, -200, 400, 400),
    ).add_child(path)


@pytest.mark.parametrize(
    "transformation",
    [
        svglab.Rotate(45),
        svglab.Rotate(90),
        svglab.SkewX(20),
        svglab.SkewY(-20),
        svglab.Matrix(1, 0.3, -0.3, 1, 5, -5),
        svglab.Translate(10, 20),
        svglab.Scale(0.5, 1.5),
    ],
)
def test_transformed_shorthand_lines_are_visually_equal(
    transformation: svglab.TransformFunction,
) -> None:
    original = _svg(
        svglab.Path(
            d=path_data.PathData.from_str(_D), transform=[transformation]
        )
    )
    transformed = _svg(
        svglab.Path(d=transformation @ path_data.PathData.from_str(_D))
    )

    conftest.assert_svg_visually_equal(original, transformed)
