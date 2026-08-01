import copy

import pytest

import svglab
from tests import conftest


def _svg(transform: svglab.Transform, *, group: bool) -> svglab.Svg:
    rect = svglab.Rect(
        x=svglab.Length(10),
        y=svglab.Length(10),
        width=svglab.Length(30),
        height=svglab.Length(20),
        fill=svglab.Color("blue"),
    )

    child: svglab.Element = rect

    if group:
        child = svglab.G().add_child(rect)

    child.transform = transform

    return svglab.Svg(
        width=svglab.Length(200), height=svglab.Length(200)
    ).add_child(child)


@pytest.mark.parametrize("group", [False, True])
@pytest.mark.parametrize(
    "transform",
    [
        [svglab.Scale(2, 3)],
        [svglab.Translate(10, 20), svglab.Scale(2, 3)],
        [svglab.Scale(2, 3), svglab.Translate(10, 20)],
    ],
)
def test_non_uniform_scale_is_not_dropped(
    transform: svglab.Transform, *, group: bool
) -> None:
    original = _svg(transform, group=group)
    reified = copy.deepcopy(original)

    reified.reify()

    assert reified.find(svglab.G, svglab.Rect).transform
    conftest.assert_svg_visually_equal(original, reified)
