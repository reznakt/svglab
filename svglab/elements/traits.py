from svglab.attrs import groups, regular


class Element(groups.Core, groups.Presentation):
    pass


class GraphicsElement(Element):
    pass


class Shape(GraphicsElement):
    pass


class BasicShape(Shape):
    pass


class AnimationElement(regular.OnLoad, Element):
    pass


class ContainerElement(Element):
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
