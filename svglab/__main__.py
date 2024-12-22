#!/usr/bin/env python3

# ruff: noqa: T201

import sys

from svglab import CData, Comment, G, RawText, Rect, parse_svg
from svglab.attrs import Color, Length, SkewX, Translate
from svglab.serialize import Formatter, set_formatter


set_formatter(Formatter(indent=4, max_precision=2, color_mode="rgb"))


def main() -> None:
    # Parse an existing SVG file
    svg = parse_svg(
        """
        <svg xmlns="http://www.w3.org/2000/svg">
          <g>
              <rect
                id="background"
                width="100cm"
                height="100%"
                transform="rotate(45)"
              />
              <rect color="hsl(0, 100%, 100%)"/>
              <!-- This is a comment -->
              <![CDATA[.background { fill: blue; }]]>
              Hello SVG!
          </g>
        </svg>
    """
    )

    # Create an element programmatically
    group = G().add_children(
        Rect(
            x=1,
            width=Length(15, "px"),
            height=Length(20),
            transform=[SkewX(45.123), Translate(10, 20)],
            color=Color("#ff0000"),
        ),
        Comment("This is a comment"),
        CData(".background { fill: blue; }"),
        RawText("Hello SVG!"),
    )

    # Add the element to the SVG
    svg.add_child(group)

    # Manipulate attributes
    print(svg.xmlns)  # http://www.w3.org/2000/svg
    svg.xmlns = "http://example.com"

    # Save to a file
    svg.save(sys.stdout)

    print(*svg.find_all(Rect), sep="\n")


if __name__ == "__main__":
    main()
