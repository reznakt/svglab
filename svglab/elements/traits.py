from svglab.attrs import groups
from svglab.elements import common


class Element(groups.Core, groups.Presentation, common.Tag):
    pass


class GraphicsElement(
    groups.GraphicalEvents,  # TODO: check if this is correct
    Element,
):
    pass


class Shape(GraphicsElement):
    pass


class BasicShape(Shape):
    pass


class AnimationElement(groups.AnimationEvents, Element):
    pass


class ContainerElement(
    groups.GraphicalEvents,  # TODO: check if this is correct
    common.PairedTag,
):
    pass


class DescriptiveElement(Element):
    pass


class FilterPrimitiveElement(Element):
    pass


class GradientElement(Element):
    pass


class GraphicsReferencingElement(Element):
    pass


class LightSourceElement(Element):
    pass


class StructuralElement(Element):
    pass


class TextContentElement(Element):
    pass


class TextContentChildElement(Element):
    pass


class TextContentBlockElement(Element):
    pass
