import pytest

import svglab


@pytest.mark.parametrize("points", [None, []])
def test_polygon_without_points_converts_to_empty_path(
    points: list[svglab.Point] | None,
) -> None:
    polygon = svglab.Polygon(points=points)

    assert len(polygon.to_path_data()) == 0
    assert len(polygon.to_path().d or []) == 0


@pytest.mark.parametrize("points", [None, []])
def test_polyline_without_points_converts_to_empty_path(
    points: list[svglab.Point] | None,
) -> None:
    polyline = svglab.Polyline(points=points)

    assert len(polyline.to_path_data()) == 0
    assert len(polyline.to_path().d or []) == 0


def test_polygon_with_single_point_is_closed() -> None:
    polygon = svglab.Polygon(points=[svglab.Point(1, 2)])
    d = polygon.to_path_data()

    assert len(d) == 2
    assert isinstance(d[-1], svglab.ClosePath)
