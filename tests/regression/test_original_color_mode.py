from svglab import Formatter, Rect, parse_svg


def test_original_color_mode_writes_function_colors_verbatim() -> None:
    svg = parse_svg('<svg><rect fill="rgba(10, 20, 30, 0.5)"/></svg>')
    formatter = Formatter(color_mode="original")

    output = svg.find(Rect).to_xml(formatter=formatter)

    assert output == '<rect fill="rgba(10, 20, 30, 0.5)"/>'
    assert parse_svg(f"<svg>{output}</svg>") == svg
