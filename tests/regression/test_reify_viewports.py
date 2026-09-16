"""Viewports resize their content only as far as they are told to."""

import copy

import pytest

import svglab
from tests import conftest


L = svglab.Length
C = svglab.Color

_BITMAP = svglab.Iri(
    path=(conftest.ASSETS_DIR / "bitmap.txt").read_text().strip()
)


def _svg(child: svglab.Element, transform: svglab.Transform) -> svglab.Svg:
    return svglab.Svg(
        width=L(240), height=L(240), viewBox=(-40, -40, 240, 240)
    ).add_child(svglab.G(transform=transform).add_child(child))


def _nested(*, viewbox: bool, stretched: bool = False) -> svglab.Svg:
    kwargs: dict[str, object] = {
        "x": L(10),
        "y": L(10),
        "width": L(70),
        "height": L(70),
    }

    if viewbox:
        kwargs["viewBox"] = (0, 0, 100, 50)
    if stretched:
        kwargs["preserveAspectRatio"] = "none"

    inner = svglab.Svg(**kwargs)  # type: ignore[arg-type]

    return inner.add_children(
        svglab.Rect(
            x=L(5), y=L(5), width=L(40), height=L(20), fill=C("#c36")
        ),
        svglab.Circle(cx=L(70), cy=L(25), r=L(15), fill=C("#3c6")),
    )


def _image(*, stretched: bool = False) -> svglab.Image:
    kwargs: dict[str, object] = {
        "x": L(10),
        "y": L(10),
        "width": L(70),
        "height": L(50),
        "href": _BITMAP,
    }

    if stretched:
        kwargs["preserveAspectRatio"] = "none"

    return svglab.Image(**kwargs)  # type: ignore[arg-type]


_UNIFORM = [svglab.Scale(1.4)]
_NON_UNIFORM = [svglab.Scale(1.3, 0.7)]


@pytest.mark.parametrize(
    ("make", "uniform", "non_uniform"),
    [
        # without a viewBox the content keeps its own size, so resizing the
        # viewport would only reveal more of it
        (lambda: _nested(viewbox=False), False, False),
        (lambda: _nested(viewbox=True), True, False),
        (lambda: _nested(viewbox=True, stretched=True), True, True),
        (_image, True, False),
        (lambda: _image(stretched=True), True, True),
    ],
    ids=[
        "nested-svg",
        "nested-svg-viewBox",
        "nested-svg-stretched",
        "image",
        "image-stretched",
    ],
)
def test_a_viewport_is_resized_only_as_far_as_its_content_follows(
    make: object, *, uniform: bool, non_uniform: bool
) -> None:
    for transform, expected in (
        (_UNIFORM, uniform),
        (_NON_UNIFORM, non_uniform),
    ):
        child = make()  # type: ignore[operator]
        original = _svg(child, list(transform))
        reified = copy.deepcopy(original)
        reified.reify()

        inner = reified.find(svglab.G).get_child(0)

        assert isinstance(inner, svglab.Element)
        assert (inner.transform is None) == expected, transform
        conftest.assert_svg_visually_equal(
            original, reified, tolerance=1e-6
        )


def test_an_embedded_bitmap_survives_being_moved_and_resized() -> None:
    original = _svg(
        _image(), [svglab.Translate(12, -7), svglab.Scale(1.4)]
    )
    reified = copy.deepcopy(original)

    reified.reify()

    image = reified.find(svglab.Image)

    assert image.transform is None
    assert image.width == L(98)

    conftest.assert_svg_visually_equal(original, reified)


def test_an_embedded_bitmap_refuses_to_be_turned() -> None:
    # turning a bitmap means turning its pixels, which no attribute says
    original = _svg(_image(), [svglab.Rotate(23)])
    reified = copy.deepcopy(original)

    reified.reify()

    assert reified.find(svglab.Image).transform
    conftest.assert_svg_visually_equal(original, reified)
