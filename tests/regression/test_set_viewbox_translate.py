import copy

import svglab
from tests import conftest


def test_set_viewbox_translate() -> None:
    svg1 = svglab.parse_svg("""
        <svg width="100" height="100" viewBox="100 0 100 100">
            <rect x="100" y="0" width="100" height="100" fill="blue"/>
        </svg>
    """)
    svg2 = copy.deepcopy(svg1)

    svg2.set_viewbox((0, 0, 200, 200))
    rect = svg2.find(svglab.Rect)

    assert (rect.x, rect.y) == (svglab.Length(0), svglab.Length(0))
    conftest.assert_svg_visually_equal(svg1, svg2)
