import copy

from svglab import Length, RawText, Scale, Svg, Text
from tests.conftest import assert_svg_visually_equal


def _svg() -> Svg:
    text = Text(
        x=[Length(10)],
        y=[Length(40)],
        dx=[Length(1), Length(2)],
        dy=[Length(3)],
        textLength=Length(50),
        font_size=Length(12),
        transform=[Scale(2)],
    )
    text.add_child(RawText("Hamburgefonstiv"))

    return Svg(width=Length(200), height=Length(200)).add_child(text)


def test_text_offsets_are_scaled() -> None:
    original = _svg()
    reified = copy.deepcopy(original)

    reified.reify()
    text = reified.find(Text)

    assert text.x == [Length(20)]
    assert text.y == [Length(80)]
    assert text.dx == [Length(2), Length(4)]
    assert text.dy == [Length(6)]
    assert text.textLength == Length(100)
    assert text.font_size == Length(24)

    assert_svg_visually_equal(original, reified)
