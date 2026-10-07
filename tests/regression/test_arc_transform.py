import pytest
from typing_extensions import Final

from svglab import (
    Length,
    Path,
    PathData,
    Rotate,
    Scale,
    Svg,
    TransformFunction,
)
from tests.conftest import assert_svg_visually_equal


_D: Final = "M 40,100 A 40 20 30 1 0 160,100"


def _svg(path: Path) -> Svg:
    # the viewBox is centered on the origin so that mirrored and rotated
    # arcs stay inside the viewport
    return Svg(
        width=Length(400),
        height=Length(400),
        viewBox=(-200, -200, 400, 400),
    ).add_child(path)


@pytest.mark.parametrize(
    "transformation",
    [
        Rotate(10),
        Rotate(-10),
        Rotate(30, 100, 100),
        Rotate(90, 100, 100),
        Rotate(-45, 100, 100),
        Scale(-1, 1),
        Scale(1, -1),
        Scale(-1, -1),
        Scale(-0.5),
        Scale(0.5),
    ],
)
def test_transformed_arc_is_visually_equal(
    transformation: TransformFunction,
) -> None:
    original = _svg(
        Path(d=PathData.from_str(_D), transform=[transformation])
    )
    transformed = _svg(Path(d=transformation @ PathData.from_str(_D)))

    assert_svg_visually_equal(original, transformed)


def test_tilted_arc_rejects_a_non_uniform_scale() -> None:
    with pytest.raises(NotImplementedError, match="tilted arc"):
        _ = Scale(2, 3) @ PathData.from_str(_D)


@pytest.mark.parametrize("arc_angle", [0, 90, 180, 270])
def test_axis_aligned_arc_accepts_a_non_uniform_scale(
    arc_angle: int,
) -> None:
    d = f"M 40,100 A 40 20 {arc_angle} 1 0 160,100"
    transformation = Scale(0.5, 0.3)

    original = _svg(
        Path(d=PathData.from_str(d), transform=[transformation])
    )
    transformed = _svg(Path(d=transformation @ PathData.from_str(d)))

    assert_svg_visually_equal(original, transformed)


@pytest.mark.parametrize(
    "transformation",
    [Scale(-0.5, 0.3), Scale(0.5, -0.3), Scale(-0.5, -0.3)],
)
def test_mirrored_axis_aligned_arc_is_visually_equal(
    transformation: TransformFunction,
) -> None:
    d = "M 40,100 A 40 20 0 1 0 160,100"

    original = _svg(
        Path(d=PathData.from_str(d), transform=[transformation])
    )
    transformed = _svg(Path(d=transformation @ PathData.from_str(d)))

    assert_svg_visually_equal(original, transformed)
