import copy

from svglab import PathData, Point


def test_shallow_copy_does_not_share_commands() -> None:
    original = PathData.from_str("M 0,0 L 1,1")
    clone = copy.copy(original)

    clone.line_to(Point(9, 9))

    assert len(original) == 2
    assert len(clone) == 3
