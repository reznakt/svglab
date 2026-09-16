import base64
import copy
import importlib.util
import inspect
import io
import pathlib
import types
from collections.abc import Callable

import hypothesis
import hypothesis.strategies as st
import pydantic
import pytest
from typing_extensions import Final, Literal, Protocol

import svglab
from svglab import (
    ArcTo,
    CData,
    Circle,
    ClosePath,
    Color,
    Comment,
    Element,
    Ellipse,
    Entity,
    FloatPrecisionSettings,
    Formatter,
    G,
    Iri,
    Length,
    LengthUnit,
    Line,
    LinearGradient,
    LineTo,
    Matrix,
    Path,
    PathCommand,
    PathData,
    Point,
    Polygon,
    Polyline,
    PrecisionInterval,
    RawText,
    Rect,
    Rotate,
    Scale,
    SkewX,
    SkewY,
    Svg,
    SvgElementNotFoundError,
    SvgPathMissingMoveToError,
    Transform,
    Translate,
    UnknownElement,
    compose,
    parse_svg,
)
from svglab.elements import elements, traits
from svglab.elements.names import ELEMENT_NAME_TO_NORMALIZED
from svglab.entities import element_name as get_element_name
from tests.conftest import (
    ASSETS_DIR,
    assert_svg_visually_equal,
    complex_svg,
    nested_svg,
)


class _SupportsSerialize(Protocol):
    def serialize(self) -> str: ...


numbers: Final = st.floats(allow_nan=False, allow_infinity=False)
MarkupInput = str | bytes | io.StringIO | io.BytesIO
ShapeWithPath = Circle | Ellipse | Line | Polygon | Polyline | Rect


def _to_bytes_buffer(xml: str) -> io.BytesIO:
    return io.BytesIO(xml.encode())


@hypothesis.given(numbers)
def test_valid_length(value: float) -> None:
    units: list[LengthUnit | None] = [
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
        svg = parse_svg(xml)

        assert isinstance(svg, Svg)

        rect = next(iter(svg.children))
        assert isinstance(rect, Rect)

        assert rect.width == Length(value, unit)


@pytest.mark.parametrize("value", ["", "foo", "px", "1.2."])
def test_invalid_length(value: str) -> None:
    xml = f"<svg><rect width='{value}'/></svg>"

    with pytest.raises(
        ValueError,
        match=r"Failed to parse text with grammar 'length.lark'",
    ):
        parse_svg(xml)


@pytest.mark.parametrize(
    "factory", [str, str.encode, io.StringIO, _to_bytes_buffer]
)
def test_parse_svg_accepts_multiple_input_types(
    factory: Callable[[str], MarkupInput], tmp_path: pathlib.Path
) -> None:
    svg = complex_svg()
    xml = svg.to_xml(pretty=False)
    baseline = parse_svg(xml)

    path = tmp_path / "input.svg"
    path.write_text(xml)

    assert parse_svg(factory(xml)) == baseline
    assert parse_svg(path) == baseline


def test_parse_svg_html_parser_finds_wrapped_fragment() -> None:
    svg = parse_svg(
        "<html><body><svg><rect width='10'/></svg></body></html>",
        parser="html.parser",
    )

    assert isinstance(svg.find(Rect), Rect)


@pytest.mark.parametrize(
    ("markup", "count"),
    [
        ("<html><body><p>no svg here</p></body></html>", 0),
        ("<div><svg/><svg/></div>", 2),
    ],
)
def test_parse_svg_requires_exactly_one_svg(
    markup: str, count: int
) -> None:
    with pytest.raises(
        ValueError, match=rf"Expected one <svg> element, found {count}"
    ):
        parse_svg(markup, parser="html.parser")


@pytest.mark.skipif(
    importlib.util.find_spec("html5lib") is not None,
    reason="the html5lib extra is installed",
)
def test_parse_svg_html5lib_without_extra() -> None:
    with pytest.raises(ImportError, match=r"svglab\[html5lib\]"):
        parse_svg("<svg/>", parser="html5lib")


def test_parse_svg_unknown_element_roundtrip() -> None:
    xml = "<svg><custom-element data-extra='value'/></svg>"

    svg = parse_svg(xml)
    unknown = svg.find(UnknownElement)

    assert unknown.element_name == "custom-element"
    assert unknown.extra_attrs() == {"data-extra": "value"}
    assert parse_svg(svg.to_xml(pretty=False)) == svg


@pytest.mark.parametrize(
    "markup",
    [
        "<not-svg>abcdefghijklmnopqrstuvwxyz0123456789</not-svg>",
        b"<not-svg>abcdefghijklmnopqrstuvwxyz0123456789</not-svg>",
        io.StringIO(
            "<not-svg>abcdefghijklmnopqrstuvwxyz0123456789</not-svg>"
        ),
        io.BytesIO(
            b"<not-svg>abcdefghijklmnopqrstuvwxyz0123456789</not-svg>"
        ),
    ],
    ids=["str", "bytes", "text-stream", "binary-stream"],
)
def test_parse_svg_error_message_truncates_markup_head(
    markup: str | bytes | io.StringIO | io.BytesIO,
) -> None:
    with pytest.raises(ValueError, match=r"markup: .+\.\.\."):
        parse_svg(markup, parser="html.parser")


def test_parse_svg_path_error_message_truncates_markup_head(
    tmp_path: pathlib.Path,
) -> None:
    markup = "<not-svg>abcdefghijklmnopqrstuvwxyz0123456789</not-svg>"
    path = tmp_path / "markup.txt"
    path.write_text(markup)

    with pytest.raises(ValueError, match=r"markup: .+\.\.\."):
        parse_svg(path, parser="html.parser")


def util_test_transform(text: str, parsed: Transform) -> None:
    xml = f"<svg><rect transform='{text}'/></svg>"
    svg = parse_svg(xml)

    assert isinstance(svg, Svg)

    rect = next(iter(svg.children))
    assert isinstance(rect, Rect)

    assert rect.transform == parsed


@hypothesis.given(numbers, st.one_of(numbers, st.none()))
def test_valid_scale(x: float, y: float | None) -> None:
    util_test_transform(
        f"scale({x}, {y})" if y is not None else f"scale({x})",
        [Scale(x) if y is None else Scale(x, y)],
    )


@hypothesis.given(numbers, st.one_of(numbers, st.none()))
def test_valid_translate(x: float, y: float | None) -> None:
    util_test_transform(
        f"translate({x}, {y})" if y is not None else f"translate({x})",
        [Translate(x) if y is None else Translate(x, y)],
    )


@hypothesis.given(numbers)
def test_valid_rotate(angle: float) -> None:
    util_test_transform(f"rotate({angle})", [Rotate(angle)])


@hypothesis.given(numbers)
def test_valid_skew_x(angle: float) -> None:
    util_test_transform(f"skewX({angle})", [SkewX(angle)])


@hypothesis.given(numbers)
def test_valid_skew_y(angle: float) -> None:
    util_test_transform(f"skewY({angle})", [SkewY(angle)])


@hypothesis.given(numbers, numbers, numbers, numbers, numbers, numbers)
def test_valid_matrix(
    a: float, b: float, c: float, d: float, e: float, f: float
) -> None:
    util_test_transform(
        f"matrix({a}, {b}, {c}, {d}, {e}, {f})", [Matrix(a, b, c, d, e, f)]
    )


def test_valid_transform_sequence() -> None:
    transforms = {
        "scale(1.5, 2)": Scale(1.5, 2),
        "scale(1.5)": Scale(1.5),
        "translate(1, 2)": Translate(1, 2),
        "translate(.1)": Translate(0.1),
        "rotate(45)": Rotate(45),
        "rotate(45, 1, 2.)": Rotate(45, 1, 2.0),
        "skewX(45)": SkewX(45),
        "skewY(45)": SkewY(45),
        "matrix(1, 0, 0, 1, 0, 0)": Matrix(1, 0, 0, 1, 0, 0),
        "skewX(1e+04)": SkewX(1e4),
        "skewX(1e-04)": SkewX(1e-4),
    }

    for sep in ",", " ":
        transform_text = sep.join(transforms.keys())
        util_test_transform(transform_text, list(transforms.values()))


@pytest.mark.parametrize(
    "text",
    [
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
        match=r"Failed to parse text with grammar 'transform.lark'",
    ):
        parse_svg(f"<svg><rect transform='{text}'/></svg>")


def test_attribute_normalization_native() -> None:
    rect = Rect(
        stroke_dasharray=[Length(1), Length(2), Length(3)],
        stroke_dashoffset=Length(1),
        stroke_linecap="round",
        stroke_linejoin="round",
        stroke_width=Length(1),
        stroke_opacity=0.9,
        xml_base=Iri(scheme="https", authority="example.com"),
        xml_lang="en",
        xml_space="preserve",
    )

    assert rect.extra_attrs() == {}

    assert rect.stroke_dasharray == [Length(1), Length(2), Length(3)]
    assert rect.stroke_dashoffset == Length(1)
    assert rect.stroke_linecap == "round"
    assert rect.stroke_linejoin == "round"
    assert rect.stroke_width == Length(1)
    assert rect.stroke_opacity == 0.9
    assert rect.xml_base == Iri(scheme="https", authority="example.com")
    assert rect.xml_lang == "en"
    assert rect.xml_space == "preserve"


def test_attribute_normalization_validate() -> None:
    rect = Rect.model_validate(
        {
            "stroke-dasharray": "1 2 3",
            "stroke-dashoffset": Length(1),
            "stroke-linecap": "round",
            "stroke-linejoin": "round",
            "stroke-width": Length(1),
            "stroke-opacity": 0.9,
            "xml:base": "http://example.com",
            "xml:lang": "en",
            "xml:space": "preserve",
        }
    )

    assert rect.extra_attrs() == {}

    assert rect.stroke_dasharray == [Length(1), Length(2), Length(3)]
    assert rect.stroke_dashoffset == Length(1)
    assert rect.stroke_linecap == "round"
    assert rect.stroke_linejoin == "round"
    assert rect.stroke_width == Length(1)
    assert rect.stroke_opacity == 0.9
    assert rect.xml_base == Iri(scheme="http", authority="example.com")
    assert rect.xml_lang == "en"
    assert rect.xml_space == "preserve"


def test_attribute_normalization_serialize() -> None:
    rect = Rect(
        stroke_dasharray=[Length(1), Length(2), Length(3)],
        stroke_dashoffset=Length(1),
        stroke_linecap="round",
        stroke_linejoin="round",
        stroke_width=Length(1),
        stroke_opacity=0.9,
        xml_base=Iri(scheme="https", authority="example.com"),
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
        "xml:base": {"authority": "example.com", "scheme": "https"},
        "xml:lang": "en",
        "xml:space": "preserve",
    }

    dump = rect.model_dump(by_alias=True, exclude_none=True)

    assert dump == attrs


def test_svg_save_roundtrip_path_and_file(tmp_path: pathlib.Path) -> None:
    svg = nested_svg()
    path = tmp_path / "saved.svg"

    svg.save(path, pretty=False)
    assert path.read_text().endswith("\n")

    buffer = io.StringIO()
    svg.save(buffer, pretty=False, trailing_newline=False)

    assert not buffer.getvalue().endswith("\n")
    assert parse_svg(path) == parse_svg(buffer.getvalue())


def test_svg_to_data_uri_roundtrip() -> None:
    svg = complex_svg()

    data_uri = svg.to_data_uri()
    prefix = "data:image/svg+xml;base64,"

    assert data_uri.startswith(prefix)

    decoded = base64.b64decode(data_uri.removeprefix(prefix)).decode()

    assert parse_svg(decoded).to_data_uri() == data_uri


@pytest.mark.parametrize(
    ("shape", "expected_num_commands", "last_command_type"),
    [
        pytest.param(
            Circle(
                cx=Length(40),
                cy=Length(50),
                r=Length(20),
                fill=Color("red"),
                stroke=Color("black"),
            ),
            3,
            ArcTo,
            id="circle",
        ),
        pytest.param(
            Ellipse(
                cx=Length(60),
                cy=Length(45),
                rx=Length(30),
                ry=Length(10),
                fill=Color("green"),
                stroke=Color("black"),
            ),
            3,
            ArcTo,
            id="ellipse",
        ),
        pytest.param(
            Line(
                x1=Length(10),
                y1=Length(15),
                x2=Length(90),
                y2=Length(70),
                stroke=Color("blue"),
                stroke_width=Length(4),
            ),
            2,
            LineTo,
            id="line",
        ),
        pytest.param(
            Polygon(
                points=[
                    Point(10, 10),
                    Point(90, 10),
                    Point(75, 70),
                    Point(25, 70),
                ],
                fill=Color("yellow"),
                stroke=Color("black"),
            ),
            5,
            ClosePath,
            id="polygon",
        ),
        pytest.param(
            Polyline(
                points=[
                    Point(10, 50),
                    Point(30, 20),
                    Point(60, 60),
                    Point(90, 25),
                ],
                fill="none",
                stroke=Color("purple"),
                stroke_width=Length(3),
            ),
            4,
            LineTo,
            id="polyline",
        ),
        pytest.param(
            Rect(
                x=Length(20),
                y=Length(15),
                width=Length(60),
                height=Length(40),
                rx=Length(8),
                fill=Color("orange"),
                stroke=Color("black"),
            ),
            10,
            ClosePath,
            id="rect-rx-only",
        ),
        pytest.param(
            Rect(
                x=Length(15),
                y=Length(20),
                width=Length(70),
                height=Length(35),
                ry=Length(6),
                fill=Color("cyan"),
                stroke=Color("black"),
            ),
            10,
            ClosePath,
            id="rect-ry-only",
        ),
        pytest.param(
            Rect(
                x=Length(10),
                y=Length(10),
                width=Length(80),
                height=Length(50),
                rx=Length(12),
                ry=Length(4),
                fill=Color("pink"),
                stroke=Color("black"),
            ),
            10,
            ClosePath,
            id="rect-rx-ry",
        ),
    ],
)
def test_basic_shape_to_path_is_visually_equivalent(
    shape: ShapeWithPath,
    expected_num_commands: int,
    last_command_type: type[PathCommand],
) -> None:
    original = Svg(width=Length(100), height=Length(100)).add_child(
        copy.deepcopy(shape)
    )
    path = copy.deepcopy(shape).to_path()
    converted = Svg(width=Length(100), height=Length(100)).add_child(path)

    assert path.d is not None
    assert len(path.d) == expected_num_commands
    assert isinstance(path.d[-1], last_command_type)
    assert_svg_visually_equal(original, converted)


def test_shape_set_path_length_scales_non_percentage_attrs() -> None:
    path = Path(
        pathLength=100,
        stroke_dasharray=[Length(10), Length(5, "%")],
        stroke_dashoffset=Length(4),
    )

    path.set_path_length(250)

    assert path.pathLength == 250
    assert path.stroke_dasharray == [Length(25), Length(5, "%")]
    assert path.stroke_dashoffset == Length(10)


def test_shape_set_path_length_requires_positive_value() -> None:
    path = Path(pathLength=100)

    with pytest.raises(ValueError, match="Path length must be positive"):
        path.set_path_length(0)


def test_shape_set_path_length_requires_existing_path_length() -> None:
    path = Path()

    with pytest.raises(
        RuntimeError, match="Current pathLength must not be None"
    ):
        path.set_path_length(100)


@pytest.mark.parametrize("element", [RawText, Comment, CData])
def test_text_elements_min_str_length_invalid(
    element: type[RawText | Comment | CData],
) -> None:
    with pytest.raises(pydantic.ValidationError):
        element("")


@hypothesis.given(st.text(min_size=1))
def test_text_elements_min_str_length_valid(test: str) -> None:
    RawText(test)
    Comment(test)
    CData(test)


@hypothesis.given(st.text(min_size=1))
def test_eq_text(text: str) -> None:
    assert RawText(text) == RawText(text)
    assert Comment(text) == Comment(text)
    assert CData(text) == CData(text)

    assert RawText(text) != Comment(text)
    assert RawText(text) != CData(text)
    assert Comment(text) != CData(text)


def test_eq_element_simple() -> None:
    assert Rect() == Rect()
    assert Rect() != Circle()

    stroke_width = Length(1, "px")

    assert Rect(stroke_width=stroke_width) == Rect(
        stroke_width=stroke_width
    )
    assert Rect(stroke_width=stroke_width) != Rect()
    assert Rect(stroke_width=stroke_width) != Rect(
        stroke_width=Length(2, "px")
    )
    assert Rect(stroke_width=stroke_width) != Circle(
        stroke_width=stroke_width
    )

    assert Rect(stroke_width=stroke_width) != Rect(
        stroke_width=stroke_width, stroke=Color("red")
    )


def test_eq_element_group() -> None:
    assert G().add_child(Rect()) == G().add_child(Rect())


@hypothesis.given(st.text())
def test_eq_element_prefix(prefix: str) -> None:
    assert Rect(prefix=prefix) == Rect(prefix=prefix)


def test_tree_navigation_search_and_mutation() -> None:
    root = Svg()
    group = G(id="group")
    rect = Rect(id="rect")
    circle = Circle(id="circle")
    line = Line(id="line")

    root.add_child(group)
    group.add_children(rect, circle, line)

    assert list(circle.ancestors) == [group, root]
    assert list(circle.prev_siblings) == [rect]
    assert list(circle.next_siblings) == [line]
    assert list(circle.siblings) == [rect, line]
    assert circle.get_root() is root

    assert group.find("circle", recursive=False) is circle
    assert list(group.find_all(Circle, recursive=False)) == [circle]
    assert group.find("ellipse", default=None) is None

    with pytest.raises(SvgElementNotFoundError):
        group.find("ellipse")

    assert group.get_child_index(circle) == 1

    removed = group.remove_child(circle)

    assert removed is circle
    assert circle.parent is None

    with pytest.raises(ValueError, match="Child not found"):
        group.remove_child(circle)

    popped = group.pop_child(0)

    assert popped is rect
    assert rect.parent is None

    group.clear_children()

    assert not group.has_children()
    assert line.parent is None


def test_resolve_iri_and_reference_detection() -> None:
    gradient = LinearGradient(id="paint")
    rect = Rect(fill=gradient.get_func_iri())
    svg = Svg().add_children(gradient, rect)

    assert svg.resolve_iri(Iri(fragment="paint")) is gradient
    assert rect.references_other_element() is True

    rect.fill = Iri(fragment="missing").to_func_iri()

    with pytest.warns(UserWarning, match=r"Dangling IRI reference"):
        assert rect.references_other_element() is False

    with pytest.raises(ValueError, match="non-local IRI reference"):
        svg.resolve_iri(Iri(scheme="https", authority="example.com"))


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("", PathData()),
        ("M 10,10", PathData().move_to(Point(10, 10))),
        (
            "M0,0L 10,10",
            PathData().move_to(Point(0, 0)).line_to(Point(10, 10)),
        ),
        (
            "M0,0H 10",
            PathData().move_to(Point(0, 0)).horizontal_line_to(10),
        ),
        ("M0,0V 10", PathData().move_to(Point(0, 0)).vertical_line_to(10)),
        (
            # https://github.com/mathandy/svgpathtools/issues/185
            "M12 22a10 10 0 110-20 10 10 0 010 20z",
            PathData()
            .move_to(Point(12, 22))
            .arc_to(Point(10, 10), 0, Point(12, 2), large=True, sweep=True)
            .arc_to(
                Point(10, 10), 0, Point(12, 22), large=False, sweep=True
            )
            .close(),
        ),
        (
            "M1 1 2 2 3 3 4 4",
            PathData()
            .move_to(Point(1, 1))
            .line_to(Point(2, 2))
            .line_to(Point(3, 3))
            .line_to(Point(4, 4)),
        ),
        (
            (
                "M0,0C 10,10 20,20 30,30S 40,40 50,50Q 60,60 70,70T 80,80"
                "A 90,90 0 1 0 100,100T 110,110ZH 120V 130L 140,140Z"
            ),
            PathData()
            .move_to(Point(0, 0))
            .cubic_bezier_to(Point(10, 10), Point(20, 20), Point(30, 30))
            .smooth_cubic_bezier_to(Point(40, 40), Point(50, 50))
            .quadratic_bezier_to(Point(60, 60), Point(70, 70))
            .smooth_quadratic_bezier_to(Point(80, 80))
            .arc_to(
                Point(90, 90), 0, Point(100, 100), large=True, sweep=False
            )
            .smooth_quadratic_bezier_to(Point(110, 110))
            .close()
            .horizontal_line_to(120)
            .vertical_line_to(130)
            .line_to(Point(140, 140))
            .close(),
        ),
        (
            "M0,0 Z H100",  # no moveto after closepath
            PathData()
            .move_to(Point(0, 0))
            .close()
            .horizontal_line_to(100),
        ),
    ],
)
def test_path_data_parse(text: str, expected: str) -> None:
    assert PathData.from_str(text) == expected


def test_path_data_parse_moveto_must_be_first() -> None:
    with pytest.raises(
        ValueError,
        match=r"Failed to parse text with grammar 'path_data.lark'",
    ):
        PathData.from_str("L 10,10")


SHORTHAND_TESTS: Final = [
    (PathData(), PathData()),
    (PathData().move_to(Point(10, 10)), PathData().move_to(Point(10, 10))),
    (
        PathData().move_to(Point.zero()).line_to(Point(0, 10)),
        PathData().move_to(Point.zero()).vertical_line_to(10),
    ),
    (
        PathData().move_to(Point.zero()).line_to(Point(10, 0)),
        PathData().move_to(Point.zero()).horizontal_line_to(10),
    ),
    (
        PathData()
        .move_to(Point.zero())
        .quadratic_bezier_to(Point(20, 0), Point(20, 20))
        .quadratic_bezier_to(Point(20, 40), Point(40, 40)),
        PathData()
        .move_to(Point.zero())
        .quadratic_bezier_to(Point(20, 0), Point(20, 20))
        .smooth_quadratic_bezier_to(Point(40, 40)),
    ),
    (
        PathData()
        .move_to(Point.zero())
        .cubic_bezier_to(Point(20, 0), Point(40, 0), Point(40, 20))
        .cubic_bezier_to(Point(40, 40), Point(20, 40), Point(20, 20)),
        PathData()
        .move_to(Point.zero())
        .cubic_bezier_to(Point(20, 0), Point(40, 0), Point(40, 20))
        .smooth_cubic_bezier_to(Point(20, 40), Point(20, 20)),
    ),
]


@pytest.mark.parametrize(("before", "after"), SHORTHAND_TESTS)
def test_path_data_apply_shorthands(
    before: PathData, after: PathData
) -> None:
    assert before.apply_shorthands() == after


@pytest.mark.parametrize(("after", "before"), SHORTHAND_TESTS)
def test_path_data_resolve_shorthands(
    after: PathData, before: PathData
) -> None:
    assert before.resolve_shorthands() == after


@pytest.mark.parametrize(("before", "after"), SHORTHAND_TESTS)
def test_path_data_shorthands_cancel(
    before: PathData, after: PathData
) -> None:
    assert before.apply_shorthands().resolve_shorthands() == before
    assert after.resolve_shorthands().apply_shorthands() == after


@pytest.mark.parametrize(("before", "after"), SHORTHAND_TESTS)
def test_path_data_shorthands_idempotent(
    before: PathData, after: PathData
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
    assert PathData.from_str(text).serialize() == expected


def test_path_data_first_command_is_move_to() -> None:
    with pytest.raises(SvgPathMissingMoveToError):
        PathData().line_to(Point(0, 0))

    path = PathData().move_to(Point(0, 0)).line_to(Point(0, 0))
    line_to = path[1]

    with pytest.raises(SvgPathMissingMoveToError):
        del path[0]

    with pytest.raises(SvgPathMissingMoveToError):
        path[0] = line_to

    with pytest.raises(SvgPathMissingMoveToError):
        PathData().insert(0, line_to)

    with pytest.raises(SvgPathMissingMoveToError):
        PathData().append(line_to)


@pytest.mark.parametrize(
    ("transforms", "before", "after"),
    [
        ([Translate(1, 2)], Point(1, 2), Point(2, 4)),
        ([Scale(2)], Point(1, 2), Point(2, 4)),
        ([Rotate(45, 1, 1)], Point(1, 1), Point(1, 1)),
        ([Rotate(90, 2, 2)], Point(1, 1), Point(3, 1)),
        ([Rotate(90)], Point(1, 2), Point(-2, 1)),
        ([SkewX(45)], Point(1, 2), Point(3, 2)),
        ([SkewY(45)], Point(1, 2), Point(1, 3)),
    ],
)
def test_matrix_multiplication(
    transforms: Transform, before: Point, after: Point
) -> None:
    transformed = compose(transforms) @ before

    assert transformed == after


def test_render_preserves_aspect_ratio_for_single_dimension() -> None:
    svg = Svg(width=Length(100), height=Length(200)).add_child(
        Rect(width=Length(100), height=Length(200), fill=Color("red"))
    )

    assert svg.render(width=50).size == (50, 100)
    assert svg.render(height=50).size == (25, 50)


def test_render_requires_resolvable_dimensions() -> None:
    svg = Svg(width=Length(100, "%"), height=Length(100, "%")).add_child(
        Rect(width=Length(100), height=Length(100), fill=Color("red"))
    )

    with pytest.raises(
        ValueError, match="Unable to determine image dimensions"
    ):
        svg.render()


@hypothesis.given(
    st.integers(min_value=1, max_value=1000),
    st.integers(min_value=1, max_value=1000),
    st.integers(min_value=1, max_value=1000),
)
def test_render_preserves_aspect_ratio_with_both_dimensions(
    width: int, height: int, target_size: int
) -> None:
    svg = Svg(width=Length(width), height=Length(height)).add_child(
        Rect(width=Length(width), height=Length(height), fill=Color("red"))
    )

    (img_width, img_height) = svg.render(
        width=target_size, height=target_size
    ).size

    scale = target_size / max(width, height)

    # allow one pixel of rounding error on each axis
    assert img_width == pytest.approx(width * scale, abs=1)
    assert img_height == pytest.approx(height * scale, abs=1)


def test_bbox_matches_mask_bounds() -> None:
    svg = Svg(width=Length(40), height=Length(30)).add_child(
        Rect(
            x=Length(5),
            y=Length(6),
            width=Length(10),
            height=Length(8),
            fill=Color("black"),
        )
    )
    rect = svg.find(Rect)
    mask = rect.get_mask()
    rows, cols = mask.nonzero()

    expected = (
        int(cols.min()),
        int(rows.min()),
        int(cols.max()) + 1,
        int(rows.max()) + 1,
    )

    assert rect.get_bbox() == expected


def test_visible_only_mask_and_bbox_ignore_fully_transparent_geometry() -> (
    None
):
    svg = Svg(width=Length(40), height=Length(30)).add_child(
        Rect(
            x=Length(5),
            y=Length(6),
            width=Length(10),
            height=Length(8),
            fill=Color("black"),
            fill_opacity=0,
            stroke="none",
        )
    )
    rect = svg.find(Rect)

    assert rect.get_bbox() is not None
    assert rect.get_bbox(visible_only=True) is None
    assert rect.get_mask().any()
    assert not rect.get_mask(visible_only=True).any()


_TRANSFORMS: Final = [
    [Translate(10, 20)],
    [Translate(1, 5), Scale(0.5)],
    [Translate(2, 1)] * 10,
    [Scale(1.01)] * 10,
    [
        Scale(0.5),
        Translate(5, 0),
        Scale(1.5),
        Translate(-10, -10),
        Scale(0.75),
        Translate(0, 10),
    ],
    [Scale(1), Translate(0)],
]

_REIFY_SVGS: Final = [
    complex_svg(),
    nested_svg(),
    Svg(width=Length(1000), height=Length(1000)).add_child(
        Rect(
            x=Length(200),
            y=Length(200),
            width=Length(100),
            height=Length(100),
            stroke_width=Length(1),
            fill=Color("red"),
            stroke=Color("blue"),
        )
    ),
    Svg(width=Length(1000), height=Length(1000)).add_child(
        Rect(
            x=Length(200),
            y=Length(200),
            width=Length(100),
            height=Length(100),
            stroke_width=Length(1),
            fill=Color("red"),
            stroke=Color("blue"),
            transform=[Translate(10, 20), Scale(2)],
            transform_origin=(Length(5), Length(0)),
        )
    ),
    Svg(width=Length(1000), height=Length(1000)).add_child(
        Rect(
            x=Length(200),
            y=Length(200),
            width=Length(100),
            height=Length(100),
            fill=Color("red"),
            stroke=Color("blue"),
            transform_origin=(Length(10), Length(20)),
            transform=[
                Translate(10, 20),
                Scale(2),
                Rotate(45),
                Translate(250, -300),
                SkewX(-45),
                SkewY(-20),
            ],
        )
    ),
    Svg(width=Length(1000), height=Length(1000)).add_child(
        Rect(
            width=Length(100),
            height=Length(100),
            fill=Color("red"),
            stroke=Color("blue"),
        )
    ),
    Svg(width=Length(1000), height=Length(1000)).add_child(
        Path(
            d=PathData()
            .move_to(Point(100, 100))
            .line_to(Point(200, 200))
            .cubic_bezier_to(
                Point(300, 200), Point(400, 300), Point(500, 300)
            ),
            stroke=Color("blue"),
            fill=Color("red"),
            transform=[SkewX(30)],
        )
    ),
    Svg(width=Length(1000), height=Length(1000)).add_child(
        G(transform=[Translate(100, 700)]).add_children(
            Circle(
                cx=Length(50),
                cy=Length(50),
                r=Length(30),
                stroke=Color("black"),
            ),
            Circle(
                cx=Length(150),
                cy=Length(50),
                r=Length(30),
                stroke=Color("black"),
            ),
            Line(
                x1=Length(50),
                y1=Length(50),
                x2=Length(150),
                y2=Length(50),
                stroke=Color("black"),
            ),
        )
    ),
]


@pytest.mark.parametrize("transform", _TRANSFORMS)
def test_reify_leaves_transform_empty(transform: Transform) -> None:
    svg = Svg(transform=transform)
    svg.reify()

    assert svg.transform is None


@pytest.mark.parametrize("transform", _TRANSFORMS)
def test_reify_produces_visually_equal_svg_simple(
    transform: Transform,
) -> None:
    original = Svg(width=Length(1000), height=Length(1000)).add_child(
        Rect(
            x=Length(200),
            y=Length(200),
            width=Length(100),
            height=Length(100),
            fill=Color("red"),
            transform=transform,
        )
    )

    reified = copy.deepcopy(original)
    reified.reify()

    assert_svg_visually_equal(original, reified)


@pytest.mark.parametrize("svg", _REIFY_SVGS)
def test_reify_produces_visually_equal_svg_complex(svg: Svg) -> None:
    reified = copy.deepcopy(svg)
    reified.reify()

    assert_svg_visually_equal(svg, reified)


def test_set_viewbox_sets_viewbox_attr() -> None:
    viewbox = (0, 0, 100, 100)

    svg = Svg(width=Length(25), height=Length(value=25))
    svg.set_viewbox(viewbox)

    assert svg.viewBox == viewbox


@pytest.mark.parametrize(
    "svg",
    [
        *_REIFY_SVGS,
        pytest.param(
            Svg(
                width=Length(1000),
                height=Length(1000),
                transform=[Scale(0.5)],
            ).add_child(
                G().add_children(
                    Circle(
                        cx=Length(50),
                        cy=Length(50),
                        r=Length(30),
                        stroke=Color("black"),
                    ),
                    Circle(
                        cx=Length(150),
                        cy=Length(50),
                        r=Length(30),
                        stroke=Color("black"),
                    ),
                    Line(
                        x1=Length(50),
                        y1=Length(50),
                        x2=Length(150),
                        y2=Length(50),
                        stroke=Color("black"),
                    ),
                )
            ),
            marks=pytest.mark.xfail(
                reason="Transform/viewBox bug in resvg"
            ),
        ),
        Svg(width=Length(1000), height=Length(1000)).add_child(
            Rect(
                x=Length(200),
                y=Length(200),
                width=Length(100),
                height=Length(100),
                fill=Color("red"),
                stroke=Color("blue"),
                transform=[
                    compose(
                        [
                            Translate(10, 20),
                            Scale(2),
                            Rotate(45),
                            Translate(250, -300),
                            SkewX(-45),
                            SkewY(-20),
                        ]
                    )
                ],
            )
        ),
        Svg(
            width=Length(100),
            height=Length(100),
            viewBox=(50, 50, 200, 200),
        ).add_child(
            Rect(
                x=Length(100),
                y=Length(100),
                width=Length(50),
                height=Length(50),
                fill=Color("blue"),
            )
        ),
    ],
)
def test_set_viewbox_produces_visually_equal_svg(svg: Svg) -> None:
    transformed = copy.deepcopy(svg)
    transformed.set_viewbox((5, 5, 100, 100))

    assert_svg_visually_equal(svg, transformed)


@pytest.mark.parametrize(
    "transform",
    [
        *_TRANSFORMS,
        [
            Scale(2),
            Translate(1, 2),
            Rotate(15),
            Rotate(30),
            Translate(2, 4),
            Rotate(10, 15, 30),
        ],
        [SkewX(45), SkewY(45)],
        [Scale(0)],
        [Rotate(45, 10, 10)],
        [
            Scale(1, 2),
            Translate(1, 2),
            Scale(2, 1),
            Rotate(10),
            Scale(0.5),
        ],
        [SkewX(30)],
        [SkewY(30)],
    ],
)
def test_composed_decompose_equals_compose(transform: Transform) -> None:
    matrix = compose(transform)
    decomposed = matrix.decompose()

    assert compose(decomposed) == matrix, f"{list(decomposed)=}, {matrix=}"


@pytest.mark.parametrize(
    "transform",
    [
        [Translate(1, 2)],
        [Scale(2)],
        [Rotate(50)],
        [SkewX(-10)],
        [SkewY(15)],
        [Scale(0, 1)],
        [Scale(0)],
    ],
)
def test_decompose_simple(transform: Transform) -> None:
    assert compose(transform).decompose() == transform


def test_entity_substitution() -> None:
    assert RawText(">").to_xml() == "&gt;"


@pytest.mark.parametrize(
    ("value", "serialized"),
    [
        (Length(1.123456), "1"),
        (Rotate(1.123456), "rotate(1.1)"),
        (SkewX(1.123456), "skewX(1.1)"),
        (Translate(1.123456), "translate(1.123456)"),
        (Scale(1.123456), "scale(0)"),
    ],
)
def test_float_precision_settings(
    value: _SupportsSerialize, serialized: str
) -> None:
    formatter = Formatter(
        general_precision=10,
        angle_precision=1,
        coordinate_precision=0,
        scale_precision=-1,
    )

    with formatter:
        assert value.serialize() == serialized


@pytest.mark.parametrize(
    ("value", "serialized"),
    [
        (Length(0.123456), ".123"),
        (Rotate(1.123456), "rotate(1.12)"),
        (SkewX(10.123456), "skewX(10.1)"),
        (Translate(100.123456), "translate(100)"),
        (Scale(1000.123456), "scale(1000.123456)"),
    ],
)
def test_precision_table(
    value: _SupportsSerialize, serialized: str
) -> None:
    formatter = Formatter(
        general_precision=FloatPrecisionSettings(
            precision_table={
                PrecisionInterval(0, 1, 3),
                PrecisionInterval(1, 10, 2),
                PrecisionInterval(10, 100, 1),
                PrecisionInterval(100, 1000, 0),
            },
            fallback=15,
        )
    )

    with formatter:
        assert value.serialize() == serialized


def test_path_data_point_separator() -> None:
    svg = parse_svg(
        '<svg><path d="M1 2L3 4A5 6 0 0 1 7 8"/>'
        '<polygon points="1 2 3 4"/></svg>'
    )
    formatter = Formatter(
        point_separator=",",
        path_data_point_separator=" ",
        path_data_space_before_args=True,
        path_data_commands="explicit",
    )

    path = svg.find(Path).to_xml(formatter=formatter)
    polygon = svg.find(Polygon).to_xml(formatter=formatter)

    assert path == '<path d="M 1 2 L 3 4 A 5 6 0 0 1 7 8"/>'
    assert polygon == '<polygon points="1,2 3,4"/>'


@pytest.mark.parametrize(
    ("color_mode", "serialized"),
    [
        ("hex-long", "#FFAA00"),
        ("hex-short", "#FA0"),
        ("rgb", "rgb(255 170 0)"),
        ("original", "#ffaa00"),
    ],
)
def test_color_case(
    color_mode: Literal["hex-long", "hex-short", "rgb", "original"],
    serialized: str,
) -> None:
    formatter = Formatter(color_mode=color_mode, color_case="upper")

    with formatter:
        assert Color("#ffaa00").serialize() == serialized


def test_invalid_add_child_direct_circular_reference() -> None:
    g = G()

    with pytest.raises(
        ValueError, match=r"Cannot add an element as a child of itself."
    ):
        g.add_child(g)


def test_large_float_results_in_error() -> None:
    with pytest.raises(ValueError, match=r".*Value must be finite.*"):
        parse_svg("<svg><rect x='1e9999'/></svg>")


@pytest.mark.parametrize(
    ("a", "b"),
    [
        (Rect(), Rect()),
        (Rect(stroke_width=Length(1)), Rect(stroke_width=Length(1))),
        (G().add_child(Rect()), G().add_child(Rect())),
        (RawText("test"), RawText("test")),
        (Comment("test"), Comment("test")),
        (CData("test"), CData("test")),
        (
            Svg(width=Length(100), height=Length(100)).add_children(
                Rect(x=Length(10), y=Length(10))
            ),
            Svg(width=Length(100), height=Length(100)).add_children(
                Rect(x=Length(10), y=Length(10))
            ),
        ),
    ],
)
def test_hashes_equal(a: Entity, b: Entity) -> None:
    assert hash(a) == hash(b)


@pytest.mark.parametrize(
    ("a", "b"),
    [
        (Rect(), Circle()),
        (Rect(stroke_width=Length(1)), Rect()),
        (Rect(stroke_width=Length(1)), Rect(stroke_width=Length(2))),
        (Rect(stroke_width=Length(1)), Circle(stroke_width=Length(1))),
        (G().add_child(Rect()), G().add_child(Circle())),
        (RawText("test"), RawText("test2")),
        (RawText("test"), Comment("test")),
        (RawText("test"), CData("test")),
        (Comment("test"), Comment("test2")),
        (Comment("test"), CData("test")),
        (CData("test"), CData("test2")),
    ],
)
def test_hashes_unequal(a: Entity, b: Entity) -> None:
    assert hash(a) != hash(b)


def test_points_accepts_empty_list() -> None:
    svg = parse_svg("<svg><polyline points=''/></svg>")
    polyline = svg.find(Polyline)

    assert polyline.points == []


def test_transform_accepts_empty_list() -> None:
    svg = parse_svg("<svg><rect transform=''/></svg>")
    rect = svg.find(Rect)

    assert rect.transform == []


def test_path_data_accepts_empty_list() -> None:
    svg = parse_svg("<svg><path d=''/></svg>")
    path = svg.find(Path)

    assert path.d == PathData()


def test_closepath_ends_at_start_of_subpath() -> None:
    svg = Svg().add_child(Path(d=PathData.from_str("M10,10 L20,20 Z H30")))

    assert "h20" in svg.to_xml(
        formatter=Formatter(path_data_coordinates="relative")
    )


def test_parse_svg_with_path() -> None:
    path = ASSETS_DIR / "dummy.svg"

    parse_svg(path)


def _public_classes(module: types.ModuleType) -> set[str]:
    return {
        name
        for name, obj in vars(module).items()
        if inspect.isclass(obj)
        and not name.startswith("_")
        and obj.__module__ == module.__name__
    }


@pytest.mark.parametrize(
    "module", [elements, traits], ids=lambda module: module.__name__
)
def test_public_classes_are_exported(module: types.ModuleType) -> None:
    assert _public_classes(module) <= set(svglab.__all__)


def test_element_classes_match_element_names() -> None:
    assert _public_classes(elements) == set(
        ELEMENT_NAME_TO_NORMALIZED.values()
    )


@pytest.mark.parametrize(
    ("element_name", "class_name"),
    sorted(ELEMENT_NAME_TO_NORMALIZED.items()),
)
def test_every_element_is_exported(
    element_name: str, class_name: str
) -> None:
    assert class_name in svglab.__all__, element_name

    cls = getattr(svglab, class_name)

    assert issubclass(cls, Element)
    assert get_element_name(cls.model_construct()) == element_name


def test_all_is_importable() -> None:
    assert all(hasattr(svglab, name) for name in svglab.__all__)
