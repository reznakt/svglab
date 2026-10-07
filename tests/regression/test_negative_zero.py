import svglab


def test_negative_zero_drops_sign() -> None:
    rect = svglab.Rect(x=svglab.Length(-0.0))

    assert rect.to_xml() == '<rect x="0"/>'


def test_negative_number_rounded_to_zero_drops_sign() -> None:
    rect = svglab.Rect(x=svglab.Length(-0.001))

    with svglab.Formatter(general_precision=2):
        assert rect.to_xml() == '<rect x="0"/>'
