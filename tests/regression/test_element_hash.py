from svglab import parse_svg


def test_elements_with_list_valued_attributes_are_hashable() -> None:
    markup = """
        <svg>
            <path d="M0 0" class="a b" transform="scale(2)"/>
            <polyline points="0,0 1,1" stroke-dasharray="1 2"/>
        </svg>
    """

    assert hash(parse_svg(markup)) == hash(parse_svg(markup))
