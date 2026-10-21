import pytest
from typing_extensions import Literal

from svglab import Animate, AnimateMotion, Formatter, parse_svg


def test_semicolon_separated_attributes_are_parsed_into_lists() -> None:
    svg = parse_svg("""
        <svg>
            <animate
                begin="0s; click"
                end="indefinite"
                values="0; 10 ;0"
                keyTimes="0;0.5;1"
                keySplines="0.5 0 0.5 1; 0.25,0.1,0.25,1"
            />
            <animateMotion keyPoints="0;"/>
        </svg>
    """)
    animate = svg.find(Animate)

    assert animate.begin == ["0s", "click"]
    assert animate.end == ["indefinite"]
    assert animate.values == ["0", "10", "0"]
    assert animate.keyTimes == [0, 0.5, 1]
    assert animate.keySplines == [(0.5, 0, 0.5, 1), (0.25, 0.1, 0.25, 1)]
    assert svg.find(AnimateMotion).keyPoints == [0]


@pytest.mark.parametrize("list_separator", [" ", ",", ", "])
def test_semicolon_lists_ignore_the_list_separator(
    list_separator: Literal[" ", ",", ", "],
) -> None:
    animate = Animate(values=["red", "blue"], keyTimes=[0, 1])
    formatter = Formatter(list_separator=list_separator)

    output = animate.to_xml(formatter=formatter)

    assert 'keyTimes="0;1"' in output
    assert 'values="red;blue"' in output


def test_key_splines_keep_their_control_points_together() -> None:
    animate = Animate(keySplines=[(0.5, 0, 0.5, 1), (0, 0, 1, 1)])

    assert 'keySplines=".5 0 .5 1;0 0 1 1"' in animate.to_xml()


def test_semicolon_lists_round_trip() -> None:
    svg = parse_svg(
        '<svg><animate begin="0s;click" keyTimes="0;.5;1" values="a;b"/>'
        "</svg>"
    )

    assert parse_svg(svg.to_xml()) == svg


def test_invalid_key_times_are_rejected() -> None:
    with pytest.raises(ValueError, match="keyTimes"):
        parse_svg('<svg><animate keyTimes="0;x;1"/></svg>')
