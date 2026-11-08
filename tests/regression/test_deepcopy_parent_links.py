"""A deep copy keeps its parent links within the copy."""

import copy

from svglab import Element, G, Rect, Svg, parse_svg
from svglab.entities import referenced_elements


def _svg() -> Svg:
    return parse_svg(
        '<svg xmlns="http://www.w3.org/2000/svg" width="10" height="10">'
        '<g><rect width="5" height="5">'
        '<animate attributeName="x" to="5" dur="1s"/></rect>text</g></svg>'
    )


def _assert_linked(element: Element) -> None:
    for child in element.children:
        assert child.parent is element

        if isinstance(child, Element):
            _assert_linked(child)


def test_every_parent_link_points_into_the_copy() -> None:
    original = _svg()

    copied = copy.deepcopy(original)

    assert copied.parent is None
    _assert_linked(copied)
    _assert_linked(original)
    assert copied.find(Rect) is not original.find(Rect)


def test_a_copied_subtree_is_detached() -> None:
    original = _svg()
    group = original.find(G)
    rect = original.find(Rect)

    copied = copy.deepcopy(rect)

    assert copied.parent is None
    _assert_linked(copied)
    assert rect.parent is group
    assert original.find(G) is group


def test_a_parent_copied_after_its_child_adopts_the_copy() -> None:
    original = _svg()
    rect = original.find(Rect)
    group = original.find(G)

    rect_copy, group_copy = copy.deepcopy([rect, group])

    assert rect_copy.parent is group_copy
    assert group_copy.get_child(0) is rect_copy


def test_the_memo_maps_every_element_to_its_copy() -> None:
    original = _svg()
    memo: dict[int, object] = {}

    copied = copy.deepcopy(original, memo)
    rect = original.find(Rect)

    assert memo[id(rect)] is copied.find(Rect)


def test_an_animation_finds_its_target_in_the_copy() -> None:
    copied = copy.deepcopy(_svg())

    assert referenced_elements(copied) == {id(copied.find(Rect))}
