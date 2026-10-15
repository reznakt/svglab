"""A transformation on the outermost svg is a CSS transformation of its box.

It is applied in pixels, after the `viewBox` has been fitted into the box,
and turns about the center of the box unless `transform-origin` says
otherwise. Handing it to the content means expressing it in user units
through the viewBox mapping, and a residue left on the svg is written back
in pixels about the origin.
"""

from svglab import Length, Matrix, Rect, Rotate, Svg, Translate, parse_svg
from svglab.attrparse.transform import compose
from tests.conftest import transforms_left


def test_a_move_in_pixels_is_handed_down_in_user_units() -> None:
    # the viewBox is fitted into the box at twice its size, so fifty pixels
    # are twenty-five user units
    svg = parse_svg("""
        <svg width="200" height="200" viewBox="0 0 100 100"
             transform="translate(50 0)">
            <rect x="10" y="10" width="20" height="20"/>
        </svg>
    """)

    svg.reify()

    assert not transforms_left(svg)
    assert svg.find(Rect).x == Length(35)


def test_the_fitting_of_the_viewbox_is_taken_into_account() -> None:
    # a tall box fits the square viewBox at half its height, centered
    svg = parse_svg("""
        <svg width="100" height="200" viewBox="0 0 100 100"
             transform="translate(0 50)" transform-origin="0 0">
            <rect x="10" y="10" width="20" height="20"/>
        </svg>
    """)

    svg.reify()

    assert not transforms_left(svg)
    assert svg.find(Rect).y == Length(60)


def test_a_residue_is_written_back_in_pixels() -> None:
    svg = parse_svg("""
        <svg width="200" height="200" viewBox="0 0 100 100"
             transform="rotate(90) translate(20 0)" transform-origin="0 0">
            <text x="10" y="10">Reify</text>
        </svg>
    """)

    svg.reify()

    # the text took the move, in user units; the turn stays, in pixels
    assert transforms_left(svg) == [svg]
    assert compose(svg.transform or []) == Rotate(90).to_matrix()
    assert svg.transform_origin == (Length(0), Length(0))


def test_a_root_whose_box_is_not_known_is_left_alone() -> None:
    svg = Svg(
        width=Length(100, "%"),
        viewBox=(0, 0, 100, 100),
        transform=[Translate(10, 0)],
    ).add_child(Rect(width=Length(10), height=Length(10)))

    svg.reify()

    assert svg.transform == [Translate(10, 0)]


def test_a_root_without_a_viewbox_works_in_its_own_units() -> None:
    svg = Svg(
        width=Length(100), height=Length(100), transform=[Translate(10, 0)]
    ).add_child(Rect(width=Length(10), height=Length(10)))

    svg.reify()

    assert not transforms_left(svg)
    assert svg.find(Rect).x == Length(10)
    assert isinstance(compose([Translate(0, 0)]), Matrix)
