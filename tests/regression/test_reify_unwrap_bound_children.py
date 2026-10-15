"""A group whose children act on it is not bare, attributes or not.

A `title` is the tooltip of the group it sits in, a `desc` describes it, and
an animation that names no target animates it. Lifting such children into
the group's parent would attach them to the parent instead.
"""

import copy

import pytest

from svglab import G, parse_svg
from tests.conftest import assert_svg_visually_equal


@pytest.mark.parametrize(
    "child",
    [
        "<title>Bar 1</title>",
        "<desc>The first bar</desc>",
        '<animate attributeName="opacity" to="0" dur="1s"/>',
    ],
    ids=["title", "desc", "animation"],
)
def test_a_group_with_a_child_bound_to_it_is_kept(child: str) -> None:
    original = parse_svg(f"""
        <svg width="200" height="200">
            <g opacity=".5">
                <g transform="translate(10 10)">
                    {child}
                    <rect width="40" height="40" fill="green"/>
                </g>
                <circle cx="100" cy="100" r="20" fill="blue"/>
            </g>
        </svg>
    """)
    reified = copy.deepcopy(original)

    reified.reify(unwrap_groups=True)

    assert len(list(reified.find_all(G))) == 2
    assert_svg_visually_equal(original, reified)


def test_a_group_with_only_drawn_children_is_unwrapped() -> None:
    original = parse_svg("""
        <svg width="200" height="200">
            <g opacity=".5">
                <g transform="translate(10 10)">
                    <rect width="40" height="40" fill="green"/>
                </g>
            </g>
        </svg>
    """)
    reified = copy.deepcopy(original)

    reified.reify(unwrap_groups=True)

    assert len(list(reified.find_all(G))) == 1
    assert_svg_visually_equal(original, reified)
