import pytest

from svglab import Text, parse_svg


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("underline", ["underline"]),
        ("underline line-through", ["underline", "line-through"]),
        ("none", "none"),
        ("inherit", "inherit"),
    ],
)
def test_text_decoration_keywords_are_parsed(
    value: str, expected: object
) -> None:
    svg = parse_svg(f'<svg><text text-decoration="{value}"/></svg>')
    text = svg.find(Text)

    assert text.text_decoration == expected
    assert f'text-decoration="{value}"' in text.to_xml()


def test_unknown_text_decoration_keyword_is_rejected() -> None:
    with pytest.raises(ValueError, match="text-decoration"):
        parse_svg('<svg><text text-decoration="underline wavy"/></svg>')
