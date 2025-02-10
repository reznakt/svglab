from __future__ import annotations

from svglab import graphics
from svglab.attrs import groups, regular
from svglab.elements import common


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

    def get_mask(self, *, visible_only: bool = False) -> graphics.Mask:
        """Create a mask of this element.

        A mask is a 2D boolean array with `True` values where the tag is
        located (or visible) in the rendered SVG and `False` values elsewhere.

        Args:
            tag: The tag to create a mask for.
            visible_only: If `True`, only the visible parts of the tag are
                included in the mask. If `False`, the mask includes all parts
                of the tag (even if they are transparent).

        Returns:
            A 2D boolean array representing the mask of the tag.

        """
        return (
            graphics.visible_mask(self)
            if visible_only
            else graphics.mask(self)
        )


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
