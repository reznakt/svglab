from svglab import Rect, Svg, parse_svg


def test_whitespace_in_attribute_values_survives_a_roundtrip() -> None:
    svg = Svg().add_child(Rect(id="a\nb\tc\rd"))

    xml = svg.to_xml(pretty=False)

    assert xml == '<svg><rect id="a&#10;b&#9;c&#13;d"/></svg>'
    assert parse_svg(xml).find(Rect).id == "a\nb\tc\rd"
