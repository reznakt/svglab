import abc

from typing_extensions import Protocol

from svglab import models
from svglab.attrparse import d
from svglab.attrs import groups, regular
from svglab.elements import common, transforms


class Element(groups.Core, groups.Presentation, common.Tag):
    pass


class GraphicsElement(
    groups.GraphicalEvents,  # TODO: check if this is correct
    Element,
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
    groups.GraphicalEvents,  # TODO: check if this is correct
    common.PairedTag,
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
