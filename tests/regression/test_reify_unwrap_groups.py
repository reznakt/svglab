import copy

import pytest

import svglab
from svglab import entities
from tests import conftest


def _reify(markup: str, *, unwrap_groups: bool = True) -> svglab.Svg:
    original = svglab.parse_svg(
        f'<svg width="20" height="20">{markup}</svg>'
    )
    reified = copy.deepcopy(original)
    reified.reify(unwrap_groups=unwrap_groups)

    conftest.assert_svg_visually_equal(original, reified)

    return reified


def _names(element: svglab.Element) -> list[str]:
    return [
        entities.element_name(child)
        for child in element.find_all(recursive=False)
    ]


def test_emptied_groups_are_replaced_by_their_children() -> None:
    svg = _reify(
        '<rect width="1" height="1"/>'
        '<g transform="translate(5 5)">'
        '<circle r="1"/>'
        '<g transform="translate(1 1)"><rect width="2" height="2"/></g>'
        '<ellipse rx="1" ry="2"/>'
        "</g>"
        '<line x2="4" stroke="red"/>'
    )

    assert _names(svg) == ["rect", "circle", "rect", "ellipse", "line"]
    assert all(child.parent is svg for child in svg.children)


@pytest.mark.parametrize(
    "markup",
    [
        (
            '<g transform="translate(5 5)" stroke="red">'
            '<rect width="1" height="1"/></g>'
        ),
        (
            '<g transform="translate(5 5)" id="a">'
            '<rect width="1" height="1"/></g>'
        ),
        '<g><rect width="1" height="1"/></g>',
        (
            '<switch><g transform="translate(5 5)">'
            '<rect width="1" height="1"/></g></switch>'
        ),
        (
            "<style>g { opacity: .5 }</style>"
            '<g transform="translate(5 5)"><rect width="1" height="1"/></g>'
        ),
    ],
)
def test_groups_that_matter_are_kept(markup: str) -> None:
    svg = _reify(markup)

    assert list(svg.find_all(svglab.G))


def test_groups_are_kept_by_default() -> None:
    svg = _reify(
        '<g transform="translate(5 5)"><rect width="1" height="1"/></g>',
        unwrap_groups=False,
    )

    assert _names(svg) == ["g"]


def test_the_group_reified_is_kept() -> None:
    svg = svglab.parse_svg(
        '<svg><g transform="translate(5 5)">'
        '<rect width="1" height="1"/></g></svg>'
    )
    group = svg.find(svglab.G)

    group.reify(unwrap_groups=True)

    assert group.parent is svg
    assert group.transform is None
