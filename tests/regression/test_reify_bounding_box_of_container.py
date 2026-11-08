"""A container's bounding box is the union of its children's boxes, as rects.

Renderers take the bounding box of a group to be the union of the bounding
boxes of its children, each transformed as a rectangle rather than as the
geometry inside it. Folding a child's rotation into its points tightens that
box, and with it moves a clip path, mask or filter the group lays out in
bounding box units.
"""

import copy

import pytest

from svglab import Polygon, parse_svg
from tests.conftest import assert_svg_visually_equal, transforms_left


@pytest.mark.parametrize(
    ("resource", "reference"),
    [
        (
            (
                '<clipPath id="r" clipPathUnits="objectBoundingBox">'
                '<circle cx=".5" cy=".5" r=".45"/></clipPath>'
            ),
            'clip-path="url(#r)"',
        ),
        (
            (
                '<mask id="r"><rect x="20" y="20" width="110" height="110" '
                'fill="white"/></mask>'
            ),
            'mask="url(#r)"',
        ),
        (
            (
                '<filter id="r"><feFlood flood-color="blue" '
                'flood-opacity=".4"/></filter>'
            ),
            'filter="url(#r)"',
        ),
    ],
    ids=["clip-path", "mask", "filter"],
)
def test_a_child_under_a_bounding_box_resource_keeps_its_turn(
    resource: str, reference: str
) -> None:
    original = parse_svg(f"""
        <svg width="200" height="200">
            <defs>{resource}</defs>
            <g {reference}>
                <polygon points="30,30 150,50 120,140 40,120" fill="purple"
                         transform="rotate(64 76 80) translate(5 5)"/>
            </g>
        </svg>
    """)
    reified = copy.deepcopy(original)

    reified.reify(convert_shapes_to_paths=True)

    polygon = reified.find(Polygon)

    # the move went through, the turn stayed
    assert transforms_left(reified) == [polygon]
    assert polygon.points != original.find(Polygon).points
    assert_svg_visually_equal(original, reified, tolerance=1e-5)


def test_a_child_under_a_user_space_resource_may_turn() -> None:
    original = parse_svg("""
        <svg width="200" height="200">
            <defs>
                <clipPath id="r" clipPathUnits="userSpaceOnUse">
                    <circle cx="90" cy="90" r="70"/>
                </clipPath>
            </defs>
            <g clip-path="url(#r)">
                <polygon points="30,30 150,50 120,140 40,120" fill="purple"
                         transform="rotate(64 76 80)"/>
            </g>
        </svg>
    """)
    reified = copy.deepcopy(original)

    reified.reify()

    assert not transforms_left(reified)
    assert_svg_visually_equal(original, reified, tolerance=1e-5)
