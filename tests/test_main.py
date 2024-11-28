import bs4
import pytest
from bs4 import BeautifulSoup
from hypothesis import given
from hypothesis.strategies import integers

from svglab.parse import Parser, get_root_svg_fragments


@pytest.mark.parametrize(
    ("markup", "fragment_count"),
    [
        ("a", 0),
        ("", 0),
        ("<svg></svg>", 1),
        ("<svg></svg><svg></svg>", 1),
        ("<foo><svg></svg></foo>", 1),
    ],
)
def test_get_root_svg_fragments(markup: str, fragment_count: int) -> None:
    soup = BeautifulSoup(markup, features="lxml-xml")

    assert len(get_root_svg_fragments(soup)) == fragment_count


@pytest.mark.parametrize("parser", ["lxml", "lxml-xml", "html5lib"])
def test_get_root_svg_fragments_parser(parser: Parser) -> None:
    soup = BeautifulSoup("<svg></svg>", features=parser)

    assert len(get_root_svg_fragments(soup)) == 1


@given(integers(min_value=0, max_value=100))
def test_get_root_svg_fragments_simple(fragment_count: int) -> None:
    soup = BeautifulSoup()

    for _ in range(fragment_count):
        soup.append(bs4.Tag(name="svg"))

    assert len(get_root_svg_fragments(soup)) == fragment_count


@given(integers(min_value=0, max_value=100), integers(min_value=1, max_value=100))
def test_get_root_svg_fragments_nested(fragment_count: int, nesting_level: int) -> None:
    elem: bs4.Tag = BeautifulSoup()

    for _ in range(nesting_level):
        tag = bs4.Tag(name="g")
        elem.append(tag)
        elem = tag

    for _ in range(fragment_count):
        elem.append(bs4.Tag(name="svg"))

    assert len(get_root_svg_fragments(elem)) == fragment_count
