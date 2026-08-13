import copy

import pytest
from typing_extensions import Final

import svglab
from tests import conftest


_SVGS: Final = [
    """<svg width="200" height="200" viewBox="0 0 200 200">
        <g stroke="black" stroke-width="5" transform="scale(2)">
            <path d="M10,10 L50,50"/>
        </g>
    </svg>""",
    """<svg width="200" height="200" viewBox="0 0 200 200">
        <g stroke="black" stroke-width="5">
            <path d="M10,10 L50,50" transform="scale(2)"/>
        </g>
    </svg>""",
    """<svg width="200" height="200" viewBox="0 0 200 200">
        <g stroke="black" stroke-width="5" transform="scale(2)">
            <g><path d="M10,10 L50,50"/></g>
        </g>
    </svg>""",
    """<svg width="200" height="200" viewBox="0 0 200 200">
        <g stroke="black" stroke-width="5" transform="scale(2)">
            <g stroke-width="3"><path d="M10,10 L50,50"/></g>
        </g>
    </svg>""",
]


@pytest.mark.parametrize("markup", _SVGS)
def test_reify_preserves_inherited_stroke_width(markup: str) -> None:
    original = svglab.parse_svg(markup)
    reified = copy.deepcopy(original)
    reified.reify()

    conftest.assert_svg_visually_equal(original, reified)
