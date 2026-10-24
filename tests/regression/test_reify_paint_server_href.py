"""A gradient or pattern inherits what it leaves out from its `href`.

The inheritance runs through the whole chain of references and covers the
transformation attribute too. Reifying the template's transformation into its
coordinates would take it away from everything referring to it, and dropping
an identity transformation from a referring element would let the inherited
one through. A gradient that spells out its own geometry and only borrows
the stops, the way Inkscape writes every gradient, is reified on its own.
"""

import copy

import pytest

from svglab import Element, LinearGradient, Pattern, parse_svg
from tests.conftest import assert_svg_visually_equal, transforms_left


@pytest.mark.parametrize("element", ["linearGradient", "pattern"])
def test_transform_inherited_through_href_is_left_alone(
    element: str,
) -> None:
    transform_attr = (
        "gradientTransform"
        if element == "linearGradient"
        else "patternTransform"
    )
    size = (
        ""
        if element == "linearGradient"
        else ' patternUnits="userSpaceOnUse" width="20" height="20"'
    )
    content = (
        '<stop offset="0" stop-color="gold"/>'
        '<stop offset="1" stop-color="navy"/>'
        if element == "linearGradient"
        else '<rect width="20" height="20" fill="navy"/>'
        '<rect width="10" height="20" fill="gold"/>'
    )
    original = parse_svg(f"""
        <svg width="200" height="200"
             xmlns:xlink="http://www.w3.org/1999/xlink">
            <{element} id="template" {transform_attr}="rotate(90 0.5 0.5)"
                       x1="0" y1="0" x2="1" y2="0"{size}>
                {content}
            </{element}>
            <{element} id="inherited" xlink:href="#template"/>
            <{element} id="chained" href="#inherited"/>
            <{element} id="overridden" href="#chained"
                       {transform_attr}="scale(1)"/>
            <g transform="translate(20 20)">
                <rect width="70" height="70" fill="url(#template)"/>
            </g>
            <g transform="translate(110 20)">
                <rect width="70" height="70" fill="url(#inherited)"/>
            </g>
            <g transform="translate(20 110)">
                <rect width="70" height="70" fill="url(#chained)"/>
            </g>
            <g transform="translate(110 110)">
                <rect width="70" height="70" fill="url(#overridden)"/>
            </g>
        </svg>
    """)
    reified = copy.deepcopy(original)

    reified.reify()

    kept = {e.id for e in transforms_left(reified)}

    assert {"template", "overridden"} <= kept
    assert "inherited" not in kept
    assert_svg_visually_equal(original, reified)


def test_pattern_units_are_read_through_href() -> None:
    # the pattern itself says nothing about its units, so it tiles the user
    # space the way its template does, and a shape painted with it may not be
    # moved out from under the tiling
    original = parse_svg("""
        <svg width="200" height="200">
            <pattern id="template" patternUnits="userSpaceOnUse"
                     width="20" height="20">
                <rect width="10" height="10" fill="green"/>
            </pattern>
            <pattern id="p" href="#template"/>
            <rect x="10" y="10" width="100" height="100" fill="url(#p)"
                  transform="translate(5 7)"/>
        </svg>
    """)
    reified = copy.deepcopy(original)

    reified.reify()

    rect = reified.find("rect", recursive=False)

    assert isinstance(rect, Element)
    assert transforms_left(reified) == [rect]
    assert isinstance(reified.find(Pattern), Pattern)
    assert_svg_visually_equal(original, reified)


def test_a_gradient_that_only_borrows_the_stops_is_reified() -> None:
    original = parse_svg("""
        <svg width="200" height="200"
             xmlns:xlink="http://www.w3.org/1999/xlink">
            <linearGradient id="stops">
                <stop offset="0" stop-color="gold"/>
                <stop offset="1" stop-color="navy"/>
            </linearGradient>
            <linearGradient id="own" xlink:href="#stops"
                            gradientUnits="userSpaceOnUse"
                            gradientTransform="rotate(30 100 100)"
                            x1="20" y1="100" x2="180" y2="100"/>
            <rect x="20" y="20" width="160" height="160" fill="url(#own)"/>
        </svg>
    """)
    reified = copy.deepcopy(original)

    reified.reify()

    def own(svg: Element) -> LinearGradient:
        gradient, *_ = (
            g for g in svg.find_all(LinearGradient) if g.id == "own"
        )
        return gradient

    assert not transforms_left(reified)
    assert own(reified).x1 != own(original).x1
    assert_svg_visually_equal(original, reified, tolerance=1e-5)
