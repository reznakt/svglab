from svglab import Circle, Color, G, Image, Length, Rect
from svglab.models import convert


def test_convert_does_not_copy_the_parent() -> None:
    rect = Rect(width=Length(10), height=Length(20))
    group = G().add_child(rect)

    converted = convert(rect, Circle)

    # copying the parent used to deep copy the whole document and leave the
    # converted element attached to a detached copy of the original tree
    assert converted.parent is None
    assert list(group.children) == [rect]


def test_convert_still_copies_regular_fields() -> None:
    rect = Rect(width=Length(10), height=Length(20), fill=Color("red"))

    converted = convert(rect, Image)

    assert converted.width == Length(10)
    assert converted.height == Length(20)
    assert converted.fill == Color("red")
