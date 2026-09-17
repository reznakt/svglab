"""The CSS values SVG 2 added that real documents and browsers use."""

import pytest

import svglab


def _rect(attr: str, value: str) -> str:
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" width="10" height="10">'
        f'<rect width="1" height="1" {attr}="{value}"/></svg>'
    )


@pytest.mark.parametrize(
    ("attr", "value"),
    [
        ("filter", "blur(2px)"),
        ("filter", "drop-shadow(0 1px 1px rgba(0,0,0,0.3))"),
        ("filter", "blur(4px) saturate(2)"),
        ("filter", "url(#f)"),
        ("filter", "none"),
        ("clip-path", "inset(0)"),
        ("clip-path", "inset(0 0 50% 0)"),
        ("clip-path", "circle(160px at -40px -40px)"),
        ("clip-path", "polygon(0% 100%, 50% 0%, 100% 100%)"),
        ("clip-path", "url(#c)"),
        ("font-weight", "750"),
        ("font-weight", "1"),
        ("font-weight", "1000"),
        ("font-weight", "bold"),
    ],
)
def test_a_css_value_is_read_and_written_back(
    attr: str, value: str
) -> None:
    svg = svglab.parse_svg(_rect(attr, value))

    assert f'{attr}="{value}"' in svg.to_xml()


@pytest.mark.parametrize(
    ("attr", "value"),
    [
        ("filter", "blur"),
        ("filter", "#url(#x)"),
        ("clip-path", "bogus"),
        ("clip-path", "inset"),
        ("font-weight", "0"),
        ("font-weight", "1001"),
    ],
)
def test_something_that_is_not_one_is_still_refused(
    attr: str, value: str
) -> None:
    with pytest.raises(Exception, match=r"."):
        svglab.parse_svg(_rect(attr, value))


@pytest.mark.parametrize(
    "mode",
    ["normal", "multiply", "overlay", "soft-light", "luminosity", "hue"],
)
def test_fe_blend_takes_the_css_blend_modes(mode: str) -> None:
    # SVG 1.1 gave feBlend five modes; SVG 2 defers to CSS Compositing
    svg = svglab.parse_svg(
        '<svg xmlns="http://www.w3.org/2000/svg" width="10" height="10">'
        f'<filter id="f"><feBlend mode="{mode}"/></filter></svg>'
    )

    assert svg.find(svglab.FeBlend).mode == mode


def test_a_blend_mode_that_is_not_one_is_refused() -> None:
    with pytest.raises(Exception, match=r"."):
        svglab.parse_svg(
            '<svg xmlns="http://www.w3.org/2000/svg" width="10" height="10">'
            '<filter id="f"><feBlend mode="bogus"/></filter></svg>'
        )
