import copy

from svglab import Length, Rect, parse_svg
from tests.conftest import assert_svg_visually_equal


def test_set_viewbox_translate() -> None:
    svg1 = parse_svg("""
        <svg width="100" height="100" viewBox="100 0 100 100">
            <rect x="100" y="0" width="100" height="100" fill="blue"/>
        </svg>
    """)
    svg2 = copy.deepcopy(svg1)

    svg2.set_viewbox((0, 0, 200, 200))
    rect = svg2.find(Rect)

    assert (rect.x, rect.y) == (Length(0), Length(0))
    assert_svg_visually_equal(svg1, svg2)
