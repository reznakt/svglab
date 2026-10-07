import copy

import pytest

from svglab import Color, G, Length, Rect, Scale, Svg, Transform, Translate
from tests.conftest import assert_svg_visually_equal


def _svg(transform: Transform, *, group: bool) -> Svg:
    rect = Rect(
        x=Length(10),
        y=Length(10),
        width=Length(30),
        height=Length(20),
        fill=Color("blue"),
    )

    child = rect

    if group:
        child = G().add_child(rect)

    child.transform = transform

    return Svg(width=Length(200), height=Length(200)).add_child(child)


@pytest.mark.parametrize("group", [False, True])
@pytest.mark.parametrize(
    "transform",
    [
        [Scale(2, 3)],
        [Translate(10, 20), Scale(2, 3)],
        [Scale(2, 3), Translate(10, 20)],
    ],
)
def test_non_uniform_scale_is_not_dropped(
    transform: Transform, *, group: bool
) -> None:
    original = _svg(transform, group=group)
    reified = copy.deepcopy(original)

    reified.reify()

    assert reified.find(G, Rect).transform
    assert_svg_visually_equal(original, reified)
