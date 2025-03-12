import abc
import sys

from typing_extensions import Protocol, TypeVar, cast

from svglab import errors, graphics, models, utils
from svglab.attrparse import d, length, transform
from svglab.attrs import common as common_attrs
from svglab.attrs import groups, presentation, regular
from svglab.elements import common


_T = TypeVar("_T")
_TransformT1 = TypeVar("_TransformT1", bound=transform.TransformFunction)
_TransformT2 = TypeVar("_TransformT2", bound=transform.TransformFunction)


def swap_transforms(
    a: _TransformT1, b: _TransformT2, /
) -> tuple[_TransformT2, _TransformT1]:
    """Swap transforms, adjusting parameters so that the result is equal.

    Args:
        a: The first transform.
        b: The second transform.

    Returns:
        A 2-tuple (b', a') where b' and a' are the adjusted transforms.

    Raises:
        SvgTransformSwapError: If the transforms cannot be swapped.

    Examples:
        >>> from svglab.attrparse.transform import Scale, Translate, SkewX
        >>> swap_transforms(Translate(10, 20), Scale(2, 3))
        (Scale(sx=2.0, sy=3.0), Translate(tx=5.0, ty=6.666666666666667))
        >>> swap_transforms(Scale(2, 3), SkewX(45))
        (SkewX(angle=33.690067525979785), Scale(sx=2.0, sy=3.0))
        >>> swap_transforms(SkewX(45), Translate(10, 20))
        (Translate(tx=30.0, ty=20.0), SkewX(angle=45.0))

    """
    match a, b:
        # transformations of the same type
        case (transform.Translate(), transform.Translate()) | (
            transform.Scale(),
            transform.Scale(),
        ):
            return b, a

        # translate <-> scale
        case transform.Translate(tx, ty), transform.Scale(sx, sy) as scale:
            return scale, type(a)(tx / sx, ty / sy)

        case transform.Scale(sx, sy) as scale, transform.Translate(tx, ty):
            return type(b)(sx * tx, sy * ty), scale

        # translate <-> rotate
        case transform.Rotate(angle, cx, cy), transform.Translate(tx, ty):
            return type(b)(tx, ty), type(a)(angle, cx - tx, cy - ty)
        case transform.Translate(tx, ty), transform.Rotate(angle, cx, cy):
            return type(b)(angle, cx + tx, cy + ty), type(a)(tx, ty)

        # scale <-> rotate
        case transform.Rotate(angle, cx, cy), transform.Scale(
            sx, sy
        ) as scale:
            return scale, type(a)(angle, cx / sx, cy / sy)
        case transform.Scale(sx, sy) as scale, transform.Rotate(
            angle, cx, cy
        ):
            return type(b)(angle, cx * sx, cy * sy), scale

        # translate <-> skew
        case transform.SkewX(angle) as skew_x, transform.Translate(tx, ty):
            return type(b)(tx + ty * utils.tan(angle), ty), skew_x

        case transform.Translate(tx, ty), transform.SkewX(angle) as skew_x:
            return skew_x, type(a)(tx - ty * utils.tan(angle), ty)

        case transform.SkewY(angle) as skew_y, transform.Translate(tx, ty):
            return type(b)(tx, ty + tx * utils.tan(angle)), skew_y

        case transform.Translate(tx, ty), transform.SkewY(angle) as skew_y:
            return skew_y, type(a)(tx, ty - tx * utils.tan(angle))

        # scale <-> skew
        case transform.Scale(sx, sy) as scale, transform.SkewX(angle):
            if utils.is_close(sx, sy):
                return b, a

            angle = utils.arctan(sx / sy * utils.tan(angle))
            return type(b)(angle), scale

        case transform.SkewX(angle), transform.Scale(sx, sy) as scale:
            if utils.is_close(sx, sy):
                return b, a

            angle = utils.arctan(sy / sx * utils.tan(angle))
            return scale, type(a)(angle)

        case transform.Scale(sx, sy) as scale, transform.SkewY(angle):
            if utils.is_close(sx, sy):
                return b, a

            angle = utils.arctan(sy / sx * utils.tan(angle))
            return type(b)(angle), scale

        case transform.SkewY(angle), transform.Scale(sx, sy) as scale:
            if utils.is_close(sx, sy):
                return b, a

            angle = utils.arctan(sx / sy * utils.tan(angle))

            return scale, type(a)(angle)
        case _:
            raise errors.SvgTransformSwapError(a, b)


def _move_transformation_to_end(
    transform: transform.Transform, index: int
) -> None:
    """Move a transformation to the end of the transform list.

    This function moves a transformation from the given index to the end of
    the list, swapping it with each transformation that follows it.
    The transformations in the list are adjusted so that the result is the
    same. The transformation itself may have its parameters adjusted as well.

    Args:
        transform: A list of transformations.
        index: The index of the transformation to move.

    Raises:
        ValueError: If the index is out of range.
        SvgTransformSwapError: If two transformations cannot be swapped.

    Examples:
        >>> from svglab.attrparse.transform import Translate, Scale
        >>> transform = [Translate(10, 20), Scale(2, 3)]
        >>> _move_transformation_to_end(transform, 0)
        >>> transform
        [Scale(sx=2.0, sy=3.0), Translate(tx=5.0, ty=6.666666666666667)]

    """
    if not (0 <= index < len(transform)):
        msg = f"Index {index=} out of range"
        raise ValueError(msg)

    for i in range(index, len(transform) - 1):
        transform[i], transform[i + 1] = swap_transforms(
            transform[i], transform[i + 1]
        )


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
    >>> from svglab import Length
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
    >>> from svglab import Length
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


# pyright goes nuts if `tag` is annotated as `Element`... seems like a bug
# luckily we don't really care
def _translate(tag: object, translate: transform.Translate) -> None:
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

    # but these are not, so if they are not present, we initialize them
    # to 0
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


def _scale_distance_along_a_path_attrs(tag: object, by: float) -> None:
    if isinstance(tag, presentation.StrokeDasharray) and isinstance(
        tag.stroke_dasharray, list
    ):
        tag.stroke_dasharray = [
            _scale_attr(dash, by) for dash in tag.stroke_dasharray
        ]
    if isinstance(tag, presentation.StrokeDashoffset):
        tag.stroke_dashoffset = _scale_attr(tag.stroke_dashoffset, by)


# common attributes are defined directly on the Tag class
class Element(common.Tag):
    pass


class _GraphicalOperations(Element):
    def get_bbox(
        self, *, visible_only: bool = False
    ) -> graphics.BBox | None:
        """Compute the bounding box of this element.

        The bounding box is the smallest rectangle that contains the entire
        element. If the element is not visible, the bounding box is `None`.

        Args:
            visible_only: If `True`, only the visible parts of the element are
                considered when computing the bounding box. If `False`, the
                bounding box includes all parts of the element (even if they
                are transparent).

        Returns:
            The bounding box of the element, or `None` if the element is not
            visible. The bounding box is a tuple of the form `(x_min, y_min,
            x_max, y_max)`.

        """
        return (
            graphics.visible_bbox(self)
            if visible_only
            else graphics.bbox(self)
        )

    def get_mask(
        self,
        *,
        visible_only: bool = False,
        width: float | None = None,
        height: float | None = None,
    ) -> graphics.Mask:
        """Create a mask of this element.

        A mask is a 2D boolean array with `True` values where the tag is
        located (or visible) in the rendered SVG and `False` values elsewhere.

        Args:
            tag: The tag to create a mask for.
            visible_only: If `True`, only the visible parts of the tag are
                included in the mask. If `False`, the mask includes all parts
                of the tag (even if they are transparent).
            width: The width of the mask. If `None`, the width of the root
                SVG tag in the tree is used.
            height: The height of the mask. If `None`, the height of the root
                SVG tag in the tree is used.

        Returns:
            A 2D boolean array representing the mask of the tag.

        """
        return (
            graphics.visible_mask(self, width=width, height=height)
            if visible_only
            else graphics.mask(self, width=width, height=height)
        )


class GraphicsElement(
    _GraphicalOperations, groups.GraphicalEvents, Element
):
    pass


def _scale_stroke_width(tag: presentation.StrokeWidth, by: float) -> None:
    if (
        isinstance(tag, presentation.VectorEffect)
        and tag.vector_effect == "non-scaling-stroke"
    ):
        return

    sw_set = tag.stroke_width is not None

    if not sw_set and not isinstance(tag, GraphicsElement):
        return

    if not sw_set:
        tag.stroke_width = length.Length(1)

    tag.stroke_width = _scale_attr(tag.stroke_width, by)  # type: ignore[reportAttributeAccessIssue]

    # if stroke-width was not set and the scaled value is 1 (default),
    # remove the attribute
    if (
        not sw_set
        and isinstance(tag.stroke_width, length.Length)
        and utils.is_close(float(tag.stroke_width), 1)
    ):
        tag.stroke_width = None


def _scale(tag: object, scale: transform.Scale) -> None:
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
    if isinstance(tag, common_attrs.FontSize):
        tag.font_size = _scale_attr(tag.font_size, factor)
    if isinstance(tag, regular.Points) and tag.points is not None:
        tag.points = [scale @ point for point in tag.points]
    if isinstance(tag, regular.D) and tag.d is not None:
        tag.d = scale @ tag.d

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

    if isinstance(tag, presentation.StrokeWidth):
        _scale_stroke_width(tag, factor)

    # no need to scale distance-along-a-path attributes if a custom path
    # length is provided because those attributes and pathLength are
    # proportional
    if not isinstance(tag, regular.PathLength):
        _scale_distance_along_a_path_attrs(tag, factor)


class SupportsTransform(Element, regular.Transform):
    def __apply_transformation(
        self, transformation: transform.TransformFunction, /
    ) -> None:
        """Apply a transformation to the attributes of the tag.

        Args:
        transformation: The transformation to apply.

        Raises:
        ValueError: If the transformation is not supported.
        SvgLengthConversionError: If a length attribute is not convertible
        to user units.

        """
        match transformation:
            case transform.Translate():
                _translate(self, transformation)
            case transform.Scale():
                _scale(self, transformation)
            case _:
                msg = f"Unsupported transformation: {transformation}"
                raise ValueError(msg)

    def __reify_this(self, *, limit: int) -> None:
        if limit < 0:
            raise ValueError("Limit must be a positive integer")

        if not self.transform:
            return

        reified = 0
        i = 0

        while reified < limit and i < len(self.transform):
            if not isinstance(self.transform[i], transform.Reifiable):
                i += 1
                continue

            try:
                # move the transformation to the end of the list where it can
                # be directly applied to the element
                _move_transformation_to_end(self.transform, i)
                transformation = self.transform.pop()

                self.__apply_transformation(transformation)

                for child in self._find_children(SupportsTransform):
                    if child.transform is None:
                        child.transform = []

                    child.transform.insert(0, transformation)
                    child.reify(limit=1, recursive=False)
            except (ValueError, errors.SvgTransformSwapError) as e:
                raise errors.SvgReifyError(self.transform) from e

            reified += 1

    def reify(
        self,
        *,
        limit: int = sys.maxsize,
        recursive: bool = True,
        remove_transform_list_if_empty: bool = True,
    ) -> None:
        """Apply transformations defined by the `transform` attribute.

        This method takes the transformations defined by the `transform`
        attribute and applies them directly to the coordinate, length, and
        other attributes of the element. The transformations are applied in
        the order in which they are defined. The result of this operation
        should be a visually identical element with the `transform` attribute
        reduced or removed (depending on the `limit` parameter).

        Only `Translate` and `Scale` transformations are can be reified. If
        the `transform` attribute contains other transformations, their
        parameters are adjusted so that `Translate` and `Scale` transformations
        can be applied. Unsupported transformations are ignored.

        If all transformations are successfully applied, the `transform`
        attribute is removed from the element.

        All length values in the element must be convertible to user units.

        Args:
            limit: The maximum number of transformations to apply. If the
                `transform` attribute contains more transformations than the
                limit, the remaining transformations are kept in the attribute
                and not applied. The limit must be a positive integer and is
                applied on a per-element basis.
            recursive: If `True`, the method is called recursively on all
                child elements that support reification.
            remove_transform_list_if_empty: If `True`, the `transform`
                attribute is set to `None` if the list is empty after
                reification.

        Raises:
            ValueError: If the limit is not a positive integer.
            SvgReifyError: If the `transform` attribute cannot be reified.
            SvgUnitConversionError: If a length value cannot be converted to
                user units.

        Examples:
            >>> from svglab import Rect, Length, Translate
            >>> rect = Rect(
            ...     x=Length(10),
            ...     y=Length(20),
            ...     width=Length(20),
            ...     height=Length(40),
            ...     transform=[Translate(5, 5)],
            ... )
            >>> rect.reify()
            >>> rect.x
            Length(value=15.0, unit=None)
            >>> rect.y
            Length(value=25.0, unit=None)
            >>> rect.width
            Length(value=20.0, unit=None)
            >>> rect.height
            Length(value=40.0, unit=None)
            >>> rect.transform is None
            True

        """
        self.__reify_this(limit=limit)

        if remove_transform_list_if_empty and not self.transform:
            self.transform = None

        if recursive:
            for child in self._find_children(SupportsTransform):
                child.reify(limit=limit, recursive=True)


class Shape(regular.PathLength, SupportsTransform, GraphicsElement):
    def set_path_length(self, value: float) -> None:
        """Set a new value for the `pathLength` attribute.

        This method sets a new value for the `pathLength` attribute and scales
        the shape's `stroke-dasharray` and `stroke-dashoffset` attributes
        so that the visual appearance of the shape remains unchanged.

        The shape must have the `pathLength` attribute defined. The `Length`
        values of the scaled attributes must be either in percentages (`%`) or
        convertible to user units. Percentage values are not scaled.

        Args:
            value: The new value for the `pathLength` attribute. Must be
                positive.

        Raises:
            ValueError: If the `value` is not positive.
            RuntimeError: If the current path length is `None`.
            SvgUnitConversionError: If the attribute values cannot be converted
                to user units.

        """
        if value <= 0:
            raise ValueError("Path length must be positive")

        if self.pathLength is None:
            raise RuntimeError("Current pathLength must not be None")

        ratio = value / self.pathLength
        _scale_distance_along_a_path_attrs(self, ratio)

        self.pathLength = value


class _PathLike(Protocol):
    d: models.Attr[d.D]


class BasicShape(Shape, metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def to_d(self) -> d.D:
        """Convert this basic shape into path data.

        The resulting path data produce the same visual result as the original
        basic shape.

        Returns:
            A `D` instance representing the path data.

        """
        ...

    @abc.abstractmethod
    def to_path(self) -> _PathLike:
        """Convert this basic shape into a `Path` element.

        The resulting `Path` element's path data produce the same visual result
        as the original basic shape. The `Path` element will have the same
        attributes as the original basic shape.

        Returns:
            A `Path` element representing the basic shape.

        """
        ...


class AnimationElement(
    groups.AnimationEvents, groups.AnimationTiming, Element
):
    pass


class ContainerElement(
    _GraphicalOperations, groups.GraphicalEvents, Element
):
    pass


class DescriptiveElement(Element):
    pass


class FilterPrimitiveElement(groups.FilterPrimitives, Element):
    pass


class GradientElement(Element):
    pass


class GraphicsReferencingElement(Element):
    pass


class LightSourceElement(Element):
    pass


class StructuralElement(Element):
    pass


class TextContentElement(GraphicsElement):
    pass


class TextContentChildElement(Element):
    pass


class TextContentBlockElement(Element):
    pass
