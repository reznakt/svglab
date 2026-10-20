from svglab import Formatter, G, Matrix, Path, PathData, Point


def test_matrix_scale_components_use_the_scale_precision() -> None:
    group = G(transform=[Matrix(0.264583, 0, 0, 0.264583, 10.123, 5)])
    formatter = Formatter(general_precision=1, scale_precision=6)

    output = group.to_xml(formatter=formatter)

    assert output == '<g transform="matrix(.264583 0 0 .264583 10.1 5)"/>'


def test_arc_rotation_uses_the_angle_precision() -> None:
    path = Path(
        d=PathData()
        .move_to(Point(0, 0))
        .arc_to(
            Point(10, 5), 12.345, Point(20, 0), large=False, sweep=True
        )
    )
    formatter = Formatter(general_precision=0, angle_precision=2)

    assert "A10,5 12.35 0 1 20,0" in path.to_xml(formatter=formatter)
