from svglab import Formatter, G, Matrix


def test_matrix_scale_components_use_the_scale_precision() -> None:
    group = G(transform=[Matrix(0.264583, 0, 0, 0.264583, 10.123, 5)])
    formatter = Formatter(general_precision=1, scale_precision=6)

    output = group.to_xml(formatter=formatter)

    assert output == '<g transform="matrix(.264583 0 0 .264583 10.1 5)"/>'
