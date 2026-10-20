import pytest

from svglab import FuncIri, Rect, parse_svg


@pytest.mark.parametrize(
    "value", ["url('#g')", 'url("#g")', "url( '#g' )", "URL(#g)"]
)
def test_func_iri_strips_the_url_function_and_quotes(value: str) -> None:
    iri = FuncIri.from_str(value)

    assert iri.is_local
    assert iri.fragment == "g"
    assert iri.serialize() == "url(#g)"


def test_quoted_func_iri_round_trips_and_resolves() -> None:
    svg = parse_svg("""
        <svg>
            <linearGradient id="g"/>
            <rect fill='url("#g")'/>
        </svg>
    """)
    rect = svg.find(Rect)

    assert rect.references_other_element()
    assert 'fill="url(#g)"' in rect.to_xml()
