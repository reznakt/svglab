import hypothesis
import hypothesis.strategies as st
import pydantic
import pytest
from typing_extensions import Final

from svglab import elements, errors, parse
from svglab.attrparse import d, length, point, transform


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
        [transform.Scale(x) if y is None else transform.Scale(x, y)],
    )


@hypothesis.given(numbers, st.one_of(numbers, st.none()))
def test_valid_translate(x: float, y: float | None) -> None:
    util_test_transform(
        f"translate({x}, {y})" if y is not None else f"translate({x})",
        [
            transform.Translate(x)
            if y is None
            else transform.Translate(x, y)
        ],
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

    dump = rect.model_dump(by_alias=True, exclude_none=True)

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


def test_eq_tag_group() -> None:
    assert elements.G().add_child(
        elements.Rect()
    ) == elements.G().add_child(elements.Rect())


@hypothesis.given(st.text())
def test_eq_tag_prefix(prefix: str) -> None:
    assert elements.Rect(prefix=prefix) == elements.Rect(prefix=prefix)


def test_xmlns_always_present_on_svg() -> None:
    svg = elements.Svg()

    assert "xmlns" in svg.standard_attrs()
    assert svg.xmlns == "http://www.w3.org/2000/svg"


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("", d.D()),
        ("M 10,10", d.D().move_to(point.Point(10, 10))),
        (
            "M0,0L 10,10",
            d.D().move_to(point.Point(0, 0)).line_to(point.Point(10, 10)),
        ),
        (
            "M0,0H 10",
            d.D().move_to(point.Point(0, 0)).horizontal_line_to(10),
        ),
        (
            "M0,0V 10",
            d.D().move_to(point.Point(0, 0)).vertical_line_to(10),
        ),
        (
            # https://github.com/mathandy/svgpathtools/issues/185
            "M12 22a10 10 0 110-20 10 10 0 010 20z",
            d.D()
            .move_to(point.Point(12, 22))
            .arc_to(
                point.Point(22, 32),
                0,
                point.Point(12, 2),
                large=True,
                sweep=True,
            )
            .arc_to(
                point.Point(22, 12),
                0,
                point.Point(12, 22),
                large=False,
                sweep=True,
            )
            .close(),
        ),
        (
            "M1 1 2 2 3 3 4 4",
            d.D()
            .move_to(point.Point(1, 1))
            .line_to(point.Point(2, 2))
            .line_to(point.Point(3, 3))
            .line_to(point.Point(4, 4)),
        ),
        (
            "M0,0C 10,10 20,20 30,30S 40,40 50,50Q 60,60 70,70T 80,80A 90,90 0"
            " 1 0 100,100T 110,110ZH 120V 130L 140,140Z",
            d.D()
            .move_to(point.Point(0, 0))
            .cubic_bezier_to(
                point.Point(10, 10),
                point.Point(20, 20),
                point.Point(30, 30),
            )
            .smooth_cubic_bezier_to(
                point.Point(40, 40), point.Point(50, 50)
            )
            .quadratic_bezier_to(point.Point(60, 60), point.Point(70, 70))
            .smooth_quadratic_bezier_to(point.Point(80, 80))
            .arc_to(
                point.Point(90, 90),
                0,
                point.Point(100, 100),
                large=True,
                sweep=False,
            )
            .smooth_quadratic_bezier_to(point.Point(110, 110))
            .close()
            .horizontal_line_to(120)
            .vertical_line_to(130)
            .line_to(point.Point(140, 140))
            .close(),
        ),
    ],
)
def test_path_data_parse(text: str, expected: str) -> None:
    assert d.D.from_str(text) == expected


def test_path_data_parse_moveto_must_be_first() -> None:
    with pytest.raises(
        ValueError, match="Failed to parse text with grammar 'd.lark'"
    ):
        d.D.from_str("L 10,10")


SHORTHAND_TESTS: Final[list[tuple[d.D, d.D]]] = [
    (d.D(), d.D()),
    (
        d.D().move_to(point.Point(10, 10)),
        d.D().move_to(point.Point(10, 10)),
    ),
    (
        d.D().move_to(point.Point.zero()).line_to(point.Point(0, 10)),
        d.D().move_to(point.Point.zero()).vertical_line_to(10),
    ),
    (
        d.D().move_to(point.Point.zero()).line_to(point.Point(10, 0)),
        d.D().move_to(point.Point.zero()).horizontal_line_to(10),
    ),
    (
        d.D()
        .move_to(point.Point.zero())
        .quadratic_bezier_to(point.Point(20, 0), point.Point(20, 20))
        .quadratic_bezier_to(point.Point(20, 40), point.Point(40, 40)),
        d.D()
        .move_to(point.Point.zero())
        .quadratic_bezier_to(point.Point(20, 0), point.Point(20, 20))
        .smooth_quadratic_bezier_to(point.Point(40, 40)),
    ),
    (
        d.D()
        .move_to(point.Point.zero())
        .cubic_bezier_to(
            point.Point(20, 0), point.Point(40, 0), point.Point(40, 20)
        )
        .cubic_bezier_to(
            point.Point(40, 40), point.Point(20, 40), point.Point(20, 20)
        ),
        d.D()
        .move_to(point.Point.zero())
        .cubic_bezier_to(
            point.Point(20, 0), point.Point(40, 0), point.Point(40, 20)
        )
        .smooth_cubic_bezier_to(point.Point(20, 40), point.Point(20, 20)),
    ),
]


@pytest.mark.parametrize(("before", "after"), SHORTHAND_TESTS)
def test_path_data_apply_shorthands(before: d.D, after: d.D) -> None:
    assert before.apply_shorthands() == after


@pytest.mark.parametrize(("after", "before"), SHORTHAND_TESTS)
def test_path_data_resolve_shorthands(after: d.D, before: d.D) -> None:
    assert before.resolve_shorthands() == after


@pytest.mark.parametrize(("before", "after"), SHORTHAND_TESTS)
def test_path_data_shorthands_cancel(before: d.D, after: d.D) -> None:
    assert before.apply_shorthands().resolve_shorthands() == before
    assert after.resolve_shorthands().apply_shorthands() == after


@pytest.mark.parametrize(("before", "after"), SHORTHAND_TESTS)
def test_path_data_shorthands_idempotent(before: d.D, after: d.D) -> None:
    assert (
        before.apply_shorthands()
        == before.apply_shorthands().apply_shorthands()
    )
    assert (
        after.apply_shorthands()
        == after.apply_shorthands().apply_shorthands()
    )


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("", ""),
        ("M0 0", "M0,0"),
        ("m 1e+02 1e-02", "M100,0.01"),
        (
            "M12 22a10 10 0 110-20 10 10 0 010 20z",
            "M12,22 A22,32 0 1 1 12,2 22,12 0 0 1 12,22 Z",
        ),
        (
            "m10,10 h100 v100 l10,10 10,10 z",
            "M10,10 H110 V110 L120,120 130,130 Z",
        ),
    ],
)
def test_path_data_parse_serialize(text: str, expected: str) -> None:
    assert d.D.from_str(text).serialize() == expected


def test_path_data_first_command_is_move_to() -> None:
    with pytest.raises(errors.SvgPathMissingMoveToError):
        d.D().line_to(point.Point(0, 0))

    path = d.D().move_to(point.Point(0, 0)).line_to(point.Point(0, 0))
    line_to = path[1]

    with pytest.raises(errors.SvgPathMissingMoveToError):
        del path[0]

    with pytest.raises(errors.SvgPathMissingMoveToError):
        path[0] = line_to

    with pytest.raises(errors.SvgPathMissingMoveToError):
        d.D().insert(0, line_to)

    with pytest.raises(errors.SvgPathMissingMoveToError):
        d.D().append(line_to)


@pytest.mark.parametrize(
    ("transforms", "before", "after"),
    [
        (
            [transform.Translate(1, 2)],
            point.Point(1, 2),
            point.Point(2, 4),
        ),
        ([transform.Scale(2)], point.Point(1, 2), point.Point(2, 4)),
        (
            [transform.Rotate(45, 1, 1)],
            point.Point(1, 1),
            point.Point(1, 1),
        ),
        (
            [transform.Rotate(90, 2, 2)],
            point.Point(1, 1),
            point.Point(3, 1),
        ),
        ([transform.Rotate(90)], point.Point(1, 2), point.Point(-2, 1)),
        ([transform.SkewX(45)], point.Point(1, 2), point.Point(3, 2)),
        ([transform.SkewY(45)], point.Point(1, 2), point.Point(1, 3)),
    ],
)
def test_matrix_multiplication(
    transforms: transform.Transform,
    before: transform.Matrix,
    after: transform.Matrix,
) -> None:
    transformed = transform.compose(transforms) @ before

    assert transformed == after
