"""A viewBox with no extent disables rendering rather than reification."""

import pytest

from svglab import Rect, parse_svg


@pytest.mark.parametrize("view_box", ["0 0 100 0", "0 0 0 100"])
def test_a_zero_viewbox_leaves_the_document_alone(view_box: str) -> None:
    svg = parse_svg(f"""
        <svg width="200" height="200" viewBox="{view_box}"
             transform="scale(2)">
            <rect width="100" height="100" transform="translate(5 5)"/>
        </svg>
    """)

    svg.reify()

    assert svg.transform is not None
    assert svg.find(Rect).x is not None
