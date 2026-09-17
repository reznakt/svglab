"""`prefix` is an attribute in the wild, not only a namespace prefix."""

import svglab


_RDFA = (
    '<svg xmlns="http://www.w3.org/2000/svg" '
    'prefix="schema:http://schema.org/" '
    'vocab="http://vocabularies.wikipathways.org/wp#" '
    'width="10" height="10"><rect width="2" height="2"/></svg>'
)


def test_a_prefix_attribute_stays_an_attribute() -> None:
    # the parser merged the element's attributes over the namespace prefix
    # under the same key, so a document carrying RDFa's `prefix` had its
    # value adopted as the element's namespace
    svg = svglab.parse_svg(_RDFA)

    assert svg.namespace_prefix in (None, "")
    assert svg.all_attrs()["prefix"] == "schema:http://schema.org/"


def test_such_a_document_survives_a_round_trip() -> None:
    # it used to serialize to `<schema:http://schema.org/:svg ...>`, which
    # svglab then could not read back at all
    xml = svglab.parse_svg(_RDFA).to_xml()

    assert "<svg" in xml
    assert 'prefix="schema:http://schema.org/"' in xml

    again = svglab.parse_svg(xml)

    assert again.to_xml() == xml


def test_a_real_namespace_prefix_is_still_read() -> None:
    svg = svglab.parse_svg(
        '<svg:svg xmlns:svg="http://www.w3.org/2000/svg"'
        ' width="10" height="10"/>'
    )

    assert svg.namespace_prefix == "svg"
