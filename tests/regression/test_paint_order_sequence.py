"""`paint-order` names an order, so it takes a sequence of keywords."""

import pytest

import svglab


def _path(paint_order: str) -> str:
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" width="10" height="10">'
        f'<path d="M0,0" paint-order="{paint_order}"/></svg>'
    )


@pytest.mark.parametrize(
    "value",
    [
        "fill",
        "stroke",
        "markers",
        "fill stroke",
        "stroke fill",
        "markers stroke fill",
        "fill markers stroke",
        "stroke fill markers",
    ],
)
def test_the_order_is_read_and_written_back_as_given(value: str) -> None:
    # the grammar is `normal | [ fill || stroke || markers ]`, and the point
    # of the attribute is the order, so it has to survive a round trip
    svg = svglab.parse_svg(_path(value))

    assert svg.find(svglab.Path).paint_order == value.split()
    assert f'paint-order="{value}"' in svg.to_xml()


@pytest.mark.parametrize("value", ["normal", "inherit"])
def test_the_single_keywords_are_still_single(value: str) -> None:
    svg = svglab.parse_svg(_path(value))

    assert svg.find(svglab.Path).paint_order == value


@pytest.mark.parametrize("value", ["bogus", "fill bogus", "normal fill"])
def test_a_keyword_that_is_not_one_is_still_refused(value: str) -> None:
    with pytest.raises(Exception, match=r"."):
        svglab.parse_svg(_path(value))
