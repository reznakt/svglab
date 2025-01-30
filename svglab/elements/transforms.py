from typing_extensions import TypeVar, cast

from svglab.attrparse import length, point, transform
from svglab.attrs import presentation, regular


_T = TypeVar("_T")


def _scale_attr(attr: _T, /, by: float) -> _T:
    """Scale an attribute by the given factor.

    This is a helper function for scaling attributes. If the attribute is a
    number or a non-percentage length, it is scaled by the given factor.
    Otherwise, the attribute is left unchanged.

    Args:
    attr: The attribute to scale.
    by: The factor by which to scale the attribute.

    Returns:
    The scaled attribute.

    Examples:
    >>> from svglab.attrparse import Length
    >>> _scale_attr(Length(10), 2)
    Length(value=20.0, unit=None)
    >>> _scale_attr(None, 2) is None
    True
    >>> _scale_attr(Length(10, "%"), 2)
    Length(value=10.0, unit='%')

    """
    match attr:
        case length.Length(_, "%"):
            return attr
        case int() | float() | length.Length():
            return cast(_T, attr * by)
        case _:
            return attr


def _translate_attr(attr: _T, /, by: float) -> _T:
    """Translate an attribute by the given amount.

    This is a helper function for translating attributes. If the attribute is
    a number or a non-percentage length, it is translated by the given amount.
    Otherwise, the attribute is left unchanged.

    Args:
    attr: The attribute to translate.
    by: The amount by which to translate the attribute.

    Returns:
    The translated attribute.

    Examples:
    >>> from svglab.attrparse import Length
    >>> _translate_attr(Length(10), 5)
    Length(value=15.0, unit=None)
    >>> _translate_attr(None, 5) is None
    True
    >>> _translate_attr(Length(10, "%"), 5)
    Length(value=10.0, unit='%')

    """
    match attr:
        case length.Length(_, "%"):
            return attr
        case int() | float():
            return cast(_T, attr + by)
        case length.Length():
            return attr + length.Length(by)
        case _:
            return attr


def scale(tag: object, by: float) -> None:  # noqa: C901, PLR0912
    if isinstance(tag, regular.Width):
        tag.width = _scale_attr(tag.width, by)
    if isinstance(tag, regular.Height):
        tag.height = _scale_attr(tag.height, by)
    if isinstance(tag, regular.R):
        tag.r = _scale_attr(tag.r, by)
    if isinstance(tag, regular.X1):
        tag.x1 = _scale_attr(tag.x1, by)
    if isinstance(tag, regular.Y1):
        tag.y1 = _scale_attr(tag.y1, by)
    if isinstance(tag, regular.X2):
        tag.x2 = _scale_attr(tag.x2, by)
    if isinstance(tag, regular.Y2):
        tag.y2 = _scale_attr(tag.y2, by)
    if isinstance(tag, regular.Rx):
        tag.rx = _scale_attr(tag.rx, by)
    if isinstance(tag, regular.Ry):
        tag.ry = _scale_attr(tag.ry, by)
    if isinstance(tag, regular.Cx):
        tag.cx = _scale_attr(tag.cx, by)
    if isinstance(tag, regular.Cy):
        tag.cy = _scale_attr(tag.cy, by)
    if isinstance(tag, regular.Points) and tag.points is not None:
        tag.points = list(transform.Scale(by) @ tag.points)
    if isinstance(tag, regular.D) and tag.d is not None:
        tag.d = transform.Scale(by) @ tag.d

    # these assignments have to be mutually exclusive, because the
    # type checker doesn't know that x being a <number> implies that x is
    # not a <coordinate> and vice versa
    if isinstance(tag, regular.XNumber):  # noqa: SIM114
        tag.x = _scale_attr(tag.x, by)
    elif isinstance(tag, regular.XCoordinate):
        tag.x = _scale_attr(tag.x, by)

    if isinstance(tag, regular.YNumber):  # noqa: SIM114
        tag.y = _scale_attr(tag.y, by)
    elif isinstance(tag, regular.YCoordinate):
        tag.y = _scale_attr(tag.y, by)

    if (
        not isinstance(tag, presentation.VectorEffect)
        or tag.vector_effect != "non-scaling-stroke"
    ) and isinstance(tag, presentation.StrokeWidth):
        tag.stroke_width = _scale_attr(tag.stroke_width, by)

    # no need to scale distance-along-a-path attributes if a custom path length
    # is provided because those attributes and pathLength are proportional
    if not isinstance(tag, regular.PathLength):
        if isinstance(tag, presentation.StrokeDasharray) and isinstance(
            tag.stroke_dasharray, list
        ):
            tag.stroke_dasharray = [
                _scale_attr(dash, by) for dash in tag.stroke_dasharray
            ]
        if isinstance(tag, presentation.StrokeDashoffset):
            tag.stroke_dashoffset = _scale_attr(tag.stroke_dashoffset, by)


def translate(tag: object, by: point.Point) -> None:  # noqa: C901
    x, y = by

    if isinstance(tag, regular.X1):
        tag.x1 = _translate_attr(tag.x1, x)
    if isinstance(tag, regular.Y1):
        tag.y1 = _translate_attr(tag.y1, y)
    if isinstance(tag, regular.X2):
        tag.x2 = _translate_attr(tag.x2, x)
    if isinstance(tag, regular.Y2):
        tag.y2 = _translate_attr(tag.y2, y)
    if isinstance(tag, regular.Cx):
        tag.cx = _translate_attr(tag.cx, x)
    if isinstance(tag, regular.Cy):
        tag.cy = _translate_attr(tag.cy, y)
    if isinstance(tag, regular.Points) and tag.points is not None:
        tag.points = list(transform.Translate(x, y) @ tag.points)
    if isinstance(tag, regular.D) and tag.d is not None:
        tag.d += by

    if isinstance(tag, regular.XNumber):  # noqa: SIM114
        tag.x = _translate_attr(tag.x, x)
    elif isinstance(tag, regular.XCoordinate):
        tag.x = _translate_attr(tag.x, x)

    if isinstance(tag, regular.YNumber):  # noqa: SIM114
        tag.y = _translate_attr(tag.y, y)
    elif isinstance(tag, regular.YCoordinate):
        tag.y = _translate_attr(tag.y, y)
