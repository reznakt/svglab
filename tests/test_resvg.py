import dataclasses
import math

import hypothesis
import hypothesis.strategies as st
import numpy as np
import pytest

from svglab import Color, Length, RawText, Rect, Svg, SvgRenderError, Text
from svglab.resvg import RenderOptions, render


EMPTY = '<svg xmlns="http://www.w3.org/2000/svg" width="2" height="2"/>'

sizes = st.integers(min_value=1, max_value=16)
channels = st.integers(min_value=0, max_value=255)
zooms = st.integers(min_value=1, max_value=8)


def solid(width: int, height: int, color: Color) -> Svg:
    return Svg(width=Length(width), height=Length(height)).add_child(
        Rect(width=Length(width), height=Length(height), fill=color)
    )


def text_svg() -> Svg:
    text = Text(font_size=Length(20), y=[Length(20)])
    text.add_child(RawText("hello"))

    return Svg(width=Length(60), height=Length(30)).add_child(text)


@pytest.fixture(scope="session")
def system_font() -> None:
    if text_svg().render().getbbox() is None:
        pytest.skip("the host has no usable system font")


@hypothesis.settings(deadline=None)
@hypothesis.given(
    width=sizes, height=sizes, red=channels, green=channels, blue=channels
)
def test_solid_document_renders_one_color(
    width: int, height: int, red: int, green: int, blue: int
) -> None:
    image = solid(width, height, Color((red, green, blue))).render()

    assert image.mode == "RGBA"
    assert image.size == (width, height)
    assert (np.asarray(image) == (red, green, blue, 255)).all()


@hypothesis.settings(deadline=None)
@hypothesis.given(alpha=st.integers(min_value=1, max_value=255))
def test_alpha_is_straight_not_premultiplied(alpha: int) -> None:
    svg = Svg(width=Length(1), height=Length(1)).add_child(
        Rect(
            width=Length(1),
            height=Length(1),
            fill=Color("red"),
            fill_opacity=alpha / 255,
        )
    )

    # premultiplied storage would scale the red channel down with the alpha,
    # which is exactly what Pillow must not be handed
    assert svg.render().getpixel((0, 0)) == (255, 0, 0, alpha)


@hypothesis.settings(deadline=None)
@hypothesis.given(width=sizes, height=sizes, zoom=zooms)
def test_zoom_scales_the_image(width: int, height: int, zoom: int) -> None:
    image = solid(width, height, Color("red")).render(zoom=zoom)

    assert image.size == (width * zoom, height * zoom)


@hypothesis.given(
    zoom=st.floats(max_value=0, allow_infinity=True) | st.just(math.nan)
)
def test_zoom_must_be_positive_and_finite(zoom: float) -> None:
    with pytest.raises(ValueError, match="zoom must be positive"):
        render(EMPTY, zoom=zoom)


@hypothesis.settings(deadline=None)
@hypothesis.given(red=channels, green=channels, blue=channels)
def test_opaque_background_is_painted_under_the_document(
    red: int, green: int, blue: int
) -> None:
    image = render(EMPTY, background=Color((red, green, blue)))

    assert (np.asarray(image) == (red, green, blue, 255)).all()


def test_translucent_background_keeps_its_alpha() -> None:
    background = Color("rgba(0, 0, 255, 0.5)")

    assert render(EMPTY, background=background).getpixel((0, 0)) == (
        0,
        0,
        255,
        128,
    )


def test_document_without_a_background_is_transparent() -> None:
    assert not np.asarray(render(EMPTY)).any()


def test_malformed_document_is_rejected() -> None:
    with pytest.raises(SvgRenderError, match="cannot parse SVG"):
        render("h1 { color: red }")


def test_document_without_a_positive_size_is_rejected() -> None:
    svg = '<svg xmlns="http://www.w3.org/2000/svg" width="0" height="0"/>'

    with pytest.raises(SvgRenderError):
        render(svg)


def test_style_sheet_overrides_attributes() -> None:
    svg = solid(4, 4, Color("red"))
    options = RenderOptions(style_sheet="rect { fill: lime }")

    assert svg.render(options).getpixel((0, 0)) == (0, 255, 0, 255)


@pytest.mark.usefixtures("system_font")
def test_skip_system_fonts_draws_no_text() -> None:
    svg = text_svg()
    options = RenderOptions(skip_system_fonts=True)

    assert svg.render().getbbox() is not None
    assert svg.render(options).getbbox() is None


@pytest.mark.usefixtures("system_font")
def test_default_font_family_resolves_through_serif() -> None:
    svg = text_svg()
    options = RenderOptions(serif_family="NoSuchFontFamily")

    assert svg.render().getbbox() is not None
    assert svg.render(options).getbbox() is None


def test_options_reject_an_unknown_rendering_mode() -> None:
    with pytest.raises(ValueError, match="shape_rendering"):
        RenderOptions(shape_rendering="fastest")  # pyright: ignore[reportArgumentType]


def test_options_reject_an_invalid_default_size() -> None:
    svg = Svg(width=Length(4), height=Length(4))

    with pytest.raises(ValueError, match="invalid default_size"):
        svg.render(RenderOptions(default_size=(0, 0)))


def test_options_are_immutable() -> None:
    options = RenderOptions(dpi=300)

    with pytest.raises(dataclasses.FrozenInstanceError):
        options.dpi = 96  # pyright: ignore[reportAttributeAccessIssue]


def test_options_with_equal_settings_are_equal() -> None:
    assert RenderOptions() == RenderOptions()
    assert RenderOptions(dpi=300) != RenderOptions()
