import svglab


def test_fully_reified_gradient_transform_is_removed() -> None:
    svg = svglab.parse_svg("""
        <svg width="200" height="200">
            <linearGradient id="g" gradientUnits="userSpaceOnUse"
                            x1="0" y1="0" x2="100" y2="0"
                            gradientTransform="translate(10, 20)">
                <stop offset="0" stop-color="red"/>
            </linearGradient>
        </svg>
    """)

    svg.reify()
    gradient = svg.find(svglab.LinearGradient)

    assert gradient.gradientTransform is None
    assert "gradientTransform" not in gradient.to_xml()
