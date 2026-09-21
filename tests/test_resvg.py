import dataclasses
import math

import hypothesis
import hypothesis.strategies as st
import numpy as np
import pytest

import svglab
from svglab import resvg


EMPTY = '<svg xmlns="http://www.w3.org/2000/svg" width="2" height="2"/>'

sizes = st.integers(min_value=1, max_value=16)
channels = st.integers(min_value=0, max_value=255)
zooms = st.integers(min_value=1, max_value=8)


def solid(width: int, height: int, color: svglab.Color) -> svglab.Svg:
    return svglab.Svg(
        width=svglab.Length(width), height=svglab.Length(height)
    ).add_child(
        svglab.Rect(
            width=svglab.Length(width),
            height=svglab.Length(height),
            fill=color,
        )
    )


@hypothesis.settings(deadline=None)
@hypothesis.given(
    width=sizes, height=sizes, red=channels, green=channels, blue=channels
)
def test_solid_document_renders_one_color(
    width: int, height: int, red: int, green: int, blue: int
) -> None:
    image = solid(width, height, svglab.Color((red, green, blue))).render()

    assert image.mode == "RGBA"
    assert image.size == (width, height)
    assert (np.asarray(image) == (red, green, blue, 255)).all()


@hypothesis.settings(deadline=None)
@hypothesis.given(alpha=st.integers(min_value=1, max_value=255))
def test_alpha_is_straight_not_premultiplied(alpha: int) -> None:
    svg = svglab.Svg(
        width=svglab.Length(1), height=svglab.Length(1)
    ).add_child(
        svglab.Rect(
            width=svglab.Length(1),
            height=svglab.Length(1),
            fill=svglab.Color("red"),
            fill_opacity=alpha / 255,
        )
    )

    # premultiplied storage would scale the red channel down with the alpha,
    # which is exactly what Pillow must not be handed
    assert svg.render().getpixel((0, 0)) == (255, 0, 0, alpha)


@hypothesis.settings(deadline=None)
@hypothesis.given(width=sizes, height=sizes, zoom=zooms)
def test_zoom_scales_the_image(width: int, height: int, zoom: int) -> None:
    image = solid(width, height, svglab.Color("red")).render(zoom=zoom)

    assert image.size == (width * zoom, height * zoom)


@hypothesis.given(
    zoom=st.floats(max_value=0, allow_infinity=True) | st.just(math.nan)
)
def test_zoom_must_be_positive_and_finite(zoom: float) -> None:
    with pytest.raises(ValueError, match="zoom must be positive"):
        resvg.render(EMPTY, zoom=zoom)


@hypothesis.settings(deadline=None)
@hypothesis.given(red=channels, green=channels, blue=channels)
def test_opaque_background_is_painted_under_the_document(
    red: int, green: int, blue: int
) -> None:
    image = resvg.render(
        EMPTY, background=svglab.Color((red, green, blue))
    )

    assert (np.asarray(image) == (red, green, blue, 255)).all()


def test_translucent_background_keeps_its_alpha() -> None:
    background = svglab.Color("rgba(0, 0, 255, 0.5)")

    assert resvg.render(EMPTY, background=background).getpixel((0, 0)) == (
        0,
        0,
        255,
        128,
    )


def test_document_without_a_background_is_transparent() -> None:
    assert not np.asarray(resvg.render(EMPTY)).any()


def test_malformed_document_is_rejected() -> None:
    with pytest.raises(svglab.SvgRenderError, match="cannot parse SVG"):
        resvg.render("h1 { color: red }")


def test_document_without_a_positive_size_is_rejected() -> None:
    svg = '<svg xmlns="http://www.w3.org/2000/svg" width="0" height="0"/>'

    with pytest.raises(svglab.SvgRenderError):
        resvg.render(svg)


def test_style_sheet_overrides_attributes() -> None:
    svg = solid(4, 4, svglab.Color("red"))
    options = resvg.RenderOptions(style_sheet="rect { fill: lime }")

    assert svg.render(options).getpixel((0, 0)) == (0, 255, 0, 255)


def test_skip_system_fonts_draws_no_text() -> None:
    text = svglab.Text(font_size=svglab.Length(20), y=[svglab.Length(20)])
    text.add_child(svglab.RawText("hello"))
    svg = svglab.Svg(
        width=svglab.Length(60), height=svglab.Length(30)
    ).add_child(text)

    options = resvg.RenderOptions(skip_system_fonts=True)

    assert svg.render().getbbox() is not None
    assert svg.render(options).getbbox() is None


def test_serif_family_changes_the_rendering() -> None:
    text = svglab.Text(font_size=svglab.Length(20), y=[svglab.Length(20)])
    text.add_child(svglab.RawText("hello"))
    svg = svglab.Svg(
        width=svglab.Length(60), height=svglab.Length(30)
    ).add_child(text)
    options = resvg.RenderOptions(serif_family="DejaVu Serif")

    assert svg.render().getbbox() != svg.render(options).getbbox()


def test_options_reject_an_unknown_rendering_mode() -> None:
    with pytest.raises(ValueError, match="shape_rendering"):
        resvg.RenderOptions(shape_rendering="fastest")  # pyright: ignore[reportArgumentType]


def test_options_reject_an_invalid_default_size() -> None:
    svg = svglab.Svg(width=svglab.Length(4), height=svglab.Length(4))

    with pytest.raises(ValueError, match="invalid default_size"):
        svg.render(resvg.RenderOptions(default_size=(0, 0)))


def test_options_are_immutable() -> None:
    options = resvg.RenderOptions(dpi=300)

    with pytest.raises(dataclasses.FrozenInstanceError):
        options.dpi = 96  # pyright: ignore[reportAttributeAccessIssue]


def test_options_with_equal_settings_are_equal() -> None:
    assert resvg.RenderOptions() == resvg.RenderOptions()
    assert resvg.RenderOptions(dpi=300) != resvg.RenderOptions()
