"""An Illustrator export declares its namespaces as entities in the DOCTYPE.

The XML parser behind BeautifulSoup stops at the first reference to such an
entity, so a document exported by Illustrator parsed as having no `svg`
element at all. The entities are expanded before parsing.
"""

import pytest

from svglab import Rect, parse_svg


_MARKUP = """<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN"
 "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd" [
\t<!ENTITY ns_ai "http://ns.adobe.com/AdobeIllustrator/10.0/">
\t<!ENTITY ns_sfw 'http://ns.adobe.com/SaveForWeb/1.0/'>
]>
<svg xmlns="http://www.w3.org/2000/svg" xmlns:i="&ns_ai;" width="10"
     height="10">
  <rect width="10" height="10" i:knockout="false"/>
</svg>
"""


@pytest.mark.parametrize("markup", [_MARKUP, _MARKUP.encode()])
def test_entities_declared_in_the_doctype_are_expanded(
    markup: str | bytes,
) -> None:
    svg = parse_svg(markup)

    assert svg["xmlns:i"] == "http://ns.adobe.com/AdobeIllustrator/10.0/"
    assert isinstance(svg.find(Rect), Rect)
    assert "DOCTYPE" not in svg.to_xml()


def test_a_doctype_without_a_subset_is_left_to_the_parser() -> None:
    svg = parse_svg(
        '<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "x.dtd">'
        '<svg width="10" height="10"><rect width="10" height="10"/></svg>'
    )

    assert isinstance(svg.find(Rect), Rect)
