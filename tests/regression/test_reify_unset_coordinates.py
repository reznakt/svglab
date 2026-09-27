import copy

import pytest

from svglab import Circle, Length, Line, Rect, Svg, parse_svg
from tests.conftest import assert_svg_visually_equal


def _reify(markup: str) -> Svg:
    original = parse_svg(f'<svg width="20" height="20">{markup}</svg>')
    reified = copy.deepcopy(original)
    reified.reify()

    assert_svg_visually_equal(original, reified)

    return reified


@pytest.mark.parametrize(
    ("markup", "names"),
    [
        (
            (
                '<g transform="scale(2)" stroke="red">'
                '<rect width="5" height="5"/></g>'
            ),
            ("x", "y"),
        ),
        ('<circle r="3" transform="scale(2)"/>', ("cx", "cy")),
        (
            '<line x2="5" y2="5" stroke="red" transform="scale(2)"/>',
            ("x1", "y1"),
        ),
    ],
)
def test_coordinates_left_at_the_origin_stay_unset(
    markup: str, names: tuple[str, ...]
) -> None:
    element = next(_reify(markup).find_all(Rect, Circle, Line))

    for name in names:
        assert getattr(element, name) is None
        assert name not in element.model_fields_set


def test_translation_along_one_axis_sets_only_that_axis() -> None:
    rect = _reify(
        '<rect width="5" height="5" transform="translate(0 5)"/>'
    ).find(Rect)

    assert rect.x is None
    assert rect.y == Length(5)


def test_coordinates_that_move_are_written() -> None:
    circle = _reify('<circle r="3" transform="translate(4 5)"/>').find(
        Circle
    )

    assert circle.cx == Length(4)
    assert circle.cy == Length(5)
