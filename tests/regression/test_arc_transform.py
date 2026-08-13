import pytest
from typing_extensions import Final

import svglab
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
            d=svglab.PathData.from_str(_D), transform=[transformation]
        )
    )
    transformed = _svg(
        svglab.Path(d=transformation @ svglab.PathData.from_str(_D))
    )

    conftest.assert_svg_visually_equal(original, transformed)


def test_tilted_arc_rejects_a_non_uniform_scale() -> None:
    with pytest.raises(NotImplementedError, match="tilted arc"):
        _ = svglab.Scale(2, 3) @ svglab.PathData.from_str(_D)


@pytest.mark.parametrize("arc_angle", [0, 90, 180, 270])
def test_axis_aligned_arc_accepts_a_non_uniform_scale(
    arc_angle: int,
) -> None:
    d = f"M 40,100 A 40 20 {arc_angle} 1 0 160,100"
    transformation = svglab.Scale(0.5, 0.3)

    original = _svg(
        svglab.Path(
            d=svglab.PathData.from_str(d), transform=[transformation]
        )
    )
    transformed = _svg(
        svglab.Path(d=transformation @ svglab.PathData.from_str(d))
    )

    conftest.assert_svg_visually_equal(original, transformed)
