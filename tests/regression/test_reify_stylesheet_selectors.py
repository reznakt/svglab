"""A stylesheet may pick elements out by what reification rewrites.

An attribute selector such as `[transform]` stops matching once the attribute
is folded away, and a type selector such as `rect` stops matching a shape
that was converted into a path. Reification cannot tell which elements a
selector picks out, so it keeps its hands off in both cases.
"""

import copy

from svglab import Rect, parse_svg
from tests.conftest import assert_svg_visually_equal, transforms_left


def test_an_attribute_selector_on_a_geometric_attribute_stops_everything() -> (
    None
):
    original = parse_svg("""
        <svg width="200" height="200">
            <style>[transform="scale(2)"] { fill: green }</style>
            <rect x="10" y="10" width="40" height="40" fill="red"
                  transform="scale(2)"/>
        </svg>
    """)
    reified = copy.deepcopy(original)

    reified.reify()

    assert reified.to_xml() == original.to_xml()
    assert_svg_visually_equal(original, reified)


def test_a_selector_on_anything_else_leaves_reification_alone() -> None:
    original = parse_svg("""
        <svg width="200" height="200">
            <style>[fill="red"] { stroke: none } .a { fill: green }</style>
            <rect class="a" x="10" y="10" width="40" height="40" fill="red"
                  transform="scale(2)"/>
        </svg>
    """)
    reified = copy.deepcopy(original)

    reified.reify()

    assert not transforms_left(reified)
    assert_svg_visually_equal(original, reified)


def test_shapes_keep_their_names_in_a_document_with_a_stylesheet() -> None:
    original = parse_svg("""
        <svg width="200" height="200">
            <style>rect { fill: green }</style>
            <rect x="60" y="60" width="40" height="40" fill="red"
                  transform="rotate(30 80 80)"/>
        </svg>
    """)
    reified = copy.deepcopy(original)

    reified.reify(convert_shapes_to_paths=True)

    assert isinstance(reified.find(Rect), Rect)
    assert transforms_left(reified)
    assert_svg_visually_equal(original, reified)
