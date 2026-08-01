import pytest
from typing_extensions import Final

import svglab
from svglab.attrparse import path_data
from tests import conftest


_D: Final = "M 40,100 A 40 20 30 1 0 160,100"


def _svg(path: svglab.Path) -> svglab.Svg:
    return svglab.Svg(
        width=svglab.Length(200), height=svglab.Length(200)
    ).add_child(path)


@pytest.mark.parametrize(
    "transformation",
    [
        svglab.Rotate(10),
        svglab.Rotate(-10),
        svglab.Rotate(30, 100, 100),
        svglab.Rotate(90, 100, 100),
        svglab.Rotate(-45, 100, 100),
    ],
)
def test_transformed_arc_is_visually_equal(
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
