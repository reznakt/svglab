import copy

import hypothesis
import hypothesis.strategies as st
import pydantic
import pytest
from typing_extensions import Final

import svglab
from tests import conftest


numbers: Final = st.floats(allow_nan=False, allow_infinity=False)


@hypothesis.given(numbers)
def test_valid_length(value: float) -> None:
    units: list[svglab.LengthUnit | None] = [
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
        svg = svglab.parse_svg(xml)

        assert isinstance(svg, svglab.Svg)

        rect = next(iter(svg.children))
        assert isinstance(rect, svglab.Rect)

        assert rect.width == svglab.Length(value, unit)


@pytest.mark.parametrize("value", ["", "foo", "px", "1.2."])
def test_invalid_length(value: str) -> None:
    xml = f"<svg><rect width='{value}'/></svg>"

    with pytest.raises(
        ValueError, match="Failed to parse text with grammar 'length.lark'"
    ):
        svglab.parse_svg(xml)


def util_test_transform(text: str, parsed: svglab.Transform) -> None:
    xml = f"<svg><rect transform='{text}'/></svg>"
    svg = svglab.parse_svg(xml)

    assert isinstance(svg, svglab.Svg)

    rect = next(iter(svg.children))
    assert isinstance(rect, svglab.Rect)

    assert rect.transform == parsed


@hypothesis.given(numbers, st.one_of(numbers, st.none()))
def test_valid_scale(x: float, y: float | None) -> None:
    util_test_transform(
        f"scale({x}, {y})" if y is not None else f"scale({x})",
        [svglab.Scale(x) if y is None else svglab.Scale(x, y)],
    )


@hypothesis.given(numbers, st.one_of(numbers, st.none()))
def test_valid_translate(x: float, y: float | None) -> None:
    util_test_transform(
        f"translate({x}, {y})" if y is not None else f"translate({x})",
        [svglab.Translate(x) if y is None else svglab.Translate(x, y)],
    )


@hypothesis.given(numbers)
def test_valid_rotate(angle: float) -> None:
    util_test_transform(f"rotate({angle})", [svglab.Rotate(angle)])


@hypothesis.given(numbers)
def test_valid_skew_x(angle: float) -> None:
    util_test_transform(f"skewX({angle})", [svglab.SkewX(angle)])


@hypothesis.given(numbers)
def test_valid_skew_y(angle: float) -> None:
    util_test_transform(f"skewY({angle})", [svglab.SkewY(angle)])


@hypothesis.given(numbers, numbers, numbers, numbers, numbers, numbers)
def test_valid_matrix(
    a: float, b: float, c: float, d: float, e: float, f: float
) -> None:
    util_test_transform(
        f"matrix({a}, {b}, {c}, {d}, {e}, {f})",
        [svglab.Matrix(a, b, c, d, e, f)],
    )


def test_valid_transform_sequence() -> None:
    transforms: dict[str, svglab.TransformFunction] = {
        "scale(1.5, 2)": svglab.Scale(1.5, 2),
        "scale(1.5)": svglab.Scale(1.5),
        "translate(1, 2)": svglab.Translate(1, 2),
        "translate(.1)": svglab.Translate(0.1),
        "rotate(45)": svglab.Rotate(45),
        "rotate(45, 1, 2.)": svglab.Rotate(45, 1, 2.0),
        "skewX(45)": svglab.SkewX(45),
        "skewY(45)": svglab.SkewY(45),
        "matrix(1, 0, 0, 1, 0, 0)": svglab.Matrix(1, 0, 0, 1, 0, 0),
        "skewX(1e+04)": svglab.SkewX(1e4),
        "skewX(1e-04)": svglab.SkewX(1e-4),
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
        svglab.parse_svg(f"<svg><rect transform='{text}'/></svg>")


def test_attribute_normalization_native() -> None:
    rect = svglab.Rect(
        stroke_dasharray=[
            svglab.Length(1),
            svglab.Length(2),
            svglab.Length(3),
        ],
        stroke_dashoffset=svglab.Length(1),
        stroke_linecap="round",
        stroke_linejoin="round",
        stroke_width=svglab.Length(1),
        stroke_opacity=0.9,
        xml_base="http://example.com",
        xml_lang="en",
        xml_space="preserve",
    )

    assert rect.extra_attrs() == {}

    assert rect.stroke_dasharray == [
        svglab.Length(1),
        svglab.Length(2),
        svglab.Length(3),
    ]
    assert rect.stroke_dashoffset == svglab.Length(1)
    assert rect.stroke_linecap == "round"
    assert rect.stroke_linejoin == "round"
    assert rect.stroke_width == svglab.Length(1)
    assert rect.stroke_opacity == 0.9
    assert rect.xml_base == "http://example.com"
    assert rect.xml_lang == "en"
    assert rect.xml_space == "preserve"


def test_attribute_normalization_validate() -> None:
    rect = svglab.Rect.model_validate(
        {
            "stroke-dasharray": "1 2 3",
            "stroke-dashoffset": svglab.Length(1),
            "stroke-linecap": "round",
            "stroke-linejoin": "round",
            "stroke-width": svglab.Length(1),
            "stroke-opacity": 0.9,
            "xml:base": "http://example.com",
            "xml:lang": "en",
            "xml:space": "preserve",
        }
    )

    assert rect.extra_attrs() == {}

    assert rect.stroke_dasharray == [
        svglab.Length(1),
        svglab.Length(2),
        svglab.Length(3),
    ]
    assert rect.stroke_dashoffset == svglab.Length(1)
    assert rect.stroke_linecap == "round"
    assert rect.stroke_linejoin == "round"
    assert rect.stroke_width == svglab.Length(1)
    assert rect.stroke_opacity == 0.9
    assert rect.xml_base == "http://example.com"
    assert rect.xml_lang == "en"
    assert rect.xml_space == "preserve"


def test_attribute_normalization_serialize() -> None:
    rect = svglab.Rect(
        stroke_dasharray=[
            svglab.Length(1),
            svglab.Length(2),
            svglab.Length(3),
        ],
        stroke_dashoffset=svglab.Length(1),
        stroke_linecap="round",
        stroke_linejoin="round",
        stroke_width=svglab.Length(1),
        stroke_opacity=0.9,
        xml_base="http://example.com",
        xml_lang="en",
        xml_space="preserve",
    )

    attrs = {
        "stroke-dasharray": [
            {"value": 1.0},
            {"value": 2.0},
            {"value": 3.0},
        ],
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
    "element", [svglab.RawText, svglab.Comment, svglab.CData]
)
def test_text_elements_min_str_length_invalid(
    element: type[svglab.RawText | svglab.Comment | svglab.CData],
) -> None:
    with pytest.raises(pydantic.ValidationError):
        element("")


@hypothesis.given(st.text(min_size=1))
def test_text_elements_min_str_length_valid(test: str) -> None:
    svglab.RawText(test)
    svglab.Comment(test)
    svglab.CData(test)


@hypothesis.given(st.text(min_size=1))
def test_eq_text(text: str) -> None:
    assert svglab.RawText(text) == svglab.RawText(text)
    assert svglab.Comment(text) == svglab.Comment(text)
    assert svglab.CData(text) == svglab.CData(text)

    assert svglab.RawText(text) != svglab.Comment(text)
    assert svglab.RawText(text) != svglab.CData(text)
    assert svglab.Comment(text) != svglab.CData(text)


def test_eq_tag_simple() -> None:
    assert svglab.Rect() == svglab.Rect()
    assert svglab.Rect() != svglab.Circle()

    stroke_width = svglab.Length(1, "px")

    assert svglab.Rect(stroke_width=stroke_width) == svglab.Rect(
        stroke_width=stroke_width
    )
    assert svglab.Rect(stroke_width=stroke_width) != svglab.Rect()
    assert svglab.Rect(stroke_width=stroke_width) != svglab.Rect(
        stroke_width=svglab.Length(2, "px")
    )
    assert svglab.Rect(stroke_width=stroke_width) != svglab.Circle(
        stroke_width=stroke_width
    )

    assert svglab.Rect(stroke_width=stroke_width) != svglab.Rect(
        stroke_width=stroke_width, stroke="red"
    )


def test_eq_tag_group() -> None:
    assert svglab.G().add_child(svglab.Rect()) == svglab.G().add_child(
        svglab.Rect()
    )


@hypothesis.given(st.text())
def test_eq_tag_prefix(prefix: str) -> None:
    assert svglab.Rect(prefix=prefix) == svglab.Rect(prefix=prefix)


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("", svglab.D()),
        ("M 10,10", svglab.D().move_to(svglab.Point(10, 10))),
        (
            "M0,0L 10,10",
            svglab.D()
            .move_to(svglab.Point(0, 0))
            .line_to(svglab.Point(10, 10)),
        ),
        (
            "M0,0H 10",
            svglab.D().move_to(svglab.Point(0, 0)).horizontal_line_to(10),
        ),
        (
            "M0,0V 10",
            svglab.D().move_to(svglab.Point(0, 0)).vertical_line_to(10),
        ),
        (
            # https://github.com/mathandy/svgpathtools/issues/185
            "M12 22a10 10 0 110-20 10 10 0 010 20z",
            svglab.D()
            .move_to(svglab.Point(12, 22))
            .arc_to(
                svglab.Point(10, 10),
                0,
                svglab.Point(12, 2),
                large=True,
                sweep=True,
            )
            .arc_to(
                svglab.Point(10, 10),
                0,
                svglab.Point(12, 22),
                large=False,
                sweep=True,
            )
            .close(),
        ),
        (
            "M1 1 2 2 3 3 4 4",
            svglab.D()
            .move_to(svglab.Point(1, 1))
            .line_to(svglab.Point(2, 2))
            .line_to(svglab.Point(3, 3))
            .line_to(svglab.Point(4, 4)),
        ),
        (
            "M0,0C 10,10 20,20 30,30S 40,40 50,50Q 60,60 70,70T 80,80A 90,90 0"
            " 1 0 100,100T 110,110ZH 120V 130L 140,140Z",
            svglab.D()
            .move_to(svglab.Point(0, 0))
            .cubic_bezier_to(
                svglab.Point(10, 10),
                svglab.Point(20, 20),
                svglab.Point(30, 30),
            )
            .smooth_cubic_bezier_to(
                svglab.Point(40, 40), svglab.Point(50, 50)
            )
            .quadratic_bezier_to(
                svglab.Point(60, 60), svglab.Point(70, 70)
            )
            .smooth_quadratic_bezier_to(svglab.Point(80, 80))
            .arc_to(
                svglab.Point(90, 90),
                0,
                svglab.Point(100, 100),
                large=True,
                sweep=False,
            )
            .smooth_quadratic_bezier_to(svglab.Point(110, 110))
            .close()
            .horizontal_line_to(120)
            .vertical_line_to(130)
            .line_to(svglab.Point(140, 140))
            .close(),
        ),
    ],
)
def test_path_data_parse(text: str, expected: str) -> None:
    assert svglab.D.from_str(text) == expected


def test_path_data_parse_moveto_must_be_first() -> None:
    with pytest.raises(
        ValueError, match="Failed to parse text with grammar 'd.lark'"
    ):
        svglab.D.from_str("L 10,10")


SHORTHAND_TESTS: Final[list[tuple[svglab.D, svglab.D]]] = [
    (svglab.D(), svglab.D()),
    (
        svglab.D().move_to(svglab.Point(10, 10)),
        svglab.D().move_to(svglab.Point(10, 10)),
    ),
    (
        svglab.D()
        .move_to(svglab.Point.zero())
        .line_to(svglab.Point(0, 10)),
        svglab.D().move_to(svglab.Point.zero()).vertical_line_to(10),
    ),
    (
        svglab.D()
        .move_to(svglab.Point.zero())
        .line_to(svglab.Point(10, 0)),
        svglab.D().move_to(svglab.Point.zero()).horizontal_line_to(10),
    ),
    (
        svglab.D()
        .move_to(svglab.Point.zero())
        .quadratic_bezier_to(svglab.Point(20, 0), svglab.Point(20, 20))
        .quadratic_bezier_to(svglab.Point(20, 40), svglab.Point(40, 40)),
        svglab.D()
        .move_to(svglab.Point.zero())
        .quadratic_bezier_to(svglab.Point(20, 0), svglab.Point(20, 20))
        .smooth_quadratic_bezier_to(svglab.Point(40, 40)),
    ),
    (
        svglab.D()
        .move_to(svglab.Point.zero())
        .cubic_bezier_to(
            svglab.Point(20, 0), svglab.Point(40, 0), svglab.Point(40, 20)
        )
        .cubic_bezier_to(
            svglab.Point(40, 40),
            svglab.Point(20, 40),
            svglab.Point(20, 20),
        ),
        svglab.D()
        .move_to(svglab.Point.zero())
        .cubic_bezier_to(
            svglab.Point(20, 0), svglab.Point(40, 0), svglab.Point(40, 20)
        )
        .smooth_cubic_bezier_to(
            svglab.Point(20, 40), svglab.Point(20, 20)
        ),
    ),
]


@pytest.mark.parametrize(("before", "after"), SHORTHAND_TESTS)
def test_path_data_apply_shorthands(
    before: svglab.D, after: svglab.D
) -> None:
    assert before.apply_shorthands() == after


@pytest.mark.parametrize(("after", "before"), SHORTHAND_TESTS)
def test_path_data_resolve_shorthands(
    after: svglab.D, before: svglab.D
) -> None:
    assert before.resolve_shorthands() == after


@pytest.mark.parametrize(("before", "after"), SHORTHAND_TESTS)
def test_path_data_shorthands_cancel(
    before: svglab.D, after: svglab.D
) -> None:
    assert before.apply_shorthands().resolve_shorthands() == before
    assert after.resolve_shorthands().apply_shorthands() == after


@pytest.mark.parametrize(("before", "after"), SHORTHAND_TESTS)
def test_path_data_shorthands_idempotent(
    before: svglab.D, after: svglab.D
) -> None:
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
        ("m 1e+02 1e-02", "M100,.01"),
        (
            "M12 22a10 10 0 110-20 10 10 0 010 20z",
            "M12,22 A10,10 0 1 1 12,2 10,10 0 0 1 12,22 Z",
        ),
        (
            "m10,10 h100 v100 l10,10 10,10 z",
            "M10,10 H110 V110 L120,120 130,130 Z",
        ),
    ],
)
def test_path_data_parse_serialize(text: str, expected: str) -> None:
    assert svglab.D.from_str(text).serialize() == expected


def test_path_data_first_command_is_move_to() -> None:
    with pytest.raises(svglab.SvgPathMissingMoveToError):
        svglab.D().line_to(svglab.Point(0, 0))

    path = (
        svglab.D().move_to(svglab.Point(0, 0)).line_to(svglab.Point(0, 0))
    )
    line_to = path[1]

    with pytest.raises(svglab.SvgPathMissingMoveToError):
        del path[0]

    with pytest.raises(svglab.SvgPathMissingMoveToError):
        path[0] = line_to

    with pytest.raises(svglab.SvgPathMissingMoveToError):
        svglab.D().insert(0, line_to)

    with pytest.raises(svglab.SvgPathMissingMoveToError):
        svglab.D().append(line_to)


@pytest.mark.parametrize(
    ("transforms", "before", "after"),
    [
        ([svglab.Translate(1, 2)], svglab.Point(1, 2), svglab.Point(2, 4)),
        ([svglab.Scale(2)], svglab.Point(1, 2), svglab.Point(2, 4)),
        (
            [svglab.Rotate(45, 1, 1)],
            svglab.Point(1, 1),
            svglab.Point(1, 1),
        ),
        (
            [svglab.Rotate(90, 2, 2)],
            svglab.Point(1, 1),
            svglab.Point(3, 1),
        ),
        ([svglab.Rotate(90)], svglab.Point(1, 2), svglab.Point(-2, 1)),
        ([svglab.SkewX(45)], svglab.Point(1, 2), svglab.Point(3, 2)),
        ([svglab.SkewY(45)], svglab.Point(1, 2), svglab.Point(1, 3)),
    ],
)
def test_matrix_multiplication(
    transforms: svglab.Transform, before: svglab.Point, after: svglab.Point
) -> None:
    transformed = svglab.compose(transforms) @ before

    assert transformed == after


_TRANSFORMS: Final[list[svglab.Transform]] = [
    [svglab.Translate(10, 20)],
    [svglab.Translate(1, 5), svglab.Scale(0.5)],
    [svglab.Translate(2, 1)] * 10,
    [svglab.Scale(1.01)] * 10,
    [
        svglab.Scale(0.5),
        svglab.Translate(5, 0),
        svglab.Scale(1.5),
        svglab.Translate(-10, -10),
        svglab.Scale(0.75),
        svglab.Translate(0, 10),
    ],
    [svglab.Scale(1), svglab.Translate(0)],
]

_REIFY_SVGS: Final[list[svglab.Svg]] = [
    conftest.complex_svg(),
    conftest.nested_svg(),
    svglab.Svg(
        width=svglab.Length(1000), height=svglab.Length(1000)
    ).add_child(
        svglab.Rect(
            x=svglab.Length(200),
            y=svglab.Length(200),
            width=svglab.Length(100),
            height=svglab.Length(100),
            stroke_width=svglab.Length(1),
            fill="red",
            stroke="blue",
        )
    ),
    svglab.Svg(
        width=svglab.Length(1000), height=svglab.Length(1000)
    ).add_child(
        svglab.Rect(
            x=svglab.Length(200),
            y=svglab.Length(200),
            width=svglab.Length(100),
            height=svglab.Length(100),
            stroke_width=svglab.Length(1),
            fill="red",
            stroke="blue",
            transform=[svglab.Translate(10, 20), svglab.Scale(2)],
        )
    ),
    svglab.Svg(
        width=svglab.Length(1000), height=svglab.Length(1000)
    ).add_child(
        svglab.Rect(
            x=svglab.Length(200),
            y=svglab.Length(200),
            width=svglab.Length(100),
            height=svglab.Length(100),
            fill="red",
            stroke="blue",
            transform=[
                svglab.Translate(10, 20),
                svglab.Scale(2),
                svglab.Rotate(45),
                svglab.Translate(250, -300),
                svglab.SkewX(-45),
                svglab.SkewY(-20),
            ],
        )
    ),
    svglab.Svg(
        width=svglab.Length(1000), height=svglab.Length(1000)
    ).add_child(
        svglab.Rect(
            width=svglab.Length(100),
            height=svglab.Length(100),
            fill="red",
            stroke="blue",
        )
    ),
    svglab.Svg(
        width=svglab.Length(1000), height=svglab.Length(1000)
    ).add_child(
        svglab.Path(
            d=svglab.D()
            .move_to(svglab.Point(100, 100))
            .line_to(svglab.Point(200, 200))
            .cubic_bezier_to(
                svglab.Point(300, 200),
                svglab.Point(400, 300),
                svglab.Point(500, 300),
            ),
            stroke="blue",
            fill="red",
            transform=[svglab.SkewX(30)],
        )
    ),
    svglab.Svg(
        width=svglab.Length(1000), height=svglab.Length(1000)
    ).add_child(
        svglab.G(transform=[svglab.Translate(100, 700)]).add_children(
            svglab.Circle(
                cx=svglab.Length(50),
                cy=svglab.Length(50),
                r=svglab.Length(30),
                stroke="black",
            ),
            svglab.Circle(
                cx=svglab.Length(150),
                cy=svglab.Length(50),
                r=svglab.Length(30),
                stroke="black",
            ),
            svglab.Line(
                x1=svglab.Length(50),
                y1=svglab.Length(50),
                x2=svglab.Length(150),
                y2=svglab.Length(50),
                stroke="black",
            ),
        )
    ),
]


@pytest.mark.parametrize("transform", _TRANSFORMS)
def test_reify_leaves_transform_empty(transform: svglab.Transform) -> None:
    svg = svglab.Svg(transform=transform)
    svg.reify()

    assert svg.transform is None


@pytest.mark.parametrize("transform", _TRANSFORMS)
def test_reify_produces_visually_equal_svg_simple(
    transform: svglab.Transform,
) -> None:
    original = svglab.Svg(
        width=svglab.Length(1000), height=svglab.Length(1000)
    ).add_child(
        svglab.Rect(
            x=svglab.Length(200),
            y=svglab.Length(200),
            width=svglab.Length(100),
            height=svglab.Length(100),
            fill="red",
            transform=transform,
        )
    )

    reified = copy.deepcopy(original)
    reified.reify()

    conftest.assert_svg_visually_equal(original, reified)


@pytest.mark.parametrize("svg", _REIFY_SVGS)
def test_reify_produces_visually_equal_svg_complex(
    svg: svglab.Svg,
) -> None:
    reified = copy.deepcopy(svg)
    reified.reify()

    conftest.assert_svg_visually_equal(svg, reified)


def test_set_viewbox_sets_viewbox_attr() -> None:
    viewbox = (0, 0, 100, 100)

    svg = svglab.Svg(
        width=svglab.Length(25), height=svglab.Length(value=25)
    )
    svg.set_viewbox(viewbox)

    assert svg.viewBox == viewbox


@pytest.mark.parametrize(
    "svg",
    [
        *_REIFY_SVGS,
        pytest.param(
            svglab.Svg(
                width=svglab.Length(1000),
                height=svglab.Length(1000),
                transform=[svglab.Scale(0.5)],
            ).add_child(
                svglab.G().add_children(
                    svglab.Circle(
                        cx=svglab.Length(50),
                        cy=svglab.Length(50),
                        r=svglab.Length(30),
                        stroke="black",
                    ),
                    svglab.Circle(
                        cx=svglab.Length(150),
                        cy=svglab.Length(50),
                        r=svglab.Length(30),
                        stroke="black",
                    ),
                    svglab.Line(
                        x1=svglab.Length(50),
                        y1=svglab.Length(50),
                        x2=svglab.Length(150),
                        y2=svglab.Length(50),
                        stroke="black",
                    ),
                )
            ),
            marks=pytest.mark.xfail(
                reason="Transform/viewBox bug in resvg"
            ),
        ),
    ],
)
def test_set_viewbox_produces_visually_equal_svg(svg: svglab.Svg) -> None:
    transformed = copy.deepcopy(svg)
    transformed.set_viewbox((5, 5, 100, 100))

    conftest.assert_svg_visually_equal(svg, transformed)


@pytest.mark.parametrize(
    ("original", "swapped"),
    [
        # transforms of same type
        (
            (svglab.Translate(1, 2), svglab.Translate(2, 1)),
            (svglab.Translate(2, 1), svglab.Translate(1, 2)),
        ),
        (
            (svglab.Scale(2), svglab.Scale(0.5)),
            (svglab.Scale(0.5), svglab.Scale(2)),
        ),
        # isotropic scaling and translation
        (
            (svglab.Scale(2), svglab.Translate(1, 2)),
            (svglab.Translate(2, 4), svglab.Scale(2)),
        ),
        # skew and translation
        (
            (svglab.SkewX(45), svglab.Translate(10, 20)),
            (svglab.Translate(10 + 20, 20), svglab.SkewX(45)),
        ),
        # skew and isotropic scaling
        (
            (svglab.SkewX(45), svglab.Scale(2)),
            (svglab.Scale(2), svglab.SkewX(45)),
        ),
        # skew and anisotropic scaling
        (
            (svglab.SkewX(45), svglab.Scale(2, 3)),
            (svglab.Scale(2, 3), svglab.SkewX(56.30993247402021308647)),
        ),
    ],
)
def test_transform_swap(
    original: tuple[svglab.TransformFunction, svglab.TransformFunction],
    swapped: tuple[svglab.TransformFunction, svglab.TransformFunction],
) -> None:
    a, b = original
    c, d = swapped

    assert svglab.swap_transforms(a, b) == swapped
    assert svglab.swap_transforms(c, d) == original


@pytest.mark.parametrize(
    "transform",
    [
        *_TRANSFORMS,
        [
            svglab.Scale(2),
            svglab.Translate(1, 2),
            svglab.Rotate(15),
            svglab.Rotate(30),
            svglab.Translate(2, 4),
            svglab.Rotate(10, 15, 30),
        ],
        [svglab.SkewX(45), svglab.SkewY(45)],
        [svglab.Scale(0)],
        [svglab.Rotate(45, 10, 10)],
        [
            svglab.Scale(1, 2),
            svglab.Translate(1, 2),
            svglab.Scale(2, 1),
            svglab.Rotate(10),
            svglab.Scale(0.5),
        ],
        [svglab.SkewX(30)],
        [svglab.SkewY(30)],
    ],
)
def test_composed_decompose_equals_compose(
    transform: svglab.Transform,
) -> None:
    matrix = svglab.compose(transform)
    decomposed = matrix.decompose()

    assert svglab.compose(decomposed) == matrix, (
        f"{list(decomposed)=}, {matrix=}"
    )


@pytest.mark.parametrize(
    "transform",
    [
        [svglab.Translate(1, 2)],
        [svglab.Scale(2)],
        [svglab.Rotate(50)],
        [svglab.SkewX(-10)],
        [svglab.SkewY(15)],
    ],
)
def test_decompose_simple(transform: svglab.Transform) -> None:
    assert list(svglab.compose(transform).decompose()) == transform
