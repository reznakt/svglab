#!/usr/bin/env python3

# ruff: noqa: T201

import sys

from svglab import (
    CData,
    Comment,
    G,
    Path,
    Polyline,
    RawText,
    Rect,
    parse_svg,
)
from svglab.attrparse import Color, D, Length, Point, SkewX, Translate
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
                stroke="red"
              />
              <rect color="hsl(0, 100%, 100%)"/>
              <!-- This is a comment -->
              <![CDATA[.background { fill: blue; }]]>
              Hello SVG!
              <path d="M 10,10 H 10 L 100,100 Q 100,100 50,50 v 100 Z"/>
              <polygon points="0,0 100,0 100,100 0,100"/>
          </g>
        </svg>
    """
    )

    print(svg)

    # Create an element programmatically
    group = G().add_children(
        Rect(
            width=Length(15, "px"),
            height=Length(20),
            transform=[SkewX(45.123), Translate(10, 20)],
            color=Color("#ff0000"),
        ),
        Comment("This is a comment"),
        CData(".background { fill: blue; }"),
        RawText("Hello SVG!"),
        Path(
            d=D()
            .move_to(Point(10, 10))
            .line_to(Point(100, 100))
            .quadratic_bezier_to(Point(100, 100), Point(50, 50))
            .move_to(Point(50, 50))
            .cubic_bezier_to(
                Point(100, 100), Point(100, 100), Point(10, 10)
            )
            .arc_to(
                Point(50, 50), 90, Point(100, 100), large=True, sweep=False
            )
            .vertical_line_to(100)
            .horizontal_line_to(-10, relative=True)
            .close()
        ),
        Polyline(
            points=[
                Point(0, 0),
                Point(100, 0),
                Point(100, 100),
                Point(0, 100),
            ],
            stroke_linecap="square",
            opacity=0.5,
        ),
    )

    # Add the element to the SVG
    svg.add_child(group)

    # Manipulate attributes
    print(svg.xmlns)  # http://www.w3.org/2000/svg
    svg.x = Length(10, "px")

    # Save to a file
    svg.save(sys.stdout)

    print(svg.find(G).find(Rect).width)
    print(*svg.find_all(Rect), sep="\n")


if __name__ == "__main__":
    main()
