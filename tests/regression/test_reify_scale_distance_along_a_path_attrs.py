import copy

import svglab
from tests import conftest


def test_reify_scale_distance_along_a_path_attrs() -> None:
    svg1 = svglab.parse_svg("""
        <svg width="100" height="100" viewBox="0 0 100 100">
            <path d="M0,0 L10,10" stroke="black" stroke-width="2"
                stroke-dasharray="6 3" stroke-dashoffset="1"
                transform="scale(3)"/>
        </svg>
    """)
    svg2 = copy.deepcopy(svg1)

    svg2.reify()

    conftest.assert_svg_visually_equal(svg1, svg2)
