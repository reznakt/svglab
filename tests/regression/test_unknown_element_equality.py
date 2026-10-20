from svglab import UnknownElement, parse_svg


def test_unknown_elements_with_different_names_are_unequal() -> None:
    assert UnknownElement(element_name="foo") != UnknownElement(
        element_name="bar"
    )
    assert parse_svg("<svg><foo/></svg>") != parse_svg("<svg><bar/></svg>")


def test_unknown_elements_with_the_same_name_are_equal() -> None:
    assert UnknownElement(element_name="foo") == UnknownElement(
        element_name="foo"
    )
