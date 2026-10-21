from svglab import Color, Rect, Use, parse_svg


def test_find_all_returns_elements_in_document_order() -> None:
    svg = parse_svg("""
        <svg>
            <g id="a"><rect id="b"/></g>
            <rect id="c"/>
        </svg>
    """)

    assert [element.id for element in svg.find_all()] == ["a", "b", "c"]


def test_find_returns_the_first_element_in_document_order() -> None:
    svg = parse_svg("""
        <svg>
            <g><rect id="first"/></g>
            <rect id="second"/>
        </svg>
    """)

    assert svg.find(Rect).id == "first"


def test_duplicate_id_resolves_to_the_first_element() -> None:
    svg = parse_svg("""
        <svg>
            <g><rect id="r" fill="lime"/></g>
            <rect id="r" fill="red"/>
            <use href="#r"/>
        </svg>
    """)
    use = svg.find(Use)

    assert use.href is not None
    assert svg.resolve_iri(use.href).fill == Color("lime")
