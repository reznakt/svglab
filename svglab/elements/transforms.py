from typing_extensions import TypeVar, cast

from svglab import utils
from svglab.attrparse import length, transform
from svglab.attrs import common, presentation, regular


_T = TypeVar("_T")


def _scale_attr(attr: _T, /, by: float) -> _T:
    """Scale an attribute by the given factor.

    This is a helper function for scaling attributes. If the attribute is a
    number or a non-percentage length, it is scaled by the given factor.
    Otherwise, the attribute is left unchanged. If the attribute is a list or
    tuple, the function is applied recursively to each element.

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
        case list() | tuple():
            return type(attr)(_scale_attr(item, by) for item in attr)
        case _:
            return attr


def _translate_attr(attr: _T, /, by: float) -> _T:
    """Translate an attribute by the given amount.

    This is a helper function for translating attributes. If the attribute is
    a number or a non-percentage length, it is translated by the given amount.
    Otherwise, the attribute is left unchanged. If the attribute is a list or
    tuple, the function is applied recursively to each element.

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
        case list() | tuple():
            return type(attr)(_translate_attr(item, by) for item in attr)
        case _:
            return attr


def scale_distance_along_a_path_attrs(tag: object, by: float) -> None:
    if isinstance(tag, presentation.StrokeDasharray) and isinstance(
        tag.stroke_dasharray, list
    ):
        tag.stroke_dasharray = [
            _scale_attr(dash, by) for dash in tag.stroke_dasharray
        ]
    if isinstance(tag, presentation.StrokeDashoffset):
        tag.stroke_dashoffset = _scale_attr(tag.stroke_dashoffset, by)


def scale(tag: object, scale: transform.Scale) -> None:
    if not utils.is_close(scale.sx, scale.sy):
        raise ValueError("Non-uniform scaling is not supported.")

    factor = scale.sx

    if utils.is_close(factor, 1):
        return

    if isinstance(tag, regular.Width):
        tag.width = _scale_attr(tag.width, factor)
    if isinstance(tag, regular.Height):
        tag.height = _scale_attr(tag.height, factor)
    if isinstance(tag, regular.R):
        tag.r = _scale_attr(tag.r, factor)
    if isinstance(tag, regular.X1):
        tag.x1 = _scale_attr(tag.x1, factor)
    if isinstance(tag, regular.Y1):
        tag.y1 = _scale_attr(tag.y1, factor)
    if isinstance(tag, regular.X2):
        tag.x2 = _scale_attr(tag.x2, factor)
    if isinstance(tag, regular.Y2):
        tag.y2 = _scale_attr(tag.y2, factor)
    if isinstance(tag, regular.Rx):
        tag.rx = _scale_attr(tag.rx, factor)
    if isinstance(tag, regular.Ry):
        tag.ry = _scale_attr(tag.ry, factor)
    if isinstance(tag, regular.Cx):
        tag.cx = _scale_attr(tag.cx, factor)
    if isinstance(tag, regular.Cy):
        tag.cy = _scale_attr(tag.cy, factor)
    if isinstance(tag, common.FontSize):
        tag.font_size = _scale_attr(tag.font_size, factor)
    if isinstance(tag, regular.Points) and tag.points is not None:
        tag.points = [scale @ point for point in tag.points]
    if isinstance(tag, regular.D) and tag.d is not None:
        tag.d = scale @ tag.d
    if isinstance(tag, regular.Transform) and tag.transform is not None:
        tag.transform = transform.prepend_transform_list(
            tag.transform, scale
        )
        tag.transform.pop(0)  # TODO: is this correct?

    # these assignments have to be mutually exclusive, because the
    # type checker doesn't know that x being a <number> implies that x is
    # not a <coordinate> and vice versa
    if isinstance(tag, regular.XNumber):  # noqa: SIM114
        tag.x = _scale_attr(tag.x, factor)
    elif isinstance(tag, regular.XCoordinate):
        tag.x = _scale_attr(tag.x, factor)

    if isinstance(tag, regular.YNumber):  # noqa: SIM114
        tag.y = _scale_attr(tag.y, factor)
    elif isinstance(tag, regular.YCoordinate):
        tag.y = _scale_attr(tag.y, factor)

    if (
        not isinstance(tag, presentation.VectorEffect)
        or tag.vector_effect != "non-scaling-stroke"
    ) and isinstance(tag, presentation.StrokeWidth):
        tag.stroke_width = _scale_attr(tag.stroke_width, factor)

    # no need to scale distance-along-a-path attributes if a custom path length
    # is provided because those attributes and pathLength are proportional
    if not isinstance(tag, regular.PathLength):
        scale_distance_along_a_path_attrs(tag, factor)


def translate(tag: object, translate: transform.Translate) -> None:
    tx, ty = translate.tx, translate.ty

    if utils.is_close(tx, 0) and utils.is_close(ty, 0):
        return

    zero = length.Length.zero()

    # these attributes are mandatory for the respective elements
    if isinstance(tag, regular.X1):
        tag.x1 = _translate_attr(tag.x1, tx)
    if isinstance(tag, regular.Y1):
        tag.y1 = _translate_attr(tag.y1, ty)
    if isinstance(tag, regular.X2):
        tag.x2 = _translate_attr(tag.x2, tx)
    if isinstance(tag, regular.Y2):
        tag.y2 = _translate_attr(tag.y2, ty)

    # but these are not, so if they are not present, we initialize them to 0
    if isinstance(tag, regular.Cx):
        tag.cx = _translate_attr(tag.cx or zero, tx)
    if isinstance(tag, regular.Cy):
        tag.cy = _translate_attr(tag.cy or zero, ty)

    if isinstance(tag, regular.XNumber):
        tag.x = _translate_attr(tag.x or 0, tx)
    elif isinstance(tag, regular.XCoordinate):
        tag.x = _translate_attr(tag.x or zero, tx)

    if isinstance(tag, regular.YNumber):
        tag.y = _translate_attr(tag.y or 0, ty)
    elif isinstance(tag, regular.YCoordinate):
        tag.y = _translate_attr(tag.y or zero, ty)

    if isinstance(tag, regular.Points) and tag.points is not None:
        tag.points = [translate @ point for point in tag.points]
    if isinstance(tag, regular.D) and tag.d is not None:
        tag.d = translate @ tag.d
    if isinstance(tag, regular.Transform) and tag.transform is not None:
        tag.transform = transform.prepend_transform_list(
            tag.transform, translate
        )
        tag.transform.pop(0)  # TODO: is this correct?
