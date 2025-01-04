from typing import Final

import hypothesis
import hypothesis.strategies as st
import pydantic
import pytest

from svglab import elements, parse
from svglab.attrparse import length, transform


numbers: Final = st.floats(allow_nan=False, allow_infinity=False)


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

    with pytest.raises(
        ValueError, match="Failed to parse text with grammar 'length.lark'"
    ):
        parse.parse_svg(xml)


@hypothesis.given(numbers, st.one_of(numbers, st.none()))
def test_valid_scale(x: float, y: float | None) -> None:
    util_test_transform(
        f"scale({x}, {y})" if y is not None else f"scale({x})",
        [transform.Scale(x, y)],
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
        f"matrix({a}, {b}, {c}, {d}, {e}, {f})",
        [transform.Matrix(a, b, c, d, e, f)],
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
        ValueError,
        match="Failed to parse text with grammar 'transform.lark'",
    ):
        parse.parse_svg(f"<svg><rect transform='{text}'/></svg>")


def test_invalid_rotate() -> None:
    with pytest.raises(
        ValueError,
        match="Both cx and cy must either be provided or omitted",
    ):
        transform.Rotate(1, 2)  # pyright: ignore[reportCallIssue]


def test_attribute_normalization_native() -> None:
    rect = elements.Rect(
        stroke_dasharray="1 2 3",
        stroke_dashoffset=length.Length(1),
        stroke_linecap="round",
        stroke_linejoin="round",
        stroke_width=length.Length(1),
        stroke_opacity=0.9,
        xml_base="http://example.com",
        xml_lang="en",
        xml_space="preserve",
    )

    assert rect.extra_attrs() == {}

    assert rect.stroke_dasharray == "1 2 3"
    assert rect.stroke_dashoffset == length.Length(1)
    assert rect.stroke_linecap == "round"
    assert rect.stroke_linejoin == "round"
    assert rect.stroke_width == length.Length(1)
    assert rect.stroke_opacity == 0.9
    assert rect.xml_base == "http://example.com"
    assert rect.xml_lang == "en"
    assert rect.xml_space == "preserve"


def test_attribute_normalization_validate() -> None:
    rect = elements.Rect.model_validate(
        {
            "stroke-dasharray": "1 2 3",
            "stroke-dashoffset": length.Length(1),
            "stroke-linecap": "round",
            "stroke-linejoin": "round",
            "stroke-width": length.Length(1),
            "stroke-opacity": 0.9,
            "xml:base": "http://example.com",
            "xml:lang": "en",
            "xml:space": "preserve",
        }
    )

    assert rect.extra_attrs() == {}

    assert rect.stroke_dasharray == "1 2 3"
    assert rect.stroke_dashoffset == length.Length(1)
    assert rect.stroke_linecap == "round"
    assert rect.stroke_linejoin == "round"
    assert rect.stroke_width == length.Length(1)
    assert rect.stroke_opacity == 0.9
    assert rect.xml_base == "http://example.com"
    assert rect.xml_lang == "en"
    assert rect.xml_space == "preserve"


def test_attribute_normalization_serialize() -> None:
    rect = elements.Rect(
        stroke_dasharray="1 2 3",
        stroke_dashoffset=length.Length(1),
        stroke_linecap="round",
        stroke_linejoin="round",
        stroke_width=length.Length(1),
        stroke_opacity=0.9,
        xml_base="http://example.com",
        xml_lang="en",
        xml_space="preserve",
    )

    attrs = {
        "stroke-dasharray": "1 2 3",
        "stroke-dashoffset": {"value": 1},
        "stroke-linecap": "round",
        "stroke-linejoin": "round",
        "stroke-width": {"value": 1},
        "stroke-opacity": 0.9,
        "xml:base": "http://example.com",
        "xml:lang": "en",
        "xml:space": "preserve",
    }

    dump = rect.model_dump(
        by_alias=True,
        exclude_defaults=True,
        exclude_unset=True,
        exclude_none=True,
    )

    assert dump == attrs


@pytest.mark.parametrize(
    "element", [elements.RawText, elements.Comment, elements.CData]
)
def test_text_elements_min_str_length_invalid(
    element: type[elements.RawText | elements.Comment | elements.CData],
) -> None:
    with pytest.raises(pydantic.ValidationError):
        element("")


@hypothesis.given(st.text(min_size=1))
def test_text_elements_min_str_length_valid(test: str) -> None:
    elements.RawText(test)
    elements.Comment(test)
    elements.CData(test)


@hypothesis.given(st.text(min_size=1))
def test_eq_text(text: str) -> None:
    assert elements.RawText(text) == elements.RawText(text)
    assert elements.Comment(text) == elements.Comment(text)
    assert elements.CData(text) == elements.CData(text)

    assert elements.RawText(text) != elements.Comment(text)
    assert elements.RawText(text) != elements.CData(text)
    assert elements.Comment(text) != elements.CData(text)


def test_eq_tag_simple() -> None:
    assert elements.Rect() == elements.Rect()
    assert elements.Rect() != elements.Circle()

    stroke_width = length.Length(1, "px")

    assert elements.Rect(stroke_width=stroke_width) == elements.Rect(
        stroke_width=stroke_width
    )
    assert elements.Rect(stroke_width=stroke_width) != elements.Rect()
    assert elements.Rect(stroke_width=stroke_width) != elements.Rect(
        stroke_width=length.Length(2, "px")
    )
    assert elements.Rect(stroke_width=stroke_width) != elements.Circle(
        stroke_width=stroke_width
    )

    assert elements.Rect(stroke_width=stroke_width) != elements.Rect(
        stroke_width=stroke_width, stroke="red"
    )


@pytest.mark.xfail
def test_eq_tag_group() -> None:
    assert elements.G().add_child(
        elements.Rect()
    ) == elements.G().add_child(elements.Rect())
