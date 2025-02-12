import abc

from typing_extensions import Protocol

from svglab import graphics, models
from svglab.attrparse import d
from svglab.attrs import groups, regular
from svglab.elements import common, transforms


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


class Shape(regular.PathLength, GraphicsElement):
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
        transforms.scale_distance_along_a_path_attrs(self, ratio)

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
