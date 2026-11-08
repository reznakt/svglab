"""A linear gradient survives any affine transformation.

Its stops lie on parallel lines, and an affine map takes parallel lines to
parallel lines, so the gradient can always be redrawn with a vector
perpendicular to the mapped lines. A radial gradient cannot: a stretch turns
its circles into ellipses, which no radius can express.
"""

import copy

import pytest

from svglab import LinearGradient, RadialGradient, parse_svg
from tests.conftest import assert_svg_visually_equal, transforms_left


@pytest.mark.parametrize(
    "gradient_transform",
    ["skewX(30)", "scale(2 0.5)", "matrix(1.2 0.3 -0.6 0.8 10 5)"],
)
@pytest.mark.parametrize("units", ["userSpaceOnUse", "objectBoundingBox"])
def test_a_linear_gradient_absorbs_a_skew_or_stretch(
    gradient_transform: str, units: str
) -> None:
    coords = (
        'x1="30" y1="40" x2="150" y2="120"'
        if units == "userSpaceOnUse"
        else 'x1="0.1" y1="0.2" x2="0.8" y2="0.6"'
    )
    original = parse_svg(f"""
        <svg width="200" height="200">
            <linearGradient id="g" gradientUnits="{units}" {coords}
                            gradientTransform="{gradient_transform}">
                <stop offset="0" stop-color="gold"/>
                <stop offset="0.5" stop-color="crimson"/>
                <stop offset="1" stop-color="navy"/>
            </linearGradient>
            <rect x="20" y="20" width="160" height="160" fill="url(#g)"/>
        </svg>
    """)
    reified = copy.deepcopy(original)

    reified.reify()

    assert not transforms_left(reified)
    assert reified.find(LinearGradient).gradientTransform is None
    assert_svg_visually_equal(original, reified, tolerance=1e-4)


def test_a_radial_gradient_keeps_a_stretch() -> None:
    original = parse_svg("""
        <svg width="200" height="200">
            <radialGradient id="g" gradientUnits="userSpaceOnUse"
                            cx="100" cy="100" r="60"
                            gradientTransform="translate(10 0) scale(2 1)">
                <stop offset="0" stop-color="gold"/>
                <stop offset="1" stop-color="navy"/>
            </radialGradient>
            <rect x="20" y="20" width="160" height="160" fill="url(#g)"/>
        </svg>
    """)
    reified = copy.deepcopy(original)

    reified.reify()

    gradient = reified.find(RadialGradient)

    # the move went through, the stretch stayed
    assert transforms_left(reified) == [gradient]
    assert gradient.cx != original.find(RadialGradient).cx
    assert_svg_visually_equal(original, reified, tolerance=1e-5)
