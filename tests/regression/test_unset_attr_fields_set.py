import svglab
from svglab import Length, Rect


def test_setting_an_attribute_to_none_unsets_it() -> None:
    rect = Rect(x=Length(1), y=Length(2))
    rect.y = None

    assert "y" not in rect.model_fields_set
    assert "x" in rect.model_fields_set


def test_deleting_an_attribute_unsets_it() -> None:
    rect = Rect(x=Length(1), y=Length(2))
    del rect.x

    assert "x" not in rect.model_fields_set
    assert "y" in rect.model_fields_set


def test_reify_unsets_the_transform_it_removes() -> None:
    svg = svglab.parse_svg(
        '<svg xmlns="http://www.w3.org/2000/svg">'
        '<g transform="translate(5 5)"><rect width="1" height="1"/></g>'
        "</svg>"
    )
    svg.reify()
    group = svg.find("g")

    assert group.transform is None
    assert "transform" not in group.model_fields_set
