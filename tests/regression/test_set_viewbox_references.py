"""`set_viewbox` hands its mapping only to what is drawn where it sits."""

import pytest

import svglab
from svglab import errors
from tests import conftest


_VIEWBOX = (-13.25, 27.5, 200, 200)


def _parse(content: str) -> svglab.Svg:
    # parsed afresh rather than deep-copied, which loses the parent links an
    # animation is resolved through
    return svglab.parse_svg(
        '<svg xmlns="http://www.w3.org/2000/svg" '
        'xmlns:xlink="http://www.w3.org/1999/xlink" '
        f'width="100" height="100" viewBox="0 0 100 100">{content}</svg>'
    )


def _set_viewbox(content: str) -> tuple[svglab.Svg, svglab.Svg]:
    original = _parse(content)
    changed = _parse(content)
    changed.set_viewbox(_VIEWBOX)

    return original, changed


def test_a_top_level_clip_path_is_left_alone() -> None:
    original, changed = _set_viewbox(
        '<clipPath id="c"><circle cx="50" cy="50" r="30"/></clipPath>'
        '<rect x="10" y="10" width="80" height="80" fill="blue" '
        'clip-path="url(#c)"/>'
    )

    assert changed.find(svglab.ClipPath).transform is None
    conftest.assert_svg_visually_equal(original, changed)


def test_defs_are_left_alone() -> None:
    original, changed = _set_viewbox(
        '<defs><rect id="r" width="20" height="20" fill="red"/></defs>'
        '<use href="#r" x="30" y="30"/>'
    )

    assert changed.find(svglab.Defs).transform is None
    conftest.assert_svg_visually_equal(original, changed)


@pytest.mark.parametrize("href", ["href", "xlink:href"])
def test_an_element_a_use_references_is_wrapped(href: str) -> None:
    original, changed = _set_viewbox(
        '<rect id="r" x="10" y="10" width="20" height="20" fill="red" '
        'transform="rotate(10)"/>'
        f'<use {href}="#r" x="40" y="30"/>'
    )
    rect = changed.find(svglab.Rect)

    assert isinstance(rect.parent, svglab.G)
    assert rect.parent.parent is changed
    assert rect.transform == [svglab.Rotate(10)]
    conftest.assert_svg_visually_equal(original, changed)


def test_an_animated_element_is_wrapped() -> None:
    _, changed = _set_viewbox(
        '<rect x="10" y="10" width="20" height="20" fill="red">'
        '<animateTransform attributeName="transform" type="rotate" '
        'from="0" to="360" dur="1s"/></rect>'
    )
    rect = changed.find(svglab.Rect)

    assert isinstance(rect.parent, svglab.G)
    assert rect.transform is None
    assert (rect.x, rect.width) == (svglab.Length(10), svglab.Length(20))


@pytest.mark.parametrize(
    "style", ["transform: rotate(10deg)", "transform-origin: 20px 20px"]
)
def test_an_element_whose_style_sets_its_transform_is_wrapped(
    style: str,
) -> None:
    original, changed = _set_viewbox(
        '<rect x="10" y="10" width="40" height="20" fill="red" '
        f'transform="rotate(30)" style="{style}"/>'
    )
    rect = changed.find(svglab.Rect)

    assert isinstance(rect.parent, svglab.G)
    assert rect.transform == [svglab.Rotate(30)]
    conftest.assert_svg_visually_equal(original, changed)


def test_an_origin_relative_to_the_viewbox_is_refused() -> None:
    # `center` is the middle of the viewBox being replaced, so no
    # transformation of the element alone keeps it where it was
    svg = _parse(
        '<rect x="10" y="10" width="40" height="20" fill="red" '
        'transform="rotate(30)" transform-origin="center"/>'
    )

    with pytest.raises(errors.SvgTransformOriginError):
        svg.set_viewbox(_VIEWBOX)
