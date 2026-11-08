"""A paint server reaches a shape through inheritance as well as directly.

`fill` and `stroke` are inherited, so a gradient or pattern named on a group
paints every shape below it. One in user space pins those shapes where they
are just as it would if they named it themselves, whether it is named in an
attribute or in a `style` declaration.
"""

import copy

import pytest

from svglab import G, Rect, parse_svg
from tests.conftest import assert_svg_visually_equal, transforms_left


@pytest.mark.parametrize(
    "paint",
    ['fill="url(#g)"', 'style="fill: url(#g)"', 'stroke="url(#g)"'],
    ids=["attribute", "style", "stroke"],
)
def test_a_user_space_gradient_inherited_from_a_group_pins_the_shape(
    paint: str,
) -> None:
    original = parse_svg(f"""
        <svg width="200" height="200">
            <linearGradient id="g" gradientUnits="userSpaceOnUse"
                            x1="0" x2="100">
                <stop offset="0" stop-color="red"/>
                <stop offset="1" stop-color="blue"/>
            </linearGradient>
            <g {paint} stroke-width="20">
                <rect width="100" height="100" transform="translate(50 50)"/>
            </g>
        </svg>
    """)
    reified = copy.deepcopy(original)

    reified.reify()

    assert transforms_left(reified) == [reified.find(Rect)]
    assert_svg_visually_equal(original, reified)


def test_a_bounding_box_gradient_inherited_from_a_group_moves_along() -> (
    None
):
    original = parse_svg("""
        <svg width="200" height="200">
            <linearGradient id="g">
                <stop offset="0" stop-color="red"/>
                <stop offset="1" stop-color="blue"/>
            </linearGradient>
            <g fill="url(#g)">
                <rect width="100" height="100"
                      transform="translate(50 50) scale(0.5 1)"/>
            </g>
        </svg>
    """)
    reified = copy.deepcopy(original)

    reified.reify()

    assert not transforms_left(reified)
    assert_svg_visually_equal(original, reified)


def test_a_group_painted_in_user_space_still_hands_down_what_it_can() -> (
    None
):
    # the group's own transformation reaches its children only, each of
    # which is pinned by the paint, so it stays on the group
    original = parse_svg("""
        <svg width="200" height="200">
            <linearGradient id="g" gradientUnits="userSpaceOnUse"
                            x1="0" x2="100">
                <stop offset="0" stop-color="red"/>
                <stop offset="1" stop-color="blue"/>
            </linearGradient>
            <g fill="url(#g)" transform="translate(50 50)">
                <rect width="100" height="100"/>
            </g>
        </svg>
    """)
    reified = copy.deepcopy(original)

    reified.reify()

    assert transforms_left(reified) == [reified.find(G)]
    assert_svg_visually_equal(original, reified)
