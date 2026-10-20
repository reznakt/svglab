import pytest

from svglab import Color, FeFlood, Formatter, Stop, parse_svg


def test_stop_and_flood_colors_are_parsed_as_colors() -> None:
    svg = parse_svg("""
        <svg>
            <linearGradient><stop stop-color="red"/></linearGradient>
            <filter><feFlood flood-color="#00ff00"/></filter>
        </svg>
    """)

    assert svg.find(Stop).stop_color == Color("red")
    assert svg.find(FeFlood).flood_color == Color("#00ff00")


def test_stop_color_follows_the_formatter_color_mode() -> None:
    stop = parse_svg('<svg><stop stop-color="red"/></svg>').find(Stop)

    output = stop.to_xml(formatter=Formatter(color_mode="hex-long"))

    assert 'stop-color="#ff0000"' in output


@pytest.mark.parametrize(
    "value", ["currentColor", "#abc icc-color(x, 0.1)"]
)
def test_stop_color_keeps_other_values(value: str) -> None:
    stop = parse_svg(f'<svg><stop stop-color="{value}"/></svg>').find(Stop)

    assert stop.stop_color == value
