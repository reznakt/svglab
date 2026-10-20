from svglab import G, Use, parse_svg


def test_clip_path_reference_is_detected() -> None:
    svg = parse_svg("""
        <svg>
            <clipPath id="c"/>
            <g clip-path="url(#c)"/>
        </svg>
    """)

    assert svg.find(G).references_other_element()


def test_xlink_href_reference_is_detected() -> None:
    svg = parse_svg("""
        <svg xmlns:xlink="http://www.w3.org/1999/xlink">
            <rect id="r"/>
            <use xlink:href="#r"/>
        </svg>
    """)

    assert svg.find(Use).references_other_element()
