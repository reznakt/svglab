"""What a `use` refers to is rendered with the properties of the `use`.

An element referenced by `use` is drawn where it sits, inheriting from its
ancestors, and again wherever the `use` is, inheriting from the `use`. A
property that neither the element nor its ancestors up to the referenced one
spell out may differ between the two renderings, so reification cannot rely
on it: a shape may be stroked in one and not the other, and a stroke width
or a dash pattern it would have to resize may be anything.
"""

import copy

import pytest

from svglab import Rect, parse_svg
from tests.conftest import assert_svg_visually_equal, transforms_left


def test_a_stroke_the_use_passes_down_is_resized_nowhere() -> None:
    # the rect is drawn unstroked in place and stroked through the `use`,
    # at a width only the `use` knows, so there is nothing to double
    original = parse_svg("""
        <svg width="200" height="200"
             xmlns:xlink="http://www.w3.org/1999/xlink">
            <g id="shapes" fill="red">
                <rect width="20" height="30"
                      transform="translate(10 10) scale(2)"/>
            </g>
            <use xlink:href="#shapes" fill="none" stroke="black"
                 stroke-width="2" transform="translate(100 100)"/>
        </svg>
    """)
    reified = copy.deepcopy(original)

    reified.reify()

    assert transforms_left(reified) == [reified.find(Rect)]
    assert_svg_visually_equal(original, reified)


def test_a_stroke_spelled_out_below_the_referenced_element_is_known() -> (
    None
):
    original = parse_svg("""
        <svg width="200" height="200"
             xmlns:xlink="http://www.w3.org/1999/xlink">
            <g id="shapes" fill="red" stroke="black" stroke-width="2">
                <rect width="20" height="30"
                      transform="translate(10 10) scale(2)"/>
            </g>
            <use xlink:href="#shapes" fill="blue" stroke="green"
                 transform="translate(100 100)"/>
        </svg>
    """)
    reified = copy.deepcopy(original)

    reified.reify()

    assert not transforms_left(reified)
    assert_svg_visually_equal(original, reified)


def test_a_property_nothing_in_the_document_declares_is_known() -> None:
    # nothing anywhere sets a stroke, so the shape is unstroked in either
    # rendering and there is nothing to resize
    original = parse_svg("""
        <svg width="200" height="200"
             xmlns:xlink="http://www.w3.org/1999/xlink">
            <g id="shapes" fill="red">
                <rect width="20" height="30"
                      transform="translate(10 10) scale(2)"/>
            </g>
            <use xlink:href="#shapes" fill="blue"
                 transform="translate(100 100)"/>
        </svg>
    """)
    reified = copy.deepcopy(original)

    reified.reify()

    assert not transforms_left(reified)
    assert_svg_visually_equal(original, reified)


@pytest.mark.parametrize("units", ["userSpaceOnUse", "objectBoundingBox"])
def test_a_paint_the_use_may_pass_down_is_judged_by_the_document(
    units: str,
) -> None:
    # the `use` paints the shapes with a gradient; in user space it pins the
    # rect where it is, in bounding box units it only forbids turning it
    original = parse_svg(f"""
        <svg width="200" height="200"
             xmlns:xlink="http://www.w3.org/1999/xlink">
            <linearGradient id="g" gradientUnits="{units}"
                            x1="0" x2="100">
                <stop offset="0" stop-color="red"/>
                <stop offset="1" stop-color="blue"/>
            </linearGradient>
            <g id="shapes">
                <rect width="20" height="30"
                      transform="translate(10 10) scale(2 1)"/>
            </g>
            <use xlink:href="#shapes" fill="url(#g)"
                 transform="translate(100 100)"/>
        </svg>
    """)
    reified = copy.deepcopy(original)

    reified.reify()

    pinned = units == "userSpaceOnUse"

    assert bool(transforms_left(reified)) == pinned
    assert_svg_visually_equal(original, reified)


def test_a_marker_the_use_may_pass_down_only_lets_the_shape_move() -> None:
    original = parse_svg("""
        <svg width="200" height="200"
             xmlns:xlink="http://www.w3.org/1999/xlink">
            <marker id="m" markerWidth="10" markerHeight="10" refX="5"
                    refY="5">
                <circle cx="5" cy="5" r="4" fill="green"/>
            </marker>
            <g id="shapes" fill="none" stroke="black">
                <polyline points="0,0 20,10 0,20" transform="scale(2)"/>
            </g>
            <use xlink:href="#shapes" marker-mid="url(#m)"
                 transform="translate(100 100)"/>
        </svg>
    """)
    reified = copy.deepcopy(original)

    reified.reify()

    assert len(transforms_left(reified)) == 1
    assert_svg_visually_equal(original, reified)
