"""Tests for the svglab package."""

# ruff: noqa: D103

import base64
import copy
import io
import pathlib
from collections.abc import Callable

import hypothesis
import hypothesis.strategies as st
import pydantic
import pytest
from typing_extensions import Final, Protocol

import svglab
from tests import conftest


class _SupportsSerialize(Protocol):
    def serialize(self) -> str: ...


numbers: Final = st.floats(allow_nan=False, allow_infinity=False)
MarkupInput = str | bytes | io.StringIO | io.BytesIO
ShapeWithPath = (
    svglab.Circle
    | svglab.Ellipse
    | svglab.Line
    | svglab.Polygon
    | svglab.Polyline
    | svglab.Rect
)


def _to_bytes_buffer(xml: str) -> io.BytesIO:
    return io.BytesIO(xml.encode())


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
        ValueError,
        match=r"Failed to parse text with grammar 'length.lark'",
    ):
        svglab.parse_svg(xml)


@pytest.mark.parametrize(
    "factory", [str, str.encode, io.StringIO, _to_bytes_buffer]
)
def test_parse_svg_accepts_multiple_input_types(
    factory: Callable[[str], MarkupInput], tmp_path: pathlib.Path
) -> None:
    svg = conftest.complex_svg()
    xml = svg.to_xml(pretty=False)
    baseline = svglab.parse_svg(xml)

    path = tmp_path / "input.svg"
    path.write_text(xml)

    assert svglab.parse_svg(factory(xml)) == baseline
    assert svglab.parse_svg(path) == baseline


def test_parse_svg_html_parser_finds_wrapped_fragment() -> None:
    svg = svglab.parse_svg(
        "<html><body><svg><rect width='10'/></svg></body></html>",
        parser="html.parser",
    )

    assert isinstance(svg.find(svglab.Rect), svglab.Rect)


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
        svglab.parse_svg(markup, parser="html.parser")


def test_parse_svg_unknown_element_roundtrip() -> None:
    xml = "<svg><custom-element data-extra='value'/></svg>"

    svg = svglab.parse_svg(xml)
    unknown = svg.find(svglab.UnknownElement)

    assert unknown.element_name == "custom-element"
    assert unknown.extra_attrs() == {"data-extra": "value"}
    assert svglab.parse_svg(svg.to_xml(pretty=False)) == svg


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
)
def test_parse_svg_error_message_truncates_markup_head(
    markup: str | bytes | io.StringIO | io.BytesIO,
) -> None:
    with pytest.raises(ValueError, match=r"markup: .+\.\.\."):
        svglab.parse_svg(markup, parser="html.parser")


def test_parse_svg_path_error_message_truncates_markup_head(
    tmp_path: pathlib.Path,
) -> None:
    markup = "<not-svg>abcdefghijklmnopqrstuvwxyz0123456789</not-svg>"
    path = tmp_path / "markup.txt"
    path.write_text(markup)

    with pytest.raises(ValueError, match=r"markup: .+\.\.\."):
        svglab.parse_svg(path, parser="html.parser")


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
        xml_base=svglab.Iri(scheme="https", authority="example.com"),
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
    assert rect.xml_base == svglab.Iri(
        scheme="https", authority="example.com"
    )
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
    assert rect.xml_base == svglab.Iri(
        scheme="http", authority="example.com"
    )
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
        xml_base=svglab.Iri(scheme="https", authority="example.com"),
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
    svg = conftest.nested_svg()
    path = tmp_path / "saved.svg"

    svg.save(path, pretty=False)
    assert path.read_text().endswith("\n")

    buffer = io.StringIO()
    svg.save(buffer, pretty=False, trailing_newline=False)

    assert not buffer.getvalue().endswith("\n")
    assert svglab.parse_svg(path) == svglab.parse_svg(buffer.getvalue())


def test_svg_to_data_uri_roundtrip() -> None:
    svg = conftest.complex_svg()

    data_uri = svg.to_data_uri()
    prefix = "data:image/svg+xml;base64,"

    assert data_uri.startswith(prefix)

    decoded = base64.b64decode(data_uri.removeprefix(prefix)).decode()

    assert svglab.parse_svg(decoded).to_data_uri() == data_uri


@pytest.mark.parametrize(
    ("shape", "expected_num_commands", "last_command_type"),
    [
        pytest.param(
            svglab.Circle(
                cx=svglab.Length(40),
                cy=svglab.Length(50),
                r=svglab.Length(20),
                fill=svglab.Color("red"),
                stroke=svglab.Color("black"),
            ),
            3,
            svglab.ArcTo,
            id="circle",
        ),
        pytest.param(
            svglab.Ellipse(
                cx=svglab.Length(60),
                cy=svglab.Length(45),
                rx=svglab.Length(30),
                ry=svglab.Length(10),
                fill=svglab.Color("green"),
                stroke=svglab.Color("black"),
            ),
            3,
            svglab.ArcTo,
            id="ellipse",
        ),
        pytest.param(
            svglab.Line(
                x1=svglab.Length(10),
                y1=svglab.Length(15),
                x2=svglab.Length(90),
                y2=svglab.Length(70),
                stroke=svglab.Color("blue"),
                stroke_width=svglab.Length(4),
            ),
            2,
            svglab.LineTo,
            id="line",
        ),
        pytest.param(
            svglab.Polygon(
                points=[
                    svglab.Point(10, 10),
                    svglab.Point(90, 10),
                    svglab.Point(75, 70),
                    svglab.Point(25, 70),
                ],
                fill=svglab.Color("yellow"),
                stroke=svglab.Color("black"),
            ),
            5,
            svglab.ClosePath,
            id="polygon",
        ),
        pytest.param(
            svglab.Polyline(
                points=[
                    svglab.Point(10, 50),
                    svglab.Point(30, 20),
                    svglab.Point(60, 60),
                    svglab.Point(90, 25),
                ],
                fill="none",
                stroke=svglab.Color("purple"),
                stroke_width=svglab.Length(3),
            ),
            4,
            svglab.LineTo,
            id="polyline",
        ),
        pytest.param(
            svglab.Rect(
                x=svglab.Length(20),
                y=svglab.Length(15),
                width=svglab.Length(60),
                height=svglab.Length(40),
                rx=svglab.Length(8),
                fill=svglab.Color("orange"),
                stroke=svglab.Color("black"),
            ),
            9,
            svglab.ArcTo,
            id="rect-rx-only",
        ),
        pytest.param(
            svglab.Rect(
                x=svglab.Length(15),
                y=svglab.Length(20),
                width=svglab.Length(70),
                height=svglab.Length(35),
                ry=svglab.Length(6),
                fill=svglab.Color("cyan"),
                stroke=svglab.Color("black"),
            ),
            9,
            svglab.ArcTo,
            id="rect-ry-only",
        ),
        pytest.param(
            svglab.Rect(
                x=svglab.Length(10),
                y=svglab.Length(10),
                width=svglab.Length(80),
                height=svglab.Length(50),
                rx=svglab.Length(12),
                ry=svglab.Length(4),
                fill=svglab.Color("pink"),
                stroke=svglab.Color("black"),
            ),
            9,
            svglab.ArcTo,
            id="rect-rx-ry",
        ),
    ],
)
def test_basic_shape_to_path_is_visually_equivalent(
    shape: ShapeWithPath,
    expected_num_commands: int,
    last_command_type: type[svglab.PathCommand],
) -> None:
    original = svglab.Svg(
        width=svglab.Length(100), height=svglab.Length(100)
    ).add_child(copy.deepcopy(shape))
    path = copy.deepcopy(shape).to_path()
    converted = svglab.Svg(
        width=svglab.Length(100), height=svglab.Length(100)
    ).add_child(path)

    assert path.d is not None
    assert len(path.d) == expected_num_commands
    assert isinstance(path.d[-1], last_command_type)
    conftest.assert_svg_visually_equal(original, converted)


def test_shape_set_path_length_scales_non_percentage_attrs() -> None:
    path = svglab.Path(
        pathLength=100,
        stroke_dasharray=[svglab.Length(10), svglab.Length(5, "%")],
        stroke_dashoffset=svglab.Length(4),
    )

    path.set_path_length(250)

    assert path.pathLength == 250
    assert path.stroke_dasharray == [
        svglab.Length(25),
        svglab.Length(5, "%"),
    ]
    assert path.stroke_dashoffset == svglab.Length(10)


def test_shape_set_path_length_requires_positive_value() -> None:
    path = svglab.Path(pathLength=100)

    with pytest.raises(ValueError, match="Path length must be positive"):
        path.set_path_length(0)


def test_shape_set_path_length_requires_existing_path_length() -> None:
    path = svglab.Path()

    with pytest.raises(
        RuntimeError, match="Current pathLength must not be None"
    ):
        path.set_path_length(100)


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


def test_eq_element_simple() -> None:
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
        stroke_width=stroke_width, stroke=svglab.Color("red")
    )


def test_eq_element_group() -> None:
    assert svglab.G().add_child(svglab.Rect()) == svglab.G().add_child(
        svglab.Rect()
    )


@hypothesis.given(st.text())
def test_eq_element_prefix(prefix: str) -> None:
    assert svglab.Rect(prefix=prefix) == svglab.Rect(prefix=prefix)


def test_tree_navigation_search_and_mutation() -> None:
    root = svglab.Svg()
    group = svglab.G(id="group")
    rect = svglab.Rect(id="rect")
    circle = svglab.Circle(id="circle")
    line = svglab.Line(id="line")

    root.add_child(group)
    group.add_children(rect, circle, line)

    assert list(circle.ancestors) == [group, root]
    assert list(circle.prev_siblings) == [rect]
    assert list(circle.next_siblings) == [line]
    assert list(circle.siblings) == [rect, line]
    assert circle.get_root() is root

    assert group.find("circle", recursive=False) is circle
    assert list(group.find_all(svglab.Circle, recursive=False)) == [circle]
    assert group.find("ellipse", default=None) is None

    with pytest.raises(svglab.SvgElementNotFoundError):
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
    gradient = svglab.LinearGradient(id="paint")
    rect = svglab.Rect(fill=gradient.get_func_iri())
    svg = svglab.Svg().add_children(gradient, rect)

    assert svg.resolve_iri(svglab.Iri(fragment="paint")) is gradient
    assert rect.references_other_element() is True

    rect.fill = svglab.Iri(fragment="missing").to_func_iri()

    with pytest.warns(UserWarning, match=r"Dangling IRI reference"):
        assert rect.references_other_element() is False

    with pytest.raises(ValueError, match="non-local IRI reference"):
        svg.resolve_iri(
            svglab.Iri(scheme="https", authority="example.com")
        )


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("", svglab.PathData()),
        ("M 10,10", svglab.PathData().move_to(svglab.Point(10, 10))),
        (
            "M0,0L 10,10",
            svglab.PathData()
            .move_to(svglab.Point(0, 0))
            .line_to(svglab.Point(10, 10)),
        ),
        (
            "M0,0H 10",
            svglab.PathData()
            .move_to(svglab.Point(0, 0))
            .horizontal_line_to(10),
        ),
        (
            "M0,0V 10",
            svglab.PathData()
            .move_to(svglab.Point(0, 0))
            .vertical_line_to(10),
        ),
        (
            # https://github.com/mathandy/svgpathtools/issues/185
            "M12 22a10 10 0 110-20 10 10 0 010 20z",
            svglab.PathData()
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
            svglab.PathData()
            .move_to(svglab.Point(1, 1))
            .line_to(svglab.Point(2, 2))
            .line_to(svglab.Point(3, 3))
            .line_to(svglab.Point(4, 4)),
        ),
        (
            "M0,0C 10,10 20,20 30,30S 40,40 50,50Q 60,60 70,70T 80,80A 90,90 0"
            " 1 0 100,100T 110,110ZH 120V 130L 140,140Z",
            svglab.PathData()
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
        (
            "M0,0 Z H100",  # no moveto after closepath
            svglab.PathData()
            .move_to(svglab.Point(0, 0))
            .close()
            .horizontal_line_to(100),
        ),
    ],
)
def test_path_data_parse(text: str, expected: str) -> None:
    assert svglab.PathData.from_str(text) == expected


def test_path_data_parse_moveto_must_be_first() -> None:
    with pytest.raises(
        ValueError,
        match=r"Failed to parse text with grammar 'path_data.lark'",
    ):
        svglab.PathData.from_str("L 10,10")


SHORTHAND_TESTS: Final[list[tuple[svglab.PathData, svglab.PathData]]] = [
    (svglab.PathData(), svglab.PathData()),
    (
        svglab.PathData().move_to(svglab.Point(10, 10)),
        svglab.PathData().move_to(svglab.Point(10, 10)),
    ),
    (
        svglab.PathData()
        .move_to(svglab.Point.zero())
        .line_to(svglab.Point(0, 10)),
        svglab.PathData()
        .move_to(svglab.Point.zero())
        .vertical_line_to(10),
    ),
    (
        svglab.PathData()
        .move_to(svglab.Point.zero())
        .line_to(svglab.Point(10, 0)),
        svglab.PathData()
        .move_to(svglab.Point.zero())
        .horizontal_line_to(10),
    ),
    (
        svglab.PathData()
        .move_to(svglab.Point.zero())
        .quadratic_bezier_to(svglab.Point(20, 0), svglab.Point(20, 20))
        .quadratic_bezier_to(svglab.Point(20, 40), svglab.Point(40, 40)),
        svglab.PathData()
        .move_to(svglab.Point.zero())
        .quadratic_bezier_to(svglab.Point(20, 0), svglab.Point(20, 20))
        .smooth_quadratic_bezier_to(svglab.Point(40, 40)),
    ),
    (
        svglab.PathData()
        .move_to(svglab.Point.zero())
        .cubic_bezier_to(
            svglab.Point(20, 0), svglab.Point(40, 0), svglab.Point(40, 20)
        )
        .cubic_bezier_to(
            svglab.Point(40, 40),
            svglab.Point(20, 40),
            svglab.Point(20, 20),
        ),
        svglab.PathData()
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
    before: svglab.PathData, after: svglab.PathData
) -> None:
    assert before.apply_shorthands() == after


@pytest.mark.parametrize(("after", "before"), SHORTHAND_TESTS)
def test_path_data_resolve_shorthands(
    after: svglab.PathData, before: svglab.PathData
) -> None:
    assert before.resolve_shorthands() == after


@pytest.mark.parametrize(("before", "after"), SHORTHAND_TESTS)
def test_path_data_shorthands_cancel(
    before: svglab.PathData, after: svglab.PathData
) -> None:
    assert before.apply_shorthands().resolve_shorthands() == before
    assert after.resolve_shorthands().apply_shorthands() == after


@pytest.mark.parametrize(("before", "after"), SHORTHAND_TESTS)
def test_path_data_shorthands_idempotent(
    before: svglab.PathData, after: svglab.PathData
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
    assert svglab.PathData.from_str(text).serialize() == expected


def test_path_data_first_command_is_move_to() -> None:
    with pytest.raises(svglab.SvgPathMissingMoveToError):
        svglab.PathData().line_to(svglab.Point(0, 0))

    path = (
        svglab.PathData()
        .move_to(svglab.Point(0, 0))
        .line_to(svglab.Point(0, 0))
    )
    line_to = path[1]

    with pytest.raises(svglab.SvgPathMissingMoveToError):
        del path[0]

    with pytest.raises(svglab.SvgPathMissingMoveToError):
        path[0] = line_to

    with pytest.raises(svglab.SvgPathMissingMoveToError):
        svglab.PathData().insert(0, line_to)

    with pytest.raises(svglab.SvgPathMissingMoveToError):
        svglab.PathData().append(line_to)


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


def test_render_preserves_aspect_ratio_for_single_dimension() -> None:
    svg = svglab.Svg(
        width=svglab.Length(100), height=svglab.Length(200)
    ).add_child(
        svglab.Rect(
            width=svglab.Length(100),
            height=svglab.Length(200),
            fill=svglab.Color("red"),
        )
    )

    assert svg.render(width=50).size == (50, 100)
    assert svg.render(height=50).size == (25, 50)


def test_render_requires_resolvable_dimensions() -> None:
    svg = svglab.Svg(
        width=svglab.Length(100, "%"), height=svglab.Length(100, "%")
    ).add_child(
        svglab.Rect(
            width=svglab.Length(100),
            height=svglab.Length(100),
            fill=svglab.Color("red"),
        )
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
    svg = svglab.Svg(
        width=svglab.Length(width), height=svglab.Length(height)
    ).add_child(
        svglab.Rect(
            width=svglab.Length(width),
            height=svglab.Length(height),
            fill=svglab.Color("red"),
        )
    )

    (img_width, img_height) = svg.render(
        width=target_size, height=target_size
    ).size

    scale = target_size / max(width, height)

    # allow one pixel of rounding error on each axis
    assert img_width == pytest.approx(width * scale, abs=1)
    assert img_height == pytest.approx(height * scale, abs=1)


def test_bbox_matches_mask_bounds() -> None:
    svg = svglab.Svg(
        width=svglab.Length(40), height=svglab.Length(30)
    ).add_child(
        svglab.Rect(
            x=svglab.Length(5),
            y=svglab.Length(6),
            width=svglab.Length(10),
            height=svglab.Length(8),
            fill=svglab.Color("black"),
        )
    )
    rect = svg.find(svglab.Rect)
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
    svg = svglab.Svg(
        width=svglab.Length(40), height=svglab.Length(30)
    ).add_child(
        svglab.Rect(
            x=svglab.Length(5),
            y=svglab.Length(6),
            width=svglab.Length(10),
            height=svglab.Length(8),
            fill=svglab.Color("black"),
            fill_opacity=0,
            stroke="none",
        )
    )
    rect = svg.find(svglab.Rect)

    assert rect.get_bbox() is not None
    assert rect.get_bbox(visible_only=True) is None
    assert rect.get_mask().any()
    assert not rect.get_mask(visible_only=True).any()


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
            fill=svglab.Color("red"),
            stroke=svglab.Color("blue"),
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
            fill=svglab.Color("red"),
            stroke=svglab.Color("blue"),
            transform=[svglab.Translate(10, 20), svglab.Scale(2)],
            transform_origin=(svglab.Length(5), svglab.Length(0)),
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
            fill=svglab.Color("red"),
            stroke=svglab.Color("blue"),
            transform_origin=(svglab.Length(10), svglab.Length(20)),
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
            fill=svglab.Color("red"),
            stroke=svglab.Color("blue"),
        )
    ),
    svglab.Svg(
        width=svglab.Length(1000), height=svglab.Length(1000)
    ).add_child(
        svglab.Path(
            d=svglab.PathData()
            .move_to(svglab.Point(100, 100))
            .line_to(svglab.Point(200, 200))
            .cubic_bezier_to(
                svglab.Point(300, 200),
                svglab.Point(400, 300),
                svglab.Point(500, 300),
            ),
            stroke=svglab.Color("blue"),
            fill=svglab.Color("red"),
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
                stroke=svglab.Color("black"),
            ),
            svglab.Circle(
                cx=svglab.Length(150),
                cy=svglab.Length(50),
                r=svglab.Length(30),
                stroke=svglab.Color("black"),
            ),
            svglab.Line(
                x1=svglab.Length(50),
                y1=svglab.Length(50),
                x2=svglab.Length(150),
                y2=svglab.Length(50),
                stroke=svglab.Color("black"),
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
            fill=svglab.Color("red"),
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
                        stroke=svglab.Color("black"),
                    ),
                    svglab.Circle(
                        cx=svglab.Length(150),
                        cy=svglab.Length(50),
                        r=svglab.Length(30),
                        stroke=svglab.Color("black"),
                    ),
                    svglab.Line(
                        x1=svglab.Length(50),
                        y1=svglab.Length(50),
                        x2=svglab.Length(150),
                        y2=svglab.Length(50),
                        stroke=svglab.Color("black"),
                    ),
                )
            ),
            marks=pytest.mark.xfail(
                reason="Transform/viewBox bug in resvg"
            ),
        ),
        svglab.Svg(
            width=svglab.Length(1000), height=svglab.Length(1000)
        ).add_child(
            svglab.Rect(
                x=svglab.Length(200),
                y=svglab.Length(200),
                width=svglab.Length(100),
                height=svglab.Length(100),
                fill=svglab.Color("red"),
                stroke=svglab.Color("blue"),
                transform=[
                    svglab.compose(
                        [
                            svglab.Translate(10, 20),
                            svglab.Scale(2),
                            svglab.Rotate(45),
                            svglab.Translate(250, -300),
                            svglab.SkewX(-45),
                            svglab.SkewY(-20),
                        ]
                    )
                ],
            )
        ),
        svglab.Svg(
            width=svglab.Length(100),
            height=svglab.Length(100),
            viewBox=(50, 50, 200, 200),
        ).add_child(
            svglab.Rect(
                x=svglab.Length(100),
                y=svglab.Length(100),
                width=svglab.Length(50),
                height=svglab.Length(50),
                fill=svglab.Color("blue"),
            )
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
        [svglab.Scale(0, 1)],
        [svglab.Scale(0)],
    ],
)
def test_decompose_simple(transform: svglab.Transform) -> None:
    assert svglab.compose(transform).decompose() == transform


def test_entity_substitution() -> None:
    assert svglab.RawText(">").to_xml() == "&gt;"


@pytest.mark.parametrize(
    ("value", "serialized"),
    [
        (svglab.Length(1.123456), "1"),
        (svglab.Rotate(1.123456), "rotate(1.1)"),
        (svglab.SkewX(1.123456), "skewX(1.1)"),
        (svglab.Translate(1.123456), "translate(1.123456)"),
        (svglab.Scale(1.123456), "scale(0)"),
    ],
)
def test_float_precision_settings(
    value: _SupportsSerialize, serialized: str
) -> None:
    formatter = svglab.Formatter(
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
        (svglab.Length(0.123456), ".123"),
        (svglab.Rotate(1.123456), "rotate(1.12)"),
        (svglab.SkewX(10.123456), "skewX(10.1)"),
        (svglab.Translate(100.123456), "translate(100)"),
        (svglab.Scale(1000.123456), "scale(1000.123456)"),
    ],
)
def test_precision_table(
    value: _SupportsSerialize, serialized: str
) -> None:
    formatter = svglab.Formatter(
        general_precision=svglab.FloatPrecisionSettings(
            precision_table={
                svglab.PrecisionInterval(0, 1, 3),
                svglab.PrecisionInterval(1, 10, 2),
                svglab.PrecisionInterval(10, 100, 1),
                svglab.PrecisionInterval(100, 1000, 0),
            },
            fallback=15,
        )
    )

    with formatter:
        assert value.serialize() == serialized


def test_invalid_add_child_direct_circular_reference() -> None:
    g = svglab.G()

    with pytest.raises(
        ValueError, match=r"Cannot add an element as a child of itself."
    ):
        g.add_child(g)


def test_large_float_results_in_error() -> None:
    with pytest.raises(ValueError, match=r".*Value must be finite.*"):
        svglab.parse_svg("<svg><rect x='1e9999'/></svg>")


@pytest.mark.parametrize(
    ("a", "b"),
    [
        (svglab.Rect(), svglab.Rect()),
        (
            svglab.Rect(stroke_width=svglab.Length(1)),
            svglab.Rect(stroke_width=svglab.Length(1)),
        ),
        (
            svglab.G().add_child(svglab.Rect()),
            svglab.G().add_child(svglab.Rect()),
        ),
        (svglab.RawText("test"), svglab.RawText("test")),
        (svglab.Comment("test"), svglab.Comment("test")),
        (svglab.CData("test"), svglab.CData("test")),
        (
            svglab.Svg(
                width=svglab.Length(100), height=svglab.Length(100)
            ).add_children(
                svglab.Rect(x=svglab.Length(10), y=svglab.Length(10))
            ),
            svglab.Svg(
                width=svglab.Length(100), height=svglab.Length(100)
            ).add_children(
                svglab.Rect(x=svglab.Length(10), y=svglab.Length(10))
            ),
        ),
    ],
)
def test_hashes_equal(a: svglab.Entity, b: svglab.Entity) -> None:
    assert hash(a) == hash(b)


@pytest.mark.parametrize(
    ("a", "b"),
    [
        (svglab.Rect(), svglab.Circle()),
        (svglab.Rect(stroke_width=svglab.Length(1)), svglab.Rect()),
        (
            svglab.Rect(stroke_width=svglab.Length(1)),
            svglab.Rect(stroke_width=svglab.Length(2)),
        ),
        (
            svglab.Rect(stroke_width=svglab.Length(1)),
            svglab.Circle(stroke_width=svglab.Length(1)),
        ),
        (
            svglab.G().add_child(svglab.Rect()),
            svglab.G().add_child(svglab.Circle()),
        ),
        (svglab.RawText("test"), svglab.RawText("test2")),
        (svglab.RawText("test"), svglab.Comment("test")),
        (svglab.RawText("test"), svglab.CData("test")),
        (svglab.Comment("test"), svglab.Comment("test2")),
        (svglab.Comment("test"), svglab.CData("test")),
        (svglab.CData("test"), svglab.CData("test2")),
    ],
)
def test_hashes_unequal(a: svglab.Entity, b: svglab.Entity) -> None:
    assert hash(a) != hash(b)


def test_points_accepts_empty_list() -> None:
    svg = svglab.parse_svg("<svg><polyline points=''/></svg>")
    polyline = svg.find(svglab.Polyline)

    assert polyline.points == []


def test_transform_accepts_empty_list() -> None:
    svg = svglab.parse_svg("<svg><rect transform=''/></svg>")
    rect = svg.find(svglab.Rect)

    assert rect.transform == []


def test_path_data_accepts_empty_list() -> None:
    svg = svglab.parse_svg("<svg><path d=''/></svg>")
    path = svg.find(svglab.Path)

    assert path.d == svglab.PathData()


def test_closepath_ends_at_start_of_subpath() -> None:
    svg = svglab.Svg().add_child(
        svglab.Path(d=svglab.PathData.from_str("M10,10 L20,20 Z H30"))
    )

    assert "h20" in svg.to_xml(
        formatter=svglab.Formatter(path_data_coordinates="relative")
    )


def test_parse_svg_with_path() -> None:
    path = conftest.ASSETS_DIR / "dummy.svg"

    svglab.parse_svg(path)
