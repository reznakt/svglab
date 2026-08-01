import svglab


def test_text_offsets_are_scaled() -> None:
    text = svglab.Text(
        x=[svglab.Length(10)],
        y=[svglab.Length(20)],
        dx=[svglab.Length(1), svglab.Length(2)],
        dy=[svglab.Length(3)],
        textLength=svglab.Length(50),
        font_size=svglab.Length(12),
        transform=[svglab.Scale(2)],
    )

    text.reify()

    assert text.x == [svglab.Length(20)]
    assert text.y == [svglab.Length(40)]
    assert text.dx == [svglab.Length(2), svglab.Length(4)]
    assert text.dy == [svglab.Length(6)]
    assert text.textLength == svglab.Length(100)
    assert text.font_size == svglab.Length(24)
