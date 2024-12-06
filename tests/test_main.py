import bs4
import hypothesis
import hypothesis.strategies as st
import pytest

from svglab import parse, types


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
    soup = bs4.BeautifulSoup(markup, features="lxml-xml")

    assert len(parse.get_root_svg_fragments(soup)) == fragment_count


@pytest.mark.parametrize("parser", ["lxml", "lxml-xml", "html5lib"])
def test_get_root_svg_fragments_parser(parser: types.Parser) -> None:
    soup = bs4.BeautifulSoup("<svg></svg>", features=parser)

    assert len(parse.get_root_svg_fragments(soup)) == 1


@hypothesis.given(st.integers(min_value=0, max_value=100))
def test_get_root_svg_fragments_simple(fragment_count: int) -> None:
    soup = bs4.BeautifulSoup()

    for _ in range(fragment_count):
        soup.append(bs4.Tag(name="svg"))

    assert len(parse.get_root_svg_fragments(soup)) == fragment_count


@hypothesis.given(
    st.integers(min_value=0, max_value=100), st.integers(min_value=1, max_value=100)
)
def test_get_root_svg_fragments_nested(fragment_count: int, nesting_level: int) -> None:
    elem: bs4.Tag = bs4.BeautifulSoup()

    for _ in range(nesting_level):
        tag = bs4.Tag(name="g")
        elem.append(tag)
        elem = tag

    for _ in range(fragment_count):
        elem.append(bs4.Tag(name="svg"))

    assert len(parse.get_root_svg_fragments(elem)) == fragment_count
