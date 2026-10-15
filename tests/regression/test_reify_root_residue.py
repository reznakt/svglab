"""A residue on the outermost svg is written about the origin.

A residue is worked out about the origin, but an outermost `svg` left
without a `transform-origin` turns about its center, so the residue is
written back with the origin spelled out -- which also keeps a second pass
from taking the origin apart all over again.
"""

import copy

from svglab import Length, Svg, parse_svg


def test_a_residue_on_the_root_is_written_about_the_origin() -> None:
    svg = parse_svg("""
        <svg width="200" height="200" viewBox="0 0 100 100"
             transform="skewX(20)">
            <text x="20" y="50" font-size="12">Reify</text>
        </svg>
    """)

    svg.reify()

    assert svg.transform is not None
    assert svg.transform_origin == (Length(0), Length(0))


def test_reification_of_the_root_is_idempotent() -> None:
    original = parse_svg("""
        <svg width="200" height="200" viewBox="0 0 100 100"
             transform="matrix(1.2 -0.4 0.05 1.3 8 12)"
             transform-origin="25% 10">
            <path d="M30,80 a30,50 0 0,1 60,0 a30,50 0 0,1 -60,0"
                  fill="url(#g)"/>
            <radialGradient id="g" gradientTransform="rotate(30)">
                <stop offset="0" stop-color="gold"/>
                <stop offset="1" stop-color="navy"/>
            </radialGradient>
        </svg>
    """)
    once = copy.deepcopy(original)
    once.reify()
    twice = copy.deepcopy(once)
    twice.reify()

    assert isinstance(once, Svg)
    assert twice.to_xml() == once.to_xml()
