"""An attribute that cannot be read need not cost the whole document."""

import warnings

import pytest

import svglab


_BAD = (
    '<svg xmlns="http://www.w3.org/2000/svg" width="10" height="10">'
    '<rect width="2" height="2" fill="#e8b express"'
    ' stroke-linejoin="square"/>'
    '<path d="M0,0 L1,1" text-anchor="left"/>'
    "</svg>"
)


def test_a_bad_value_still_refuses_the_document_by_default() -> None:
    with pytest.raises(Exception, match=r"."):
        svglab.parse_svg(_BAD)


def test_lenient_parsing_drops_the_attribute_and_keeps_the_document() -> (
    None
):
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        svg = svglab.parse_svg(_BAD, lenient=True)

    rect = svg.find(svglab.Rect)

    assert rect.fill is None
    assert rect.stroke_linejoin is None
    assert svg.find(svglab.Path).text_anchor is None

    # the geometry, which was fine, is untouched
    assert rect.width == svglab.Length(2)
    assert svg.find(svglab.Path).d is not None

    assert len(caught) == 3
    assert all("Dropping" in str(w.message) for w in caught)


def test_lenient_parsing_leaves_a_good_document_alone() -> None:
    good = (
        '<svg xmlns="http://www.w3.org/2000/svg" width="10" height="10">'
        '<rect width="2" height="2" fill="red"/></svg>'
    )

    assert svglab.parse_svg(good, lenient=True).to_xml() == (
        svglab.parse_svg(good).to_xml()
    )


def test_lenient_parsing_does_not_hide_a_broken_document() -> None:
    # nothing here names an attribute to drop, so there is no recovery to
    # be had and the error stands
    with pytest.raises(ValueError, match="Expected one <svg> element"):
        svglab.parse_svg("<not-svg/>", lenient=True)
