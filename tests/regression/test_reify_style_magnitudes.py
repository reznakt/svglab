"""A magnitude declared in a `style` attribute is resized where it stands.

Editors write the stroke width, the dash pattern and the font size into the
`style` attribute rather than the presentation attribute. Such a declaration
beats the attribute, so reification reads it the way the attribute would be
read and writes the resized value back into the declaration, leaving the
rest of the style, `!important` included, exactly as it was.
"""

import copy

import pytest

from svglab import Length, Path, Rect, Text, parse_svg
from tests.conftest import assert_svg_visually_equal, transforms_left


def test_a_declared_stroke_is_resized_in_the_declaration() -> None:
    style = (
        "fill:none; stroke:black; stroke-width : 0.5 ;"
        " stroke-dasharray:4,2; stroke-linecap:round"
    )
    original = parse_svg(f"""
        <svg width="200" height="200">
            <g transform="scale(2)">
                <path d="M10 10 L50 50" style="{style}"/>
            </g>
        </svg>
    """)
    reified = copy.deepcopy(original)

    reified.reify()

    path = reified.find(Path)

    assert not transforms_left(reified)
    assert path.style == (
        "fill:none; stroke:black; stroke-width : 1 ;"
        " stroke-dasharray:8 4; stroke-linecap:round"
    )
    assert_svg_visually_equal(original, reified, tolerance=1e-5)


def test_an_important_declaration_stays_important() -> None:
    svg = parse_svg("""
        <svg width="200" height="200">
            <rect x="1" y="1" width="10" height="10" transform="scale(2)"
                  style="stroke:black;stroke-width:3px !important"/>
        </svg>
    """)

    svg.reify()

    assert (
        svg.find(Rect).style == "stroke:black;stroke-width:6px !important"
    )


def test_a_magnitude_inherited_from_a_style_is_written_as_an_attribute() -> (
    None
):
    original = parse_svg("""
        <svg width="200" height="200">
            <g transform="scale(2)" style="stroke:black;stroke-width:1.5px;
                                           font-size:10px">
                <text x="10" y="80">Hi</text>
            </g>
        </svg>
    """)
    reified = copy.deepcopy(original)

    reified.reify()

    text = reified.find(Text)

    assert not transforms_left(reified)
    assert text.font_size == Length(20, "px")
    assert text.stroke_width == Length(3, "px")
    assert_svg_visually_equal(original, reified, tolerance=1e-5)


@pytest.mark.parametrize(
    "declaration",
    ["stroke-width: bogus", "stroke-width: 2%", "font: 12px serif"],
    ids=["unreadable", "percentage", "shorthand"],
)
def test_a_declaration_reification_cannot_resize_holds_the_shape(
    declaration: str,
) -> None:
    svg = parse_svg(f"""
        <svg width="200" height="200">
            <text x="10" y="80" stroke="black" transform="scale(2)"
                  style="{declaration}">Hi</text>
        </svg>
    """)

    svg.reify()

    # the text may still be moved, but a scale has to stay
    assert svg.find(Text).transform is not None
