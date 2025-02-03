import abc

from typing_extensions import Protocol

from svglab import models
from svglab.attrparse import d
from svglab.attrs import groups, regular
from svglab.elements import common


class Element(groups.Core, groups.Presentation, common.Tag):
    pass


class GraphicsElement(
    groups.GraphicalEvents,  # TODO: check if this is correct
    Element,
):
    pass


class Shape(regular.PathLength, GraphicsElement):
    pass


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
