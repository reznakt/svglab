"""A transformation that is not folded in is left exactly as written.

Working out whether anything can be absorbed takes the `transform-origin`
apart into a pair of translations around the transformation. When nothing
is absorbed after all, that pair used to stay in the list, and grew by
another pair on every pass; the attribute is now put back as it was.
"""

import copy

from svglab import UnknownElement, parse_svg


def test_an_unabsorbable_transform_is_left_as_written() -> None:
    # the nested svg cannot be moved by a fraction of a viewport it does not
    # know, so the outermost svg keeps its transformation
    original = parse_svg("""
        <svg width="400" height="400" transform="translate(100 0)"
             transform-origin="25% 75%">
            <svg x="10%" width="50" height="50">
                <rect width="50" height="50" fill="green"/>
            </svg>
        </svg>
    """)
    reified = copy.deepcopy(original)

    reified.reify()

    assert reified.to_xml() == original.to_xml()


def test_reification_is_idempotent_on_what_it_leaves_behind() -> None:
    original = parse_svg("""
        <svg width="400" height="400" transform="translate(100 0)">
            <svg x="10%" width="50" height="50">
                <rect width="50" height="50" fill="green"/>
            </svg>
        </svg>
    """)
    once = copy.deepcopy(original)
    once.reify()
    twice = copy.deepcopy(once)
    twice.reify()

    assert twice.to_xml() == once.to_xml()


def test_an_unknown_element_neither_takes_nor_blocks_a_transform() -> None:
    # a renderer draws nothing it does not know, so the group's
    # transformation belongs to the rect alone
    original = parse_svg("""
        <svg width="200" height="200"
             xmlns:html="http://www.w3.org/1999/xhtml">
            <g transform="translate(50 50)">
                <html:link rel="help" href="https://example.org/"/>
                <rect width="50" height="50" fill="green"/>
            </g>
        </svg>
    """)
    reified = copy.deepcopy(original)

    reified.reify()

    assert not any(
        e.main_transform for e in (reified, *reified.find_all())
    )
    assert reified.find(UnknownElement)["href"] == "https://example.org/"
