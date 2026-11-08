"""A paint may name a fallback after its reference.

`fill="url(#g) red"` paints with the gradient, or with red where the gradient
cannot be found. The fallback used to make the reference unparsable, or to be
swallowed into its fragment when it held parentheses, which left reification
unaware that a shape is painted in user space.
"""

import copy

import pytest

from svglab import FuncIri, Rect, parse_svg
from tests.conftest import assert_svg_visually_equal, transforms_left


@pytest.mark.parametrize(
    "fallback", ["red", "rgb(0, 0, 0)", "none", "currentColor"]
)
def test_a_fallback_is_kept_beside_the_reference(fallback: str) -> None:
    svg = parse_svg(
        '<svg xmlns="http://www.w3.org/2000/svg">'
        f'<rect fill="url(#g) {fallback}"/></svg>'
    )
    rect = svg.find(Rect)

    assert isinstance(rect.fill, FuncIri)
    assert rect.fill == FuncIri(fragment="g", fallback=fallback)
    assert rect.fill.is_local
    assert rect.to_xml() == f'<rect fill="url(#g) {fallback}"/>'


@pytest.mark.parametrize("where", ["attribute", "style"])
def test_a_paint_with_a_fallback_still_pins_the_shape(where: str) -> None:
    paint = (
        'fill="url(#g) rgb(0, 0, 0)"'
        if where == "attribute"
        else 'style="fill: url(#g) rgb(0, 0, 0)"'
    )
    original = parse_svg(f"""
        <svg width="200" height="200">
            <linearGradient id="g" gradientUnits="userSpaceOnUse"
                            x1="20" y1="0" x2="180" y2="0">
                <stop offset="0" stop-color="gold"/>
                <stop offset="1" stop-color="navy"/>
            </linearGradient>
            <g transform="translate(30 40)">
                <rect x="10" y="10" width="100" height="60" {paint}/>
            </g>
        </svg>
    """)
    reified = copy.deepcopy(original)

    reified.reify()

    assert transforms_left(reified)
    assert_svg_visually_equal(original, reified)
