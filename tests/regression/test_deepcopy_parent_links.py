"""A deep copy keeps its parent links within the copy."""

import copy

import svglab
from svglab import entities


def _svg() -> svglab.Svg:
    return svglab.parse_svg(
        '<svg xmlns="http://www.w3.org/2000/svg" width="10" height="10">'
        '<g><rect width="5" height="5">'
        '<animate attributeName="x" to="5" dur="1s"/></rect>text</g></svg>'
    )


def _assert_linked(element: svglab.Element) -> None:
    for child in element.children:
        assert child.parent is element

        if isinstance(child, svglab.Element):
            _assert_linked(child)


def test_every_parent_link_points_into_the_copy() -> None:
    original = _svg()

    copied = copy.deepcopy(original)

    assert copied.parent is None
    _assert_linked(copied)
    _assert_linked(original)
    assert copied.find(svglab.Rect) is not original.find(svglab.Rect)


def test_a_copied_subtree_is_detached() -> None:
    original = _svg()
    group = original.find(svglab.G)
    rect = original.find(svglab.Rect)

    copied = copy.deepcopy(rect)

    assert copied.parent is None
    _assert_linked(copied)
    assert rect.parent is group
    assert original.find(svglab.G) is group


def test_a_parent_copied_after_its_child_adopts_the_copy() -> None:
    original = _svg()
    rect = original.find(svglab.Rect)
    group = original.find(svglab.G)

    rect_copy, group_copy = copy.deepcopy([rect, group])

    assert rect_copy.parent is group_copy
    assert group_copy.get_child(0) is rect_copy


def test_the_memo_maps_every_element_to_its_copy() -> None:
    original = _svg()
    memo: dict[int, object] = {}

    copied = copy.deepcopy(original, memo)
    rect = original.find(svglab.Rect)

    assert memo[id(rect)] is copied.find(svglab.Rect)


def test_an_animation_finds_its_target_in_the_copy() -> None:
    copied = copy.deepcopy(_svg())

    assert entities.referenced_elements(copied) == {
        id(copied.find(svglab.Rect))
    }
