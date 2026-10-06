import svglab
from svglab import models


def test_convert_does_not_copy_the_parent() -> None:
    rect = svglab.Rect(width=svglab.Length(10), height=svglab.Length(20))
    group = svglab.G().add_child(rect)

    converted = models.convert(rect, svglab.Circle)

    # copying the parent used to deep copy the whole document and leave the
    # converted element attached to a detached copy of the original tree
    assert converted.parent is None
    assert list(group.children) == [rect]


def test_convert_still_copies_regular_fields() -> None:
    rect = svglab.Rect(
        width=svglab.Length(10),
        height=svglab.Length(20),
        fill=svglab.Color("red"),
    )

    converted = models.convert(rect, svglab.Image)

    assert converted.width == svglab.Length(10)
    assert converted.height == svglab.Length(20)
    assert converted.fill == svglab.Color("red")
