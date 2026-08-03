import copy

import pytest

import svglab


def test_get_child_index_compares_by_identity() -> None:
    # elements compare structurally, so all three children are equal
    first, second, third = svglab.Rect(), svglab.Rect(), svglab.Rect()
    assert first == second == third

    g = svglab.G().add_children(first, second, third)

    assert g.get_child_index(first) == 0
    assert g.get_child_index(second) == 1
    assert g.get_child_index(third) == 2


def test_get_child_index_honors_start_and_stop() -> None:
    first, second = svglab.Rect(), svglab.Rect()
    g = svglab.G().add_children(first, second)

    assert g.get_child_index(second, 1) == 1

    with pytest.raises(ValueError, match="not found"):
        g.get_child_index(second, 0, 1)


def test_shallow_copy_of_path_data_does_not_share_commands() -> None:
    original = svglab.PathData.from_str("M 0,0 L 1,1")
    clone = copy.copy(original)

    clone.line_to(svglab.Point(9, 9))

    assert len(original) == 2
    assert len(clone) == 3
