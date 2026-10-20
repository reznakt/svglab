import lxml.etree
import pytest

from svglab import CData, Comment, G, parse_svg


@pytest.mark.parametrize("content", ["trailing dash-", "a -- b", "---"])
def test_comment_with_dashes_is_well_formed(content: str) -> None:
    xml = G().add_child(Comment(content)).to_xml(pretty=False)

    lxml.etree.fromstring(xml)


def test_cdata_with_terminator_is_well_formed() -> None:
    xml = G().add_child(CData("x]]>y")).to_xml(pretty=False)

    lxml.etree.fromstring(xml)
    assert "x]]&gt;y" in parse_svg(f"<svg>{xml}</svg>").to_xml(
        pretty=False
    )
