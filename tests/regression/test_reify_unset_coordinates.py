import copy

import pytest

import svglab
from tests import conftest


def _reify(markup: str) -> svglab.Svg:
    original = svglab.parse_svg(
        f'<svg width="20" height="20">{markup}</svg>'
    )
    reified = copy.deepcopy(original)
    reified.reify()

    conftest.assert_svg_visually_equal(original, reified)

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
    element = next(
        _reify(markup).find_all(svglab.Rect, svglab.Circle, svglab.Line)
    )

    for name in names:
        assert getattr(element, name) is None
        assert name not in element.model_fields_set


def test_translation_along_one_axis_sets_only_that_axis() -> None:
    rect = _reify(
        '<rect width="5" height="5" transform="translate(0 5)"/>'
    ).find(svglab.Rect)

    assert rect.x is None
    assert rect.y == svglab.Length(5)


def test_coordinates_that_move_are_written() -> None:
    circle = _reify('<circle r="3" transform="translate(4 5)"/>').find(
        svglab.Circle
    )

    assert circle.cx == svglab.Length(4)
    assert circle.cy == svglab.Length(5)
