from svglab import Svg, parse_svg


def test_nested_svg_is_not_a_second_root() -> None:
    doc = parse_svg("<svg><svg/></svg>")

    assert isinstance(doc.find(Svg), Svg)
