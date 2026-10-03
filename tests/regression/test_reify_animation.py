"""An animation records values reification must not rewrite underneath it."""

import pytest

import svglab


L = svglab.Length


def _rect(**kwargs: object) -> svglab.Rect:
    kwargs.setdefault("x", L(10))
    kwargs.setdefault("y", L(10))
    kwargs.setdefault("width", L(20))
    kwargs.setdefault("height", L(20))

    return svglab.Rect(**kwargs)  # type: ignore[arg-type]


def _svg(*children: svglab.Element) -> svglab.Svg:
    return svglab.Svg(width=L(100), height=L(100)).add_children(*children)


@pytest.mark.parametrize(
    "animation",
    [
        svglab.AnimateTransform(
            attributeName="transform", type="translate", values="0 0; 20 0"
        ),
        svglab.Animate(attributeName="x", values="10; 40"),
        svglab.Animate(attributeName="width", values="20; 40"),
        svglab.Animate(attributeName="stroke-width", values="1; 4"),
        svglab.Set(attributeName="d", to="M 0,0 L 1,1"),
    ],
    ids=lambda a: str(a.attributeName or "transform"),
)
def test_an_animated_geometry_attribute_freezes_the_element(
    animation: svglab.Element,
) -> None:
    rect = _rect(transform=[svglab.Translate(5, 5)])
    rect.add_child(animation)
    _svg(rect)

    rect.reify()

    assert rect.transform == [svglab.Translate(5, 5)]
    assert rect.x == L(10)


def test_an_animation_of_something_else_does_not_freeze_the_element() -> (
    None
):
    rect = _rect(transform=[svglab.Translate(5, 5)])
    rect.add_child(
        svglab.Animate(attributeName="fill", values="red; blue")
    )
    _svg(rect)

    rect.reify()

    assert rect.transform is None
    assert rect.x == L(15)


def test_an_animation_freezes_the_element_it_points_at() -> None:
    rect = _rect(id="r", transform=[svglab.Translate(5, 5)])
    svg = _svg(
        rect,
        svglab.Animate(
            href=svglab.Iri(fragment="r"),
            attributeName="width",
            values="20; 40",
        ),
    )

    svg.reify()

    assert rect.transform == [svglab.Translate(5, 5)]


def test_nothing_is_pushed_into_an_animated_child() -> None:
    # the animation replaces the transform attribute outright, so anything
    # pushed into it would simply be dropped when the animation begins
    rect = _rect()
    rect.add_child(
        svglab.AnimateTransform(
            attributeName="transform", type="rotate", values="0; 90"
        )
    )
    group = svglab.G(transform=[svglab.Translate(5, 5)]).add_child(rect)
    svg = _svg(group)

    svg.reify()

    assert group.transform == [svglab.Translate(5, 5)]
    assert rect.transform is None
    assert rect.x == L(10)
