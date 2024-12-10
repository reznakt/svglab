from typing import Final

import bs4
import hypothesis
import hypothesis.strategies as st
import pytest

from svglab import elements, parse, types
from svglab.attrparse import length, transform

numbers: Final = st.floats(allow_nan=False, allow_infinity=False)


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


@hypothesis.given(numbers)
def test_valid_length(value: float) -> None:
    units: list[length.LengthUnit | None] = [
        "px",
        "cm",
        "mm",
        "in",
        "pt",
        "pc",
        "%",
        None,
    ]

    for unit in units:
        xml = f"<svg><rect width='{value}{unit or ''}'/></svg>"
        svg = parse.parse_svg(xml)

        assert isinstance(svg, elements.Svg)

        rect = next(iter(svg.children))
        assert isinstance(rect, elements.Rect)

        assert rect.width == length.Length(value, unit)


@pytest.mark.parametrize("value", ["", "foo", "px", "1.2."])
def test_invalid_length(value: str) -> None:
    xml = f"<svg><rect width='{value}'/></svg>"

    with pytest.raises(ValueError, match="Failed to parse text with grammar 'length'"):
        parse.parse_svg(xml)


@hypothesis.given(numbers, st.one_of(numbers, st.none()))
def test_valid_scale(x: float, y: float | None) -> None:
    util_test_transform(
        f"scale({x}, {y})" if y is not None else f"scale({x})", [transform.Scale(x, y)]
    )


@hypothesis.given(numbers, st.one_of(numbers, st.none()))
def test_valid_translate(x: float, y: float | None) -> None:
    util_test_transform(
        f"translate({x}, {y})" if y is not None else f"translate({x})",
        [transform.Translate(x, y)],
    )


@hypothesis.given(numbers)
def test_valid_rotate(angle: float) -> None:
    util_test_transform(f"rotate({angle})", [transform.Rotate(angle)])


@hypothesis.given(numbers)
def test_valid_skew_x(angle: float) -> None:
    util_test_transform(f"skewX({angle})", [transform.SkewX(angle)])


@hypothesis.given(numbers)
def test_valid_skew_y(angle: float) -> None:
    util_test_transform(f"skewY({angle})", [transform.SkewY(angle)])


@hypothesis.given(numbers, numbers, numbers, numbers, numbers, numbers)
def test_valid_matrix(
    a: float, b: float, c: float, d: float, e: float, f: float
) -> None:
    util_test_transform(
        f"matrix({a}, {b}, {c}, {d}, {e}, {f})", [transform.Matrix(a, b, c, d, e, f)]
    )


def util_test_transform(text: str, parsed: transform.Transform) -> None:
    xml = f"<svg><rect transform='{text}'/></svg>"
    svg = parse.parse_svg(xml)

    assert isinstance(svg, elements.Svg)

    rect = next(iter(svg.children))
    assert isinstance(rect, elements.Rect)

    assert rect.transform == parsed


def test_valid_transform_sequence() -> None:
    transforms: dict[str, transform.TransformAction] = {
        "scale(1.5, 2)": transform.Scale(1.5, 2),
        "scale(1.5)": transform.Scale(1.5),
        "translate(1, 2)": transform.Translate(1, 2),
        "translate(.1)": transform.Translate(0.1),
        "rotate(45)": transform.Rotate(45),
        "rotate(45, 1, 2.)": transform.Rotate(45, 1, 2.0),
        "skewX(45)": transform.SkewX(45),
        "skewY(45)": transform.SkewY(45),
        "matrix(1, 0, 0, 1, 0, 0)": transform.Matrix(1, 0, 0, 1, 0, 0),
        "skewX(1e+04)": transform.SkewX(1e4),
        "skewX(1e-04)": transform.SkewX(1e-4),
    }

    for sep in ",", " ":
        transform_text = sep.join(transforms.keys())
        util_test_transform(transform_text, list(transforms.values()))


@pytest.mark.parametrize(
    "text",
    [
        "",
        "foo",
        "scale(1,",
        "scale(1, 2, 3)",
        "rotate(1, 2)",
        "matrix(1, 2)",
        "matrix(1, 2, 3, 4, 5, 6, 7)",
        "skewX(1, 2)",
        "skewY(1, 2)",
        "translate(1, 2, 3)",
    ],
)
def test_invalid_transform(text: str) -> None:
    with pytest.raises(
        ValueError, match="Failed to parse text with grammar 'transform'"
    ):
        parse.parse_svg(f"<svg><rect transform='{text}'/></svg>")


def test_invalid_rotate() -> None:
    with pytest.raises(
        ValueError, match="Both cx and cy must either be provided or omitted"
    ):
        transform.Rotate(1, 2)
