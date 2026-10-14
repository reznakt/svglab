"""A gradient's coordinates default to percentages, which can be spelled out.

In bounding box units a percentage is a fraction of the box the gradient is
painted onto, so it is a plain number waiting to be written. In user space it
is a fraction of the nearest viewport, which is known when that viewport has
a `viewBox` or a size in user units.
"""

import copy

import pytest

from svglab import Length, LinearGradient, RadialGradient, parse_svg
from tests.conftest import assert_svg_visually_equal, transforms_left


@pytest.mark.parametrize(
    "gradient",
    [
        '<linearGradient id="g" gradientTransform="rotate(30)">',
        '<linearGradient id="g" x1="20%" gradientTransform="rotate(30)">',
        '<radialGradient id="g" gradientTransform="rotate(30 0.5 0.5)">',
        (
            '<radialGradient id="g" fx="30%" '
            'gradientTransform="translate(0.1 0.2) scale(0.8)">'
        ),
    ],
    ids=["linear", "linear-percent", "radial", "radial-focus"],
)
def test_a_bounding_box_gradient_with_default_coordinates_is_reified(
    gradient: str,
) -> None:
    original = parse_svg(f"""
        <svg width="200" height="200">
            {gradient}
                <stop offset="0" stop-color="white"/>
                <stop offset="1" stop-color="black"/>
            </{gradient[1:].split(maxsplit=1)[0]}>
            <rect x="20" y="20" width="160" height="160" fill="url(#g)"/>
        </svg>
    """)
    reified = copy.deepcopy(original)

    reified.reify()

    assert not transforms_left(reified)
    assert_svg_visually_equal(original, reified, tolerance=1e-5)


def test_a_user_space_gradient_resolves_percentages_against_the_viewbox() -> (
    None
):
    original = parse_svg("""
        <svg width="200" height="200" viewBox="0 0 400 300">
            <linearGradient id="g" gradientUnits="userSpaceOnUse"
                            x1="10%" x2="60%"
                            gradientTransform="translate(40)">
                <stop offset="0" stop-color="white"/>
                <stop offset="1" stop-color="black"/>
            </linearGradient>
            <rect width="400" height="300" fill="url(#g)"/>
        </svg>
    """)
    reified = copy.deepcopy(original)

    reified.reify()

    gradient = reified.find(LinearGradient)

    assert not transforms_left(reified)
    assert gradient.x1 == Length(80)
    assert gradient.x2 == Length(280)
    assert_svg_visually_equal(original, reified)


def test_a_user_space_gradient_in_an_unknown_viewport_is_left_alone() -> (
    None
):
    original = parse_svg("""
        <svg width="200" height="200">
            <svg width="50%" height="50%">
                <radialGradient id="g" gradientUnits="userSpaceOnUse"
                                gradientTransform="translate(10)">
                    <stop offset="0" stop-color="white"/>
                    <stop offset="1" stop-color="black"/>
                </radialGradient>
                <rect width="100" height="100" fill="url(#g)"/>
            </svg>
        </svg>
    """)
    reified = copy.deepcopy(original)

    reified.reify()

    assert transforms_left(reified) == [reified.find(RadialGradient)]
    assert reified.find(RadialGradient).cx is None
    assert_svg_visually_equal(original, reified)


def test_a_gradient_without_a_transformation_is_not_touched() -> None:
    original = parse_svg("""
        <svg width="200" height="200">
            <linearGradient id="g" x1="20%">
                <stop offset="0" stop-color="white"/>
                <stop offset="1" stop-color="black"/>
            </linearGradient>
            <rect width="200" height="200" fill="url(#g)"/>
        </svg>
    """)
    reified = copy.deepcopy(original)

    reified.reify()

    assert reified.to_xml() == original.to_xml()
