import warnings

import numpy as np

from svglab import elements
from svglab.attrparse import d, length, point, transform


def svg_visually_equal(original: elements.Svg, new: elements.Svg) -> bool:
    """Check if two SVGs are visually equal.

    This function renders the two SVGs and compares the resulting images
    pixel-by-pixel. If the images are not equal, a warning containing the
    XML and data URI representations of the SVGs is raised.

    A warning is also raised if the original SVG is empty, as this may
    indicate an error in the test.

    Args:
    original: The original SVG.
    new: The new SVG.

    Returns:
    `True` if the SVGs are visually equal, `False` otherwise.

    """
    original_img = original.render()
    new_img = new.render()

    if original_img.getbbox() is not None:
        warnings.warn("Original SVG is empty", stacklevel=2)

    equal = np.array_equal(np.asarray(original_img), np.asarray(new_img))

    if not equal:
        lines = [
            "Rendered SVGs are not visually equal:",
            "",
            "Original:",
            original.to_xml(),
            original.to_data_uri(),
            "",
            "New:",
            new.to_xml(),
            new.to_data_uri(),
            "",
        ]

        warnings.warn("\n".join(lines), stacklevel=2)

    return equal


def complex_svg() -> elements.Svg:
    svg = elements.Svg(
        width=length.Length(1000), height=length.Length(1000)
    )

    background = elements.Rect(
        width=length.Length(1000),
        height=length.Length(1000),
        fill="#f0f0f0",
    )
    svg.add_child(background)

    grid = elements.G()

    for i in range(0, 1001, 100):
        grid.add_child(
            elements.Path(
                d=d.D()
                .move_to(point.Point(0, i))
                .line_to(point.Point(1000, i)),
                stroke="#cccccc",
            )
        )
        grid.add_child(
            elements.Path(
                d=d.D()
                .move_to(point.Point(i, 0))
                .line_to(point.Point(i, 1000)),
                stroke="#cccccc",
            )
        )
    svg.add_child(grid)

    rect = elements.Rect(
        x=length.Length(200),
        y=length.Length(200),
        width=length.Length(100),
        height=length.Length(100),
        fill="red",
        stroke="blue",
        stroke_width=length.Length(2),
        transform=[
            transform.Translate(10, 20),
            transform.Scale(2),
            transform.Rotate(45),
        ],
    )
    svg.add_child(rect)

    circle = elements.Circle(
        cx=length.Length(500),
        cy=length.Length(500),
        r=length.Length(100),
        fill="#00ff00",
        opacity=0.7,
    )
    svg.add_child(circle)

    path = elements.Path(
        d=d.D()
        .move_to(point.Point(700, 200))
        .line_to(point.Point(800, 300))
        .cubic_bezier_to(
            point.Point(850, 350),
            point.Point(900, 300),
            point.Point(850, 200),
        )
        .quadratic_bezier_to(point.Point(800, 150), point.Point(700, 200))
        .close(),
        fill="#0000ff",
        stroke="#000000",
        stroke_width=length.Length(3),
        transform=[transform.SkewX(15)],
    )
    svg.add_child(path)

    star_points = [
        point.Point(300, 100),
        point.Point(350, 200),
        point.Point(450, 200),
        point.Point(375, 250),
        point.Point(400, 350),
        point.Point(300, 275),
        point.Point(200, 350),
        point.Point(225, 250),
        point.Point(150, 200),
        point.Point(250, 200),
    ]
    polygon = elements.Polygon(
        points=star_points,
        fill="yellow",
        stroke="black",
        stroke_width=length.Length(2),
    )
    svg.add_child(polygon)

    polyline = elements.Polyline(
        points=[
            point.Point(100, 600),
            point.Point(200, 650),
            point.Point(300, 600),
            point.Point(400, 650),
            point.Point(500, 600),
        ],
        stroke="#ff00ff",
        stroke_width=length.Length(4),
        fill="none",
        stroke_linecap="round",
        stroke_linejoin="round",
    )
    svg.add_child(polyline)

    rect2 = elements.Rect(
        x=length.Length(600),
        y=length.Length(600),
        width=length.Length(200),
        height=length.Length(150),
        fill="#ff9900",
        transform=[transform.Translate(100, 50), transform.SkewY(-20)],
    )
    svg.add_child(rect2)

    group = elements.G(transform=[transform.Translate(100, 700)])

    small_circle1 = elements.Circle(
        cx=length.Length(50),
        cy=length.Length(50),
        r=length.Length(30),
        fill="#993366",
    )
    small_circle2 = elements.Circle(
        cx=length.Length(150),
        cy=length.Length(50),
        r=length.Length(30),
        fill="#336699",
    )
    connecting_line = elements.Path(
        d=d.D().move_to(point.Point(50, 50)).line_to(point.Point(150, 50)),
        stroke="#000000",
        stroke_width=length.Length(2),
    )

    group.add_children(small_circle1, small_circle2, connecting_line)
    svg.add_child(group)

    return svg
