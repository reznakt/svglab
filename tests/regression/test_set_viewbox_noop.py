import copy

import svglab


def test_set_viewbox_same_viewbox_is_noop() -> None:
    svg = svglab.parse_svg("""
        <svg viewBox="0 0 200 200">
            <rect x="10" y="20" width="30" height="40"/>
        </svg>
    """)
    original = copy.deepcopy(svg)

    svg.set_viewbox((0, 0, 200, 200))

    assert svg.to_xml() == original.to_xml()


def test_set_viewbox_is_idempotent() -> None:
    svg = svglab.parse_svg("""
        <svg viewBox="100 0 100 100">
            <rect x="100" y="0" width="100" height="100"/>
        </svg>
    """)

    svg.set_viewbox((0, 0, 200, 200))
    once = svg.to_xml()

    svg.set_viewbox((0, 0, 200, 200))

    assert svg.to_xml() == once


def test_set_viewbox_same_viewbox_from_width_and_height() -> None:
    svg = svglab.parse_svg("""
        <svg width="200" height="200">
            <rect x="10" y="20" width="30" height="40"/>
        </svg>
    """)

    svg.set_viewbox((0, 0, 200, 200))
    rect = svg.find(svglab.Rect)

    assert svg.viewBox == (0, 0, 200, 200)
    assert rect.transform is None
    assert (rect.x, rect.y) == (svglab.Length(10), svglab.Length(20))
