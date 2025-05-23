"""Pytest configuration and utilities for testing."""

import numpy as np
import PIL.Image
import PIL.ImageChops

import svglab


def mean_squared_error(a: PIL.Image.Image, b: PIL.Image.Image) -> float:
    """Calculate the mean squared error (MSE) between two images.

    Args:
        a: The first image.
        b: The second image.

    Returns:
        The MSE between the two images. A lower value indicates a closer
        match.

    """
    diff = PIL.ImageChops.difference(a, b)
    errors = np.asarray(diff) / 255

    return float(np.mean(np.square(errors)))


def assert_svg_visually_equal(
    original: svglab.Svg, new: svglab.Svg, *, tolerance: float = 1e-7
) -> None:
    """Check if two SVGs are visually equal.

    This function renders the two SVGs and compares the resulting images
    using the mean squared error (MSE) metric. If the MSE is below the
    specified tolerance, the SVGs are considered visually equal. An exception
    is raised otherwise, containing the MSE and the XML and data URI
    representations of both SVGs.

    An exception is also raised if the original SVG is empty, as this may
    indicate an error in the test.

    Args:
    original: The original SVG.
    new: The new SVG.
    tolerance: The maximum MSE for the SVGs to be considered
        visually equal.

    Raises:
    AssertionError: If the SVGs are not visually equal or the original SVG
    is empty.

    """
    original_img = original.render()
    new_img = new.render()

    if original_img.getbbox() is None:
        msg = f"Original SVG is empty:\n{original.to_xml()}"
        raise AssertionError(msg)

    mse = mean_squared_error(original_img, new_img)

    if mse >= tolerance:
        lines = [
            f"Rendered SVGs are not visually equal ({mse=}):",
            "Original:",
            original.to_xml(),
            original.to_data_uri(),
            "",
            "New:",
            new.to_xml(),
            new.to_data_uri(),
            "",
        ]

        raise AssertionError("\n".join(lines))


def complex_svg() -> svglab.Svg:
    """Create a complex SVG with various shapes and transformations."""
    svg = svglab.Svg(width=svglab.Length(1000), height=svglab.Length(1000))

    background = svglab.Rect(
        width=svglab.Length(1000),
        height=svglab.Length(1000),
        fill=svglab.Color("#f0f0f0"),
    )
    svg.add_child(background)

    grid = svglab.G()

    for i in range(0, 1001, 100):
        grid.add_child(
            svglab.Path(
                d=svglab.PathData()
                .move_to(svglab.Point(0, i))
                .line_to(svglab.Point(1000, i)),
                stroke=svglab.Color("#cccccc"),
            )
        )
        grid.add_child(
            svglab.Path(
                d=svglab.PathData()
                .move_to(svglab.Point(i, 0))
                .line_to(svglab.Point(i, 1000)),
                stroke=svglab.Color("#cccccc"),
            )
        )
    svg.add_child(grid)

    rect = svglab.Rect(
        x=svglab.Length(200),
        y=svglab.Length(200),
        width=svglab.Length(100),
        height=svglab.Length(100),
        fill=svglab.Color("red"),
        stroke=svglab.Color("blue"),
        stroke_width=svglab.Length(2),
        transform=[
            svglab.Translate(10, 20),
            svglab.Scale(2),
            svglab.Rotate(45),
        ],
    )
    svg.add_child(rect)

    circle = svglab.Circle(
        cx=svglab.Length(500),
        cy=svglab.Length(500),
        r=svglab.Length(100),
        fill=svglab.Color("#00ff00"),
        opacity=0.7,
    )
    svg.add_child(circle)

    path = svglab.Path(
        d=svglab.PathData()
        .move_to(svglab.Point(700, 200))
        .line_to(svglab.Point(800, 300))
        .cubic_bezier_to(
            svglab.Point(850, 350),
            svglab.Point(900, 300),
            svglab.Point(850, 200),
        )
        .quadratic_bezier_to(
            svglab.Point(800, 150), svglab.Point(700, 200)
        )
        .close(),
        fill=svglab.Color("#0000ff"),
        stroke=svglab.Color("#000000"),
        stroke_width=svglab.Length(3),
        transform=[svglab.SkewX(15)],
    )
    svg.add_child(path)

    star_points = [
        svglab.Point(300, 100),
        svglab.Point(350, 200),
        svglab.Point(450, 200),
        svglab.Point(375, 250),
        svglab.Point(400, 350),
        svglab.Point(300, 275),
        svglab.Point(200, 350),
        svglab.Point(225, 250),
        svglab.Point(150, 200),
        svglab.Point(250, 200),
    ]
    polygon = svglab.Polygon(
        points=star_points,
        fill=svglab.Color("yellow"),
        stroke=svglab.Color("black"),
        stroke_width=svglab.Length(2),
    )
    svg.add_child(polygon)

    polyline = svglab.Polyline(
        points=[
            svglab.Point(100, 600),
            svglab.Point(200, 650),
            svglab.Point(300, 600),
            svglab.Point(400, 650),
            svglab.Point(500, 600),
        ],
        stroke=svglab.Color("#ff00ff"),
        stroke_width=svglab.Length(4),
        fill="none",
        stroke_linecap="round",
        stroke_linejoin="round",
    )
    svg.add_child(polyline)

    rect2 = svglab.Rect(
        x=svglab.Length(600),
        y=svglab.Length(600),
        width=svglab.Length(200),
        height=svglab.Length(150),
        fill=svglab.Color("#ff9900"),
        transform=[svglab.Translate(100, 50), svglab.SkewY(-20)],
    )
    svg.add_child(rect2)

    group = svglab.G(transform=[svglab.Translate(100, 700)])

    small_circle1 = svglab.Circle(
        cx=svglab.Length(50),
        cy=svglab.Length(50),
        r=svglab.Length(30),
        fill=svglab.Color("#993366"),
    )
    small_circle2 = svglab.Circle(
        cx=svglab.Length(150),
        cy=svglab.Length(50),
        r=svglab.Length(30),
        fill=svglab.Color("#336699"),
    )
    connecting_line = svglab.Line(
        x1=svglab.Length(50),
        y1=svglab.Length(50),
        x2=svglab.Length(150),
        y2=svglab.Length(50),
        stroke=svglab.Color("black"),
        stroke_width=svglab.Length(2),
    )

    group.add_children(small_circle1, small_circle2, connecting_line)
    svg.add_child(group)

    return svg


def nested_svg() -> svglab.Svg:
    """Create an SVG with lots of nesting."""
    transform_: svglab.Transform = [
        svglab.Rotate(-1),
        svglab.Scale(1.01),
        svglab.SkewX(1),
        svglab.Translate(-1, -1),
    ]

    svg = elem = svglab.Svg(
        width=svglab.Length(1000),
        height=svglab.Length(1000),
        fill=svglab.Color("transparent"),
    )

    for _ in range(10):
        group = svglab.G(transform=transform_)
        group.add_children(
            svglab.Rect(
                width=svglab.Length(100),
                height=svglab.Length(100),
                stroke=svglab.Color("black"),
            ),
            svglab.Circle(
                cx=svglab.Length(50),
                cy=svglab.Length(50),
                r=svglab.Length(50),
                stroke=svglab.Color("black"),
            ),
            svglab.Polygon(
                points=[
                    svglab.Point(0, 0),
                    svglab.Point(100, 0),
                    svglab.Point(50, 100),
                ],
                stroke=svglab.Color("black"),
            ),
        )

        elem.add_child(group)
        elem = group

    return svg
