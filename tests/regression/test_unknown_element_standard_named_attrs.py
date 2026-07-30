import pytest

import svglab


@pytest.mark.parametrize("pretty", [True, False])
def test_unknown_element_with_standard_named_attrs_serializes(
    *, pretty: bool
) -> None:
    svg = svglab.parse_svg('<svg><jfdkslfjlsd class="a" d="M0 0"/></svg>')
    xml = svg.to_xml(pretty=pretty)

    assert 'class="a"' in xml
    assert 'd="M0 0"' in xml
