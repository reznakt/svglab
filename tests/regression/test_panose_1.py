from svglab import FontFace, parse_svg


def test_panose_1_is_parsed() -> None:
    svg = parse_svg(
        '<svg><font-face panose-1="2 0 5 3 0 0 0 2 0 4"/></svg>'
    )

    assert svg.find(FontFace).panose_1 == (2, 0, 5, 3, 0, 0, 0, 2, 0, 4)


def test_panose_1_is_serialized() -> None:
    font_face = FontFace(panose_1=(2, 0, 5, 3, 0, 0, 0, 2, 0, 4))

    assert (
        font_face.to_xml() == '<font-face panose-1="2 0 5 3 0 0 0 2 0 4"/>'
    )
