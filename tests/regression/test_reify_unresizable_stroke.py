"""A stroke reification cannot resize holds its element to a move."""

import pytest

import svglab
from tests import conftest


def _parse(content: str) -> svglab.Svg:
    return svglab.parse_svg(
        '<svg xmlns="http://www.w3.org/2000/svg" width="200" height="200">'
        f"{content}</svg>"
    )


@pytest.mark.parametrize(
    "group",
    [
        '<g stroke="black" stroke-width="5%">',
        '<g stroke="black" stroke-dasharray="5% 2%">',
    ],
)
def test_an_inherited_stroke_it_cannot_resize_leaves_only_a_move(
    group: str,
) -> None:
    content = (
        f'{group}<path d="M10,10 L40,30" fill="none" '
        'transform="scale(2)"/></g>'
    )
    original = _parse(content)
    reified = _parse(content)

    reified.reify()

    assert reified.find(svglab.Path).transform == [svglab.Scale(2)]
    conftest.assert_svg_visually_equal(original, reified)
