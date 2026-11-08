"""`paint-order` names the layers to paint first, in any order."""

import pytest

from svglab import Rect, parse_svg


@pytest.mark.parametrize(
    ("value", "parsed"),
    [
        ("normal", "normal"),
        ("stroke", ["stroke"]),
        ("markers stroke", ["markers", "stroke"]),
        ("stroke fill markers", ["stroke", "fill", "markers"]),
    ],
)
def test_paint_order_round_trips(value: str, parsed: object) -> None:
    svg = parse_svg(f'<svg><rect paint-order="{value}"/></svg>')

    assert svg.find(Rect).paint_order == parsed
    assert f'paint-order="{value}"' in svg.to_xml()
