import pytest

from svglab import G, Rect


def test_adding_an_ancestor_as_a_child_is_rejected() -> None:
    middle = G().add_child(Rect())
    root = G().add_child(middle)

    with pytest.raises(ValueError, match="ancestor"):
        middle.add_child(root)

    assert root.parent is None
