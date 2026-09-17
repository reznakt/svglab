"""The `a` element takes the one `xlink:actuate` value the spec gives it."""

import pytest

import svglab


_NS = (
    'xmlns="http://www.w3.org/2000/svg" '
    'xmlns:xlink="http://www.w3.org/1999/xlink"'
)


def _svg(markup: str) -> str:
    return f'<svg {_NS} width="10" height="10">{markup}</svg>'


def test_a_link_is_actuated_on_request() -> None:
    # `onRequest` is not merely allowed on `a`, it is the only value the
    # specification gives it -- and it was the one value svglab refused,
    # because every referencing element shared the `onLoad` group
    svg = svglab.parse_svg(
        _svg('<a xlink:href="#x" xlink:actuate="onRequest"/>')
    )

    assert svg.find(svglab.A).xlink_actuate == "onRequest"


def test_a_link_is_not_actuated_on_load() -> None:
    with pytest.raises(Exception, match=r"."):
        svglab.parse_svg(
            _svg('<a xlink:href="#x" xlink:actuate="onLoad"/>')
        )


def test_everything_else_is_still_actuated_on_load() -> None:
    svg = svglab.parse_svg(
        _svg(
            '<image xlink:href="#x" xlink:actuate="onLoad"'
            ' width="1" height="1"/>'
        )
    )

    assert svg.find(svglab.Image).xlink_actuate == "onLoad"


def test_everything_else_is_not_actuated_on_request() -> None:
    with pytest.raises(Exception, match=r"."):
        svglab.parse_svg(
            _svg(
                '<image xlink:href="#x" xlink:actuate="onRequest"'
                ' width="1" height="1"/>'
            )
        )
