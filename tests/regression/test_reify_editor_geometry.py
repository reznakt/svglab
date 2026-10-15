"""Inkscape rebuilds a shape from its own attributes when it opens a file.

A path carrying `sodipodi:type="arc"` and its radii, or `inkscape:original-d`
with a path effect, is regenerated from those when Inkscape loads it, so
rewriting its `d` would be thrown away there.
"""

import pytest

from svglab import Path, parse_svg


@pytest.mark.parametrize(
    "attrs",
    [
        'sodipodi:type="arc" sodipodi:cx="50" sodipodi:rx="20"',
        'inkscape:original-d="M0 0 L50 50" inkscape:path-effect="#e"',
    ],
    ids=["sodipodi", "path-effect"],
)
def test_geometry_an_editor_regenerates_keeps_the_transform(
    attrs: str,
) -> None:
    svg = parse_svg(f"""
        <svg width="200" height="200"
             xmlns:sodipodi="http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd"
             xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape">
            <path d="M0 0 L50 50" {attrs} transform="translate(10 10)"/>
        </svg>
    """)

    svg.reify()

    assert svg.find(Path).transform is not None
