from svglab import FeTurbulence, Formatter, parse_svg


def test_integer_attributes_have_no_decimal_part() -> None:
    svg = parse_svg(
        '<svg><filter><feTurbulence numOctaves="2"/></filter>'
        '<text font-weight="400">a</text></svg>'
    )

    xml = svg.to_xml(
        pretty=False, formatter=Formatter(show_decimal_part_if_int=True)
    )

    assert 'numOctaves="2"' in xml
    assert 'font-weight="400"' in xml
    assert parse_svg(xml) == svg


def test_large_integer_attributes_are_not_in_scientific_notation() -> None:
    turbulence = FeTurbulence(numOctaves=2_000_000)

    with Formatter(large_number_scientific_threshold=1000):
        assert (
            turbulence.to_xml() == '<feTurbulence numOctaves="2000000"/>'
        )
