import pytest

from svglab import G, Rect


def test_get_child_index_compares_by_identity() -> None:
    first, second, third = Rect(), Rect(), Rect()
    assert first == second == third

    g = G().add_children(first, second, third)

    assert g.get_child_index(first) == 0
    assert g.get_child_index(second) == 1
    assert g.get_child_index(third) == 2


def test_get_child_index_honors_start_and_stop() -> None:
    first, second = Rect(), Rect()
    g = G().add_children(first, second)

    assert g.get_child_index(second, 1) == 1

    with pytest.raises(ValueError, match="not found"):
        g.get_child_index(second, 0, 1)
