import copy

import svglab
from tests import conftest


def test_render_size_from_physical_dimensions() -> None:
    svg = svglab.parse_svg("""
        <svg xmlns="http://www.w3.org/2000/svg"
             width="2in" height="1in">
            <rect width="1cm" height="10" fill="blue"/>
        </svg>
    """)

    assert svg.render().size == (192, 96)


def test_render_size_prefers_physical_dimensions_over_viewbox() -> None:
    svg = svglab.parse_svg("""
        <svg xmlns="http://www.w3.org/2000/svg"
             width="254mm" height="127mm" viewBox="0 0 254 127">
            <rect width="100" height="100" fill="blue"/>
        </svg>
    """)

    assert svg.render().size == (960, 480)


def test_physical_units_match_renderer() -> None:
    physical = svglab.parse_svg("""
        <svg xmlns="http://www.w3.org/2000/svg" width="200" height="200">
            <rect x="0.5in" y="1cm" width="36pt" height="3pc" fill="red"/>
        </svg>
    """)
    user = svglab.parse_svg("""
        <svg xmlns="http://www.w3.org/2000/svg" width="200" height="200">
            <rect x="48" y="37.795275590551185" width="48" height="48"
                  fill="red"/>
        </svg>
    """)

    conftest.assert_svg_visually_equal(physical, user)


def test_reify_converts_physical_units() -> None:
    original = svglab.parse_svg("""
        <svg xmlns="http://www.w3.org/2000/svg" width="200" height="200">
            <rect x="0.5in" y="1cm" width="36pt" height="3pc" fill="red"
                  transform="translate(10 20) scale(1.5)"/>
        </svg>
    """)

    reified = copy.deepcopy(original)
    reified.reify()
    rect = reified.find(svglab.Rect)

    assert rect.transform is None
    conftest.assert_svg_visually_equal(original, reified)


def test_serialize_converts_physical_units_to_pixels() -> None:
    with svglab.Formatter(length_unit="px"):
        assert svglab.Length(1, "in").serialize() == "96px"
