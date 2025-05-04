"""Useful traits for SVG elements.

Traits are mixins that are used to add common functionality to SVG elements.

For example, we want to be able to normalize the `pathLength` attribute of
all shapes in SVG. Therefore, the `Shape` trait contains the `set_path_length`
method. Elements that are shapes inherit from the `Shape` trait and therefore
automatically have the `set_path_length` method.

This approach allows us to define common functionality in one place and reuse
it on different elements.

Most traits are defined based on the "1.6 Definitions" section of the SVG 1.1
specification.
"""

import abc

from typing_extensions import Protocol

from svglab import graphics, models, xml
from svglab.attrparse import path_data
from svglab.attrs import attrdefs, attrgroups


# common attributes are defined directly on the Element class
class Element(xml.Element):
    """An SVG element."""


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

        A mask is a 2D boolean array with `True` values where the element is
        located (or visible) in the rendered SVG and `False` values elsewhere.

        Args:
            element: The element to create a mask for.
            visible_only: If `True`, only the visible parts of the element are
                included in the mask. If `False`, the mask includes all parts
                of the element (even if they are transparent).
            width: The width of the mask. If `None`, the width of the root
                SVG element in the tree is used.
            height: The height of the mask. If `None`, the height of the root
                SVG element in the tree is used.

        Returns:
            A 2D boolean array representing the mask of the element.

        """
        return (
            graphics.visible_mask(self, width=width, height=height)
            if visible_only
            else graphics.mask(self, width=width, height=height)
        )


class GraphicsElement(
    _GraphicalOperations,
    attrgroups.GraphicalEventsAttrs,
    xml.StrokeWidthScaled,
    Element,
):
    """A graphics element.

    From the SVG 1.1 specification:
    > "One of the element types that can cause graphics to be drawn onto the
    target canvas."
    """


class Shape(attrdefs.PathLengthAttr, GraphicsElement):
    """A shape.

    From the SVG 1.1 specification:
    > "A graphics element that is defined by some combination of straight lines
    and curves."
    """

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
        xml.scale_distance_along_a_path_attrs(self, ratio)

        self.pathLength = value


class _PathLike(Protocol):
    d: models.Attr[path_data.PathData]


class BasicShape(Shape, metaclass=abc.ABCMeta):
    """A basic shape.

    From the SVG 1.1 specification:
    > "Standard shapes which are predefined in SVG as a convenience for common
    graphical operations."
    """

    @abc.abstractmethod
    def to_d(self) -> path_data.PathData:
        """Convert this basic shape into path data.

        The resulting path data produce the same visual result as the original
        basic shape.

        Returns:
            A `PathData` instance representing the path data.

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
    attrgroups.AnimationEventsAttrs,
    attrgroups.AnimationTimingAttrs,
    Element,
):
    """An animation element.

    From the SVG 1.1 specification:
    > "An animation element is an element that can be used to animate the
    attribute or property value of another element."
    """


class ContainerElement(
    _GraphicalOperations, attrgroups.GraphicalEventsAttrs, Element
):
    """A container element.

    From the SVG 1.1 specification:
    > "An element which can have graphics elements and other container elements
    as child elements."
    """


class DescriptiveElement(Element):
    """A descriptive element.

    From the SVG 1.1 specification:
    > "An element which provides supplementary descriptive information about
    its parent."
    """


class FilterPrimitiveElement(attrgroups.FilterPrimitivesAttrs, Element):
    """A filter primitive element.

    From the SVG 1.1 specification:
    > "A filter primitive element is one that can be used as a child of
    a `filter` element to specify a node in the filter graph."
    """


class GradientElement(Element):
    """A gradient element.

    From the SVG 1.1 specification:
    > "A gradient element is one that defines a gradient paint server."
    """


class GraphicsReferencingElement(Element):
    """A graphics referencing element.

    From the SVG 1.1 specification:
    > "A graphics element which uses a reference to a different document or
    element as the source of its graphical content."
    """


class LightSourceElement(Element):
    """A light source element.

    From the SVG 1.1 specification:
    > "A light source element is one that can specify light source information
    for an `feDiffuseLighting` or `feSpecularLighting` element."
    """


class StructuralElement(Element):
    """A structural element.

    From the SVG 1.1 specification:
    > "The structural elements are those which define the primary structure of
    an SVG document."
    """


class TextContentElement(GraphicsElement):
    """A text content element.

    From the SVG 1.1 specification:
    > "A text content element is an SVG element that causes a text string to be
    rendered onto the canvas."
    """


class TextContentChildElement(Element):
    """A text content child element.

    From the SVG 1.1 specification:
    > "A text content child element is a text content element that is allowed
    as a descendant of another text content element."
    """


class TextContentBlockElement(Element):
    """A text content block element.

    From the SVG 1.1 specification:
    > "A text content block element is a text content element that serves as a
    standalone element for a unit of text, and which may optionally contain
    certain child text content elements (e.g. `tspan`)."
    """
