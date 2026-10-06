import svglab


def test_nested_svg_is_not_a_second_root() -> None:
    doc = svglab.parse_svg("<svg><svg/></svg>")

    assert isinstance(doc.find(svglab.Svg), svglab.Svg)
