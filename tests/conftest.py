import pathlib

import numpy as np
import PIL.Image
import PIL.ImageChops
from typing_extensions import Final

from svglab import (
    Circle,
    Color,
    G,
    Length,
    Line,
    Path,
    PathData,
    Point,
    Polygon,
    Polyline,
    Rect,
    Rotate,
    Scale,
    SkewX,
    SkewY,
    Svg,
    Transform,
    Translate,
)


THIS_DIR: Final = pathlib.Path(__file__).parent
ASSETS_DIR: Final = THIS_DIR / "assets"


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
    original: Svg, new: Svg, *, tolerance: float = 1e-7
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


def complex_svg() -> Svg:
    """Create a complex SVG with various shapes and transformations."""
    svg = Svg(width=Length(1000), height=Length(1000))

    background = Rect(
        width=Length(1000), height=Length(1000), fill=Color("#f0f0f0")
    )
    svg.add_child(background)

    grid = G()

    for i in range(0, 1001, 100):
        grid.add_child(
            Path(
                d=PathData().move_to(Point(0, i)).line_to(Point(1000, i)),
                stroke=Color("#cccccc"),
            )
        )
        grid.add_child(
            Path(
                d=PathData().move_to(Point(i, 0)).line_to(Point(i, 1000)),
                stroke=Color("#cccccc"),
            )
        )
    svg.add_child(grid)

    rect = Rect(
        x=Length(200),
        y=Length(200),
        width=Length(100),
        height=Length(100),
        fill=Color("red"),
        stroke=Color("blue"),
        stroke_width=Length(2),
        transform=[Translate(10, 20), Scale(2), Rotate(45)],
    )
    svg.add_child(rect)

    circle = Circle(
        cx=Length(500),
        cy=Length(500),
        r=Length(100),
        fill=Color("#00ff00"),
        opacity=0.7,
    )
    svg.add_child(circle)

    path = Path(
        d=PathData()
        .move_to(Point(700, 200))
        .line_to(Point(800, 300))
        .cubic_bezier_to(Point(850, 350), Point(900, 300), Point(850, 200))
        .quadratic_bezier_to(Point(800, 150), Point(700, 200))
        .close(),
        fill=Color("#0000ff"),
        stroke=Color("#000000"),
        stroke_width=Length(3),
        transform=[SkewX(15)],
    )
    svg.add_child(path)

    star_points = [
        Point(300, 100),
        Point(350, 200),
        Point(450, 200),
        Point(375, 250),
        Point(400, 350),
        Point(300, 275),
        Point(200, 350),
        Point(225, 250),
        Point(150, 200),
        Point(250, 200),
    ]
    polygon = Polygon(
        points=star_points,
        fill=Color("yellow"),
        stroke=Color("black"),
        stroke_width=Length(2),
    )
    svg.add_child(polygon)

    polyline = Polyline(
        points=[
            Point(100, 600),
            Point(200, 650),
            Point(300, 600),
            Point(400, 650),
            Point(500, 600),
        ],
        stroke=Color("#ff00ff"),
        stroke_width=Length(4),
        fill="none",
        stroke_linecap="round",
        stroke_linejoin="round",
    )
    svg.add_child(polyline)

    rect2 = Rect(
        x=Length(600),
        y=Length(600),
        width=Length(200),
        height=Length(150),
        fill=Color("#ff9900"),
        transform=[Translate(100, 50), SkewY(-20)],
    )
    svg.add_child(rect2)

    group = G(transform=[Translate(100, 700)])

    small_circle1 = Circle(
        cx=Length(50), cy=Length(50), r=Length(30), fill=Color("#993366")
    )
    small_circle2 = Circle(
        cx=Length(150), cy=Length(50), r=Length(30), fill=Color("#336699")
    )
    connecting_line = Line(
        x1=Length(50),
        y1=Length(50),
        x2=Length(150),
        y2=Length(50),
        stroke=Color("black"),
        stroke_width=Length(2),
    )

    group.add_children(small_circle1, small_circle2, connecting_line)
    svg.add_child(group)

    return svg


def nested_svg() -> Svg:
    """Create an SVG with lots of nesting."""
    transform_: Transform = [
        Rotate(-1),
        Scale(1.01),
        SkewX(1),
        Translate(-1, -1),
    ]

    svg = elem = Svg(
        width=Length(1000), height=Length(1000), fill=Color("transparent")
    )

    for _ in range(10):
        group = G(transform=transform_)
        group.add_children(
            Rect(
                width=Length(100),
                height=Length(100),
                stroke=Color("black"),
            ),
            Circle(
                cx=Length(50),
                cy=Length(50),
                r=Length(50),
                stroke=Color("black"),
            ),
            Polygon(
                points=[Point(0, 0), Point(100, 0), Point(50, 100)],
                stroke=Color("black"),
            ),
        )

        elem.add_child(group)
        elem = group

    return svg
