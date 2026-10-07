import pytest

from svglab import Rect, parse_svg


@pytest.mark.parametrize("parser", ["html.parser", "lxml", "lxml-xml"])
def test_space_separated_class_survives_parsing(parser: str) -> None:
    doc = parse_svg(
        '<svg><rect class="a b"/></svg>',
        parser=parser,  # pyright: ignore[reportArgumentType]
    )

    assert doc.find(Rect).class_ == ["a", "b"]
