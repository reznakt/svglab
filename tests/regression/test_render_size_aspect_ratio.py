import svglab


def test_render_size_aspect_ratio() -> None:
    svg = svglab.parse_svg("""
        <svg width="100" height="300" viewBox="0 0 100 300">
            <rect x="25" y="75" width="50" height="150" fill="blue"/>
        </svg>
    """)

    assert svg.render(width=360, height=360).size == (120, 360)
