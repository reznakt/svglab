"""A clip path in bounding box units applies its transform after the mapping.

With `clipPathUnits="objectBoundingBox"` the content of a `clipPath` is drawn
in the bounding box of the element it clips, and the `transform` of the
`clipPath` is applied on top of that mapping, in user space. Handing the
transformation down to the content would apply it in the wrong coordinate
system.
"""

import copy

from svglab import ClipPath, parse_svg
from tests.conftest import assert_svg_visually_equal, transforms_left


def test_transform_on_bounding_box_clip_path_stays_put() -> None:
    original = parse_svg("""
        <svg width="200" height="200">
            <clipPath id="clip" clipPathUnits="objectBoundingBox"
                      transform="translate(100 -40) rotate(45)">
                <rect x="0.2" y="0.2" width="0.6" height="0.6"/>
            </clipPath>
            <rect width="200" height="200" fill="green"
                  clip-path="url(#clip)"/>
        </svg>
    """)
    reified = copy.deepcopy(original)

    reified.reify()

    assert transforms_left(reified) == [reified.find(ClipPath)]
    assert_svg_visually_equal(original, reified)


def test_transform_on_user_space_clip_path_is_handed_down() -> None:
    original = parse_svg("""
        <svg width="200" height="200">
            <clipPath id="clip" transform="translate(50 20) scale(2)">
                <rect x="10" y="10" width="40" height="40"/>
            </clipPath>
            <rect width="200" height="200" fill="green"
                  clip-path="url(#clip)"/>
        </svg>
    """)
    reified = copy.deepcopy(original)

    reified.reify()

    assert transforms_left(reified) == []
    assert_svg_visually_equal(original, reified)
