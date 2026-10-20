from svglab import Rect, parse_svg


def test_hidden_element_has_no_visible_bbox() -> None:
    svg = parse_svg("""
        <svg width="40" height="40">
            <rect x="10" y="10" width="10" height="10" visibility="hidden"/>
        </svg>
    """)

    assert svg.find(Rect).get_bbox(visible_only=True) is None


def test_child_of_hidden_group_has_no_visible_bbox() -> None:
    svg = parse_svg("""
        <svg width="40" height="40">
            <g visibility="hidden">
                <rect x="10" y="10" width="10" height="10"/>
            </g>
        </svg>
    """)

    assert svg.find(Rect).get_bbox(visible_only=True) is None


def test_hidden_overlay_does_not_occlude() -> None:
    svg = parse_svg("""
        <svg width="40" height="40">
            <rect x="10" y="10" width="10" height="10"/>
            <rect width="40" height="40" visibility="hidden"/>
        </svg>
    """)
    target = svg.find(Rect)

    assert target.get_bbox(visible_only=True) == (10, 10, 20, 20)
