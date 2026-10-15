"""`set_viewbox` refuses what would resolve against the new viewBox.

A length given as a percentage of the viewport keeps its percentage while
the viewport it refers to changes underneath it. The coordinates of a
user-space gradient default to such percentages, but those can be written
out against the old viewport first.
"""

import pytest

from svglab import LinearGradient, Svg, parse_svg
from svglab.errors import SvgUnitConversionError
from tests.conftest import assert_svg_visually_equal


def _parse(content: str) -> Svg:
    return parse_svg(
        '<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100" '
        f'viewBox="0 0 100 100">{content}</svg>'
    )


@pytest.mark.parametrize(
    "content",
    [
        '<rect width="50%" height="50%"/>',
        '<rect width="50" height="50" stroke="black" stroke-width="2%"/>',
        '<svg width="100%" height="50"><rect width="10" height="10"/></svg>',
    ],
    ids=["rect", "stroke-width", "nested-svg"],
)
def test_a_percentage_of_the_viewport_is_refused(content: str) -> None:
    svg = _parse(content)

    with pytest.raises(SvgUnitConversionError):
        svg.set_viewbox((0, 0, 200, 200))


def test_a_percentage_of_something_else_is_fine() -> None:
    original = _parse(
        '<text x="10" y="50" font-size="150%">Reify</text>'
        '<linearGradient id="g"><stop offset="50%" stop-color="red"/>'
        '<stop offset="100%" stop-color="blue"/></linearGradient>'
        '<rect x="20" y="60" width="50" height="30" fill="url(#g)"/>'
    )
    changed = _parse(
        '<text x="10" y="50" font-size="150%">Reify</text>'
        '<linearGradient id="g"><stop offset="50%" stop-color="red"/>'
        '<stop offset="100%" stop-color="blue"/></linearGradient>'
        '<rect x="20" y="60" width="50" height="30" fill="url(#g)"/>'
    )

    changed.set_viewbox((0, 0, 200, 200))

    assert_svg_visually_equal(original, changed)


def test_a_user_space_gradient_is_written_out_against_the_old_viewport() -> (
    None
):
    content = (
        '<linearGradient id="g" gradientUnits="userSpaceOnUse">'
        '<stop offset="0" stop-color="red"/>'
        '<stop offset="1" stop-color="blue"/></linearGradient>'
        '<rect x="10" y="10" width="80" height="80" fill="url(#g)"/>'
    )
    original = _parse(content)
    changed = _parse(content)

    changed.set_viewbox((0, 0, 200, 200))

    gradient = changed.find(LinearGradient)

    assert gradient.x2 is not None
    assert_svg_visually_equal(original, changed)


def test_a_user_space_gradient_among_nested_viewports_is_refused() -> None:
    svg = _parse(
        '<linearGradient id="g" gradientUnits="userSpaceOnUse">'
        '<stop offset="0" stop-color="red"/>'
        '<stop offset="1" stop-color="blue"/></linearGradient>'
        '<svg x="10" y="10" width="50" height="50">'
        '<rect width="50" height="50" fill="url(#g)"/></svg>'
    )

    with pytest.raises(SvgUnitConversionError):
        svg.set_viewbox((0, 0, 200, 200))
