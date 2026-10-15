"""The whitespace of a text is drawn, so it survives parsing and printing.

Pretty-printing lays markup out with newlines and indentation. Inside a text
content element that whitespace is character data like any other, so the
element is written as it was read, and the whitespace between its spans is
kept by the parser rather than dropped as layout.
"""

import pytest

from svglab import RawText, Svg, Tspan, parse_svg
from tests.conftest import assert_svg_visually_equal


def _round_trip(svg: Svg) -> Svg:
    return parse_svg(svg.to_xml())


def test_a_pretty_printed_text_is_written_as_read() -> None:
    svg = parse_svg(
        '<svg xmlns="http://www.w3.org/2000/svg" width="200" height="60">'
        '<g><text x="5" y="40">fore<tspan fill="red">cast</tspan> ahead</text>'
        "</g></svg>"
    )

    xml = svg.to_xml()

    assert (
        '<text x="5" y="40">fore<tspan fill="red">cast</tspan> ahead</text>'
        in xml
    )
    assert_svg_visually_equal(svg, _round_trip(svg))


def test_whitespace_between_spans_is_kept() -> None:
    svg = parse_svg(
        '<svg xmlns="http://www.w3.org/2000/svg" width="200" height="60">'
        '<text x="5" y="40" font-size="30">\n  <tspan>a</tspan>\n  '
        "<tspan>b</tspan>\n</text></svg>"
    )

    first, _ = svg.find_all(Tspan)
    between = next(first.next_siblings)

    assert isinstance(between, RawText)
    assert between.content.isspace()
    assert_svg_visually_equal(svg, _round_trip(svg))


@pytest.mark.parametrize("space", ["default", "preserve"])
def test_a_text_renders_the_same_after_a_round_trip(space: str) -> None:
    svg = parse_svg(
        '<svg xmlns="http://www.w3.org/2000/svg" width="300" height="60">'
        f'<text x="5" y="40" font-size="30" xml:space="{space}">'
        "  a <tspan>b</tspan>\n\n   c  </text></svg>"
    )

    assert_svg_visually_equal(svg, _round_trip(svg))


def test_whitespace_around_other_elements_is_still_layout() -> None:
    svg = parse_svg(
        '<svg xmlns="http://www.w3.org/2000/svg">\n  <g>\n    <rect/>\n'
        "  </g>\n</svg>"
    )

    assert svg.to_xml(pretty=False) == (
        '<svg xmlns="http://www.w3.org/2000/svg"><g><rect/></g></svg>'
    )
