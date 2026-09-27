import pytest

import svglab


@pytest.mark.parametrize("parser", ["html.parser", "lxml", "lxml-xml"])
def test_space_separated_class_survives_parsing(parser: str) -> None:
    doc = svglab.parse_svg(
        '<svg><rect class="a b"/></svg>',
        parser=parser,  # pyright: ignore[reportArgumentType]
    )

    assert doc.find(svglab.Rect).class_ == ["a", "b"]
