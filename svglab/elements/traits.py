from __future__ import annotations

from svglab import bbox
from svglab.attrs import groups, regular
from svglab.elements import common


# common attributes are defined directly on the Tag class
class Element(common.Tag):
    pass


class _GraphicalOperations(Element):
    def bbox(self) -> bbox.BBox | None:
        return bbox.bbox(self)


class GraphicsElement(
    _GraphicalOperations,
    groups.GraphicalEvents,  # TODO: check if this is correct
    Element,
):
    pass


class Shape(regular.PathLength, GraphicsElement):
    pass


class BasicShape(Shape):
    pass


class AnimationElement(
    groups.AnimationEvents, groups.AnimationTiming, Element
):
    pass


class ContainerElement(
    _GraphicalOperations,
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
