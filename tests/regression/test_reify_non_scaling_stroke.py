import svglab


def test_reify_does_not_scale_non_scaling_stroke() -> None:
    svg = svglab.parse_svg("""
        <svg width="200" height="200" viewBox="0 0 200 200">
            <g stroke="black" stroke-width="5" transform="scale(2)">
                <path d="M10,10 L50,50" vector-effect="non-scaling-stroke"/>
            </g>
        </svg>
    """)
    svg.reify()

    assert svg.find(svglab.Path).stroke_width is None
