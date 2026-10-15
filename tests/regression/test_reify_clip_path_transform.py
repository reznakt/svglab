"""A clip path in bounding box units applies its transform after the mapping.

The content of such a clip path is mapped onto the bounding box of the
element it clips, and the clip path's own `transform` is applied to the
result. Folding a transformation into the element changes the box, which
happens before the clip path's transform, so the two have to commute.
"""

import copy

import pytest

from svglab import ClipPath, Rect, parse_svg
from tests.conftest import assert_svg_visually_equal, transforms_left


@pytest.mark.parametrize(
    ("clip_transform", "shape_transform", "absorbed"),
    [
        ("translate(.1 0)", "translate(20 10)", True),
        ("translate(.1 0)", "scale(2 1)", False),
        ("rotate(30)", "scale(2)", True),
        ("rotate(30)", "translate(20 10)", False),
    ],
)
def test_what_commutes_with_the_clip_transform_is_absorbed(
    clip_transform: str, shape_transform: str, *, absorbed: bool
) -> None:
    original = parse_svg(f"""
        <svg width="200" height="200">
            <clipPath id="c" clipPathUnits="objectBoundingBox"
                      transform="{clip_transform}">
                <rect width=".6" height="1"/>
            </clipPath>
            <rect x="20" y="30" width="60" height="50" fill="green"
                  clip-path="url(#c)" transform="{shape_transform}"/>
        </svg>
    """)
    reified = copy.deepcopy(original)

    reified.reify()

    rect = reified.find(Rect, recursive=False)

    assert (rect.transform is None) == absorbed
    assert transforms_left(reified) == [
        reified.find(ClipPath),
        *([rect] if not absorbed else []),
    ]
    assert_svg_visually_equal(original, reified)
