"""A filter primitive placed in user space does not follow the element.

The filter region may follow the bounding box, but a primitive given a
position of its own -- a subregion, a light -- or sampling noise from the user
space stays where it is when the element's coordinates move.
"""

import copy

import pytest

from svglab import parse_svg
from tests.conftest import assert_svg_visually_equal, transforms_left


_BITMAP = (
    "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAgAAAAICAIAAABLbSncAAAAI"
    "ElEQVR4nGNgYGD4z8CASbIwyEHY6ICFQY4Rl8TA6QAAyQsI6uMMKtQAAAAASUVORK5CYII="
)


@pytest.mark.parametrize(
    "primitive",
    [
        f'<feImage x="60" width="80" href="{_BITMAP}"/>',
        '<feFlood x="60" y="60" width="80" height="80" flood-color="blue"/>',
        (
            '<feDiffuseLighting><fePointLight x="100" y="60" z="20"/>'
            "</feDiffuseLighting>"
        ),
        '<feTurbulence baseFrequency="0.05"/>',
    ],
    ids=["subregion", "flood", "light", "turbulence"],
)
def test_positioned_primitive_keeps_the_element_in_place(
    primitive: str,
) -> None:
    original = parse_svg(f"""
        <svg width="200" height="200">
            <filter id="f" x="0" y="0" width="1" height="1">
                {primitive}
            </filter>
            <rect x="40" y="40" width="120" height="120" fill="red"
                  filter="url(#f)" transform="rotate(45 100 100)"/>
        </svg>
    """)
    reified = copy.deepcopy(original)

    reified.reify()

    assert len(transforms_left(reified)) == 1
    assert reified.to_xml() == original.to_xml()


def test_relative_primitives_let_the_element_move() -> None:
    original = parse_svg("""
        <svg width="200" height="200">
            <filter id="f">
                <feGaussianBlur stdDeviation="3"/>
                <feOffset dx="5" dy="5"/>
            </filter>
            <rect x="40" y="40" width="80" height="80" fill="seagreen"
                  filter="url(#f)" transform="translate(20 10)"/>
        </svg>
    """)
    reified = copy.deepcopy(original)

    reified.reify()

    assert transforms_left(reified) == []
    assert_svg_visually_equal(original, reified, tolerance=1e-5)
