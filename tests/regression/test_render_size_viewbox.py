import pytest

import svglab
from tests import conftest


SVG = """
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="-10 0 930 1000">
        <path fill="currentColor" d="M145 338h153v149h-153z"/>
    </svg>
"""


def test_render_size_from_viewbox() -> None:
    assert svglab.parse_svg(SVG).render().size == (930, 1000)


def test_render_width_uses_viewbox_aspect_ratio() -> None:
    assert svglab.parse_svg(SVG).render(width=256).size == (256, 275)


def test_render_height_uses_viewbox_aspect_ratio() -> None:
    assert svglab.parse_svg(SVG).render(height=1000).size == (930, 1000)


def test_render_fits_both_dimensions_into_viewbox_aspect_ratio() -> None:
    assert svglab.parse_svg(SVG).render(width=930, height=500).size == (
        465,
        500,
    )


def test_render_size_prefers_dimension_attrs_over_viewbox() -> None:
    svg = svglab.parse_svg("""
        <svg xmlns="http://www.w3.org/2000/svg"
             width="100" height="300" viewBox="0 0 100 100">
            <rect width="100" height="100" fill="blue"/>
        </svg>
    """)

    assert svg.render(width=50).size == (50, 150)


def test_render_size_falls_back_to_viewbox_for_percentage_dimensions() -> (
    None
):
    svg = svglab.parse_svg("""
        <svg xmlns="http://www.w3.org/2000/svg"
             width="100%" height="100%" viewBox="0 0 200 100">
            <rect width="200" height="100" fill="blue"/>
        </svg>
    """)

    assert svg.render().size == (200, 100)


def test_render_rejects_degenerate_viewbox() -> None:
    svg = svglab.parse_svg("""
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 0 100">
            <rect width="100" height="100" fill="blue"/>
        </svg>
    """)

    with pytest.raises(
        ValueError, match="Unable to determine image dimensions"
    ):
        svg.render()


def test_render_rejects_missing_dimensions_without_viewbox() -> None:
    svg = svglab.parse_svg("""
        <svg xmlns="http://www.w3.org/2000/svg">
            <rect width="100" height="100" fill="blue"/>
        </svg>
    """)

    with pytest.raises(
        ValueError, match="Unable to determine image dimensions"
    ):
        svg.render()


def test_viewbox_only_svg_renders_same_content_as_sized_svg() -> None:
    """The viewBox fallback must not shift or rescale the content."""
    sized = svglab.parse_svg("""
        <svg xmlns="http://www.w3.org/2000/svg"
             width="930" height="1000" viewBox="-10 0 930 1000">
            <path fill="currentColor" d="M145 338h153v149h-153z"/>
        </svg>
    """)

    conftest.assert_svg_visually_equal(svglab.parse_svg(SVG), sized)
