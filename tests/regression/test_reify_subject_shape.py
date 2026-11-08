"""The element reification is called on keeps its type and its box."""

import copy

from svglab import Image, Rect, Svg, parse_svg
from tests.conftest import assert_svg_visually_equal, transforms_left


def test_the_shape_called_on_is_judged_as_the_shape_it_stays() -> None:
    # it is not converted into a path, so it must not be handed what only a
    # path could take: a rotation would otherwise be folded into its box
    original = parse_svg("""
        <svg width="200" height="200">
            <rect x="20" y="10" width="40" height="20" fill="green"
                  transform="rotate(30 60 60)"/>
        </svg>
    """)
    reified = copy.deepcopy(original)
    rect = reified.find(Rect)

    rect.reify(convert_shapes_to_paths=True)

    assert isinstance(reified.find(Rect), Rect)
    assert transforms_left(reified) == [rect]
    assert rect.width == original.find(Rect).width
    assert_svg_visually_equal(original, reified)


def test_a_viewport_without_extents_is_only_moved() -> None:
    # a nested svg without a width is as wide as its parent, and an image
    # without one is as wide as its bitmap; neither is a number to resize
    original = parse_svg("""
        <svg width="200" height="200">
            <svg viewBox="0 0 10 10" transform="scale(0.5) translate(20 20)">
                <rect width="10" height="10" fill="green"/>
            </svg>
            <image x="100" y="100" transform="scale(2)"
                   href="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAgAAAAICAIAAABLbSncAAAAIElEQVR4nGNgYGD4z8CASbIwyEHY6ICFQY4Rl8TA6QAAyQsI6uMMKtQAAAAASUVORK5CYII="/>
        </svg>
    """)
    reified = copy.deepcopy(original)

    reified.reify()

    nested = reified.find(Svg)
    image = reified.find(Image)

    assert transforms_left(reified) == [nested, image]
    assert nested.x is not None
    assert_svg_visually_equal(original, reified)
