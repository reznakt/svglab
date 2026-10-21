import pytest

from svglab import Circle, Ellipse, Length, Rect


@pytest.mark.parametrize(
    "shape",
    [
        Circle(r=Length(0)),
        Circle(r=Length(-10)),
        Circle(),
        Ellipse(rx=Length(10), ry=Length(0)),
        Ellipse(rx=Length(-10), ry=Length(10)),
    ],
)
def test_disabled_ellipse_converts_to_empty_path(
    shape: Circle | Ellipse,
) -> None:
    assert len(shape.to_path_data()) == 0


@pytest.mark.parametrize(
    "rect",
    [
        Rect(width=Length(0), height=Length(10)),
        Rect(width=Length(10), height=Length(-10)),
        Rect(height=Length(10)),
    ],
)
def test_disabled_rect_converts_to_empty_path(rect: Rect) -> None:
    assert len(rect.to_path_data()) == 0
