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


class BasicShape(Shape):
    pass


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
