from xml.sax import saxutils

import pytest

import svglab
from svglab import serialize


@pytest.mark.parametrize(
    ("text", "families", "serialized"),
    [
        (
            "Arial, sans-serif",
            ["Arial", "sans-serif"],
            "Arial, sans-serif",
        ),
        (
            "Times New Roman,serif",
            ["Times New Roman", "serif"],
            "Times New Roman, serif",
        ),
        (
            "'Foo, Bar', \"Baz Qux\", monospace",
            ["'Foo, Bar'", '"Baz Qux"', "monospace"],
            "'Foo, Bar', \"Baz Qux\", monospace",
        ),
        ("serif", ["serif"], "serif"),
    ],
)
def test_font_family_is_separated_by_commas_only(
    text: str, families: list[str], serialized: str
) -> None:
    doc = svglab.parse_svg(
        f"<svg><text font-family={saxutils.quoteattr(text)}>a</text></svg>"
    )
    element = doc.find(svglab.Text)

    assert element.font_family == families
    assert (
        serialize.serialize_attr("font-family", element.font_family)
        == serialized
    )


def test_assigned_font_family_serializes_with_commas() -> None:
    text = svglab.Text(font_family=["Times New Roman", "serif"])

    assert 'font-family="Times New Roman, serif"' in text.to_xml()


@pytest.mark.parametrize(
    ("element", "attr", "value"),
    [
        ("rect", "cursor", "url(#a), url(#b), pointer"),
        ("font-face", "font-family", "Times New Roman, serif"),
        ("font-face", "font-style", "normal, italic"),
        ("font-face", "font-weight", "400, 700, bold"),
        ("font-face", "unicode-range", "U+0-7F, U+A0-FF"),
        ("font-face", "widths", "U+0-7F 500, 600 700"),
        ("hkern", "g1", "a, b c"),
        ("hkern", "g2", "d"),
        ("hkern", "u1", "a, U+30-39"),
        ("hkern", "u2", "b, c"),
        ("glyph", "glyph-name", "one, two"),
    ],
)
def test_comma_separated_attribute_round_trips(
    element: str, attr: str, value: str
) -> None:
    doc = svglab.parse_svg(f'<svg><{element} {attr}="{value}"/></svg>')

    assert f'{attr}="{value}"' in doc.to_xml()
