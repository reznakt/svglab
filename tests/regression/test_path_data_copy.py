import copy

import svglab


def test_shallow_copy_does_not_share_commands() -> None:
    original = svglab.PathData.from_str("M 0,0 L 1,1")
    clone = copy.copy(original)

    clone.line_to(svglab.Point(9, 9))

    assert len(original) == 2
    assert len(clone) == 3
