import copy

import svglab
from tests import conftest


def _svg() -> svglab.Svg:
    text = svglab.Text(
        x=[svglab.Length(10)],
        y=[svglab.Length(40)],
        dx=[svglab.Length(1), svglab.Length(2)],
        dy=[svglab.Length(3)],
        textLength=svglab.Length(50),
        font_size=svglab.Length(12),
        transform=[svglab.Scale(2)],
    )
    text.add_child(svglab.RawText("Hamburgefonstiv"))

    return svglab.Svg(
        width=svglab.Length(200), height=svglab.Length(200)
    ).add_child(text)


def test_text_offsets_are_scaled() -> None:
    original = _svg()
    reified = copy.deepcopy(original)

    reified.reify()
    text = reified.find(svglab.Text)

    assert text.x == [svglab.Length(20)]
    assert text.y == [svglab.Length(80)]
    assert text.dx == [svglab.Length(2), svglab.Length(4)]
    assert text.dy == [svglab.Length(6)]
    assert text.textLength == svglab.Length(100)
    assert text.font_size == svglab.Length(24)

    conftest.assert_svg_visually_equal(original, reified)
