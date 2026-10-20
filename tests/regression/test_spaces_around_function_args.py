from svglab import Formatter, Rect, parse_svg


def test_spaces_around_function_args_are_idempotent() -> None:
    formatter = Formatter(
        color_mode="original", spaces_around_function_args=True
    )
    once = (
        parse_svg('<svg><rect fill="rgb(255, 0, 0)"/></svg>')
        .find(Rect)
        .to_xml(formatter=formatter)
    )

    twice = (
        parse_svg(f"<svg>{once}</svg>")
        .find(Rect)
        .to_xml(formatter=formatter)
    )

    assert once == twice == '<rect fill="rgb( 255, 0, 0 )"/>'
