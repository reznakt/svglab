import pytest

from svglab import ClosePath, Point, Polygon, Polyline


@pytest.mark.parametrize("points", [None, []])
def test_polygon_without_points_converts_to_empty_path(
    points: list[Point] | None,
) -> None:
    polygon = Polygon(points=points)

    assert len(polygon.to_path_data()) == 0
    assert len(polygon.to_path().d or []) == 0


@pytest.mark.parametrize("points", [None, []])
def test_polyline_without_points_converts_to_empty_path(
    points: list[Point] | None,
) -> None:
    polyline = Polyline(points=points)

    assert len(polyline.to_path_data()) == 0
    assert len(polyline.to_path().d or []) == 0


def test_polygon_with_single_point_is_closed() -> None:
    polygon = Polygon(points=[Point(1, 2)])
    d = polygon.to_path_data()

    assert len(d) == 2
    assert isinstance(d[-1], ClosePath)
