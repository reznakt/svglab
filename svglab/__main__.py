#!/usr/bin/env python3

# ruff: noqa: T201

import sys

from svglab import CData, Comment, G, Rect, Text, parse_svg
from svglab.attrparse.length import Length


def main() -> None:
    # Parse an existing SVG file
    svg = parse_svg(
        """
        <svg xmlns="http://www.w3.org/2000/svg">
            <g>
                <rect id="background" width="100cm" height="100%"/>
                <!-- This is a comment -->
                <![CDATA[.background { fill: blue; }]]>
                Hello SVG!
            </g>
        </svg>
    """
    )

    # Create an element programmatically
    group = G().add_children(
        Rect(x=1, width=Length(15, "px"), height=Length(20)),
        Comment("This is a comment"),
        CData(".background { fill: blue; }"),
        Text("Hello SVG!"),
    )

    # Add the element to the SVG
    svg.add_child(group)

    # Manipulate attributes
    print(svg.xmlns)  # http://www.w3.org/2000/svg
    svg.xmlns = "http://example.com"

    # Save to a file
    svg.save(sys.stdout, indent=4)


if __name__ == "__main__":
    main()
