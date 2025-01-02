import contextlib
import os
import pathlib
from typing import final, overload

from svglab import serialize, utils
from svglab.attrs import groups, regular
from svglab.elements import traits


# ! WARNING: `Element` and `ContainerElement` must always go last


@final
class A(
    groups.ConditionalProcessing,
    groups.Xlink,
    regular.Class,
    regular.ExternalResourcesRequired,
    regular.Style,
    regular.Target,
    regular.Transform,
    traits.ContainerElement,
):
    pass


@final
class AltGlyph(
    groups.ConditionalProcessing,
    groups.GraphicalEvents,
    groups.Xlink,
    regular.Class,
    regular.DxListOfLengths,
    regular.DyListOfLengths,
    regular.ExternalResourcesRequired,
    regular.Format,
    regular.GlyphRef,
    regular.RotateListOfNumbers,
    regular.Style,
    regular.XListOfCoordinates,
    regular.YListOfCoordinates,
    traits.TextContentChildElement,
    traits.TextContentElement,
    traits.Element,
):
    pass


@final
class AltGlyphDef(traits.Element):
    pass


@final
class AltGlyphItem(traits.Element):
    pass


@final
class Animate(traits.AnimationElement, traits.Element):
    pass


@final
class AnimateColor(traits.AnimationElement, traits.Element):
    pass


@final
class AnimateMotion(traits.AnimationElement, traits.Element):
    pass


@final
class AnimateTransform(traits.AnimationElement, traits.Element):
    pass


@final
class Circle(
    groups.ConditionalProcessing,
    regular.Class,
    regular.Cx,
    regular.Cy,
    regular.ExternalResourcesRequired,
    regular.R,
    regular.Style,
    regular.Transform,
    traits.BasicShape,
    traits.Element,
):
    pass


@final
class ClipPath(regular.Transform, traits.Element):
    pass


@final
class ColorProfile(traits.Element):
    pass


@final
class Cursor(traits.Element):
    pass


@final
class Defs(
    regular.Transform, traits.StructuralElement, traits.ContainerElement
):
    pass


@final
class Desc(traits.DescriptiveElement, traits.Element):
    pass


@final
class Ellipse(
    groups.ConditionalProcessing,
    regular.Class,
    regular.Cx,
    regular.Cy,
    regular.ExternalResourcesRequired,
    regular.Rx,
    regular.Ry,
    regular.Style,
    regular.Transform,
    traits.BasicShape,
    traits.Element,
):
    pass


@final
class FeBlend(traits.FilterPrimitiveElement, traits.Element):
    pass


@final
class FeColorMatrix(traits.FilterPrimitiveElement, traits.Element):
    pass


@final
class FeComponentTransfer(traits.FilterPrimitiveElement, traits.Element):
    pass


@final
class FeComposite(traits.FilterPrimitiveElement, traits.Element):
    pass


@final
class FeConvolveMatrix(traits.FilterPrimitiveElement, traits.Element):
    pass


@final
class FeDiffuseLighting(traits.Element):
    pass


@final
class FeDisplacementMap(traits.FilterPrimitiveElement, traits.Element):
    pass


@final
class FeDistantLight(traits.LightSourceElement, traits.Element):
    pass


@final
class FeFlood(traits.FilterPrimitiveElement, traits.Element):
    pass


@final
class FeFuncA(traits.Element):
    pass


@final
class FeFuncB(traits.Element):
    pass


@final
class FeFuncG(traits.Element):
    pass


@final
class FeFuncR(traits.Element):
    pass


@final
class FeGaussianBlur(traits.FilterPrimitiveElement, traits.Element):
    pass


@final
class FeImage(traits.FilterPrimitiveElement, traits.Element):
    pass


@final
class FeMerge(traits.FilterPrimitiveElement, traits.Element):
    pass


@final
class FeMergeNode(traits.Element):
    pass


@final
class FeMorphology(traits.FilterPrimitiveElement, traits.Element):
    pass


@final
class FeOffset(traits.FilterPrimitiveElement, traits.Element):
    pass


@final
class FePointLight(traits.LightSourceElement, traits.Element):
    pass


@final
class FeSpecularLighting(traits.FilterPrimitiveElement, traits.Element):
    pass


@final
class FeSpotLight(traits.LightSourceElement, traits.Element):
    pass


@final
class FeTile(traits.FilterPrimitiveElement, traits.Element):
    pass


@final
class FeTurbulence(traits.FilterPrimitiveElement, traits.Element):
    pass


@final
class Filter(traits.Element):
    pass


@final
class Font(traits.Element):
    pass


@final
class FontFace(traits.Element):
    pass


@final
class FontFaceFormat(traits.Element):
    pass


@final
class FontFaceName(traits.Element):
    pass


@final
class FontFaceSrc(traits.Element):
    pass


@final
class FontFaceUri(traits.Element):
    pass


@final
class ForeignObject(regular.Transform, traits.Element):
    pass


@final
class G(
    groups.ConditionalProcessing,
    regular.Class,
    regular.ExternalResourcesRequired,
    regular.Style,
    regular.Transform,
    traits.StructuralElement,
    traits.ContainerElement,
):
    pass


@final
class Glyph(regular.D, traits.ContainerElement):
    pass


@final
class GlyphRef(traits.Element):
    pass


@final
class Hkern(traits.Element):
    pass


@final
class Image(
    regular.Transform, traits.GraphicsReferencingElement, traits.Element
):
    pass


@final
class Line(
    groups.ConditionalProcessing,
    regular.Class,
    regular.ExternalResourcesRequired,
    regular.Style,
    regular.Transform,
    regular.X1,
    regular.X2,
    regular.Y1,
    regular.Y2,
    traits.BasicShape,
    traits.Element,
):
    pass


@final
class LinearGradient(traits.GradientElement, traits.Element):
    pass


@final
class Marker(traits.ContainerElement):
    pass


@final
class Mask(traits.ContainerElement):
    pass


@final
class Metadata(traits.DescriptiveElement, traits.Element):
    pass


@final
class MissingGlyph(regular.D, regular.Transform, traits.ContainerElement):
    pass


@final
class Mpath(traits.Element):
    pass


@final
class Path(
    groups.ConditionalProcessing,
    regular.Class,
    regular.D,
    regular.ExternalResourcesRequired,
    regular.PathLength,
    regular.Style,
    regular.Transform,
    traits.Shape,
    traits.Element,
):
    pass


@final
class Pattern(traits.ContainerElement):
    pass


@final
class Polygon(
    groups.ConditionalProcessing,
    regular.Class,
    regular.ExternalResourcesRequired,
    regular.Points,
    regular.Style,
    regular.Transform,
    traits.BasicShape,
    traits.Element,
):
    pass


@final
class Polyline(
    groups.ConditionalProcessing,
    regular.Class,
    regular.ExternalResourcesRequired,
    regular.Points,
    regular.Style,
    regular.Transform,
    traits.BasicShape,
    traits.Element,
):
    pass


@final
class RadialGradient(traits.GradientElement, traits.Element):
    pass


@final
class Rect(
    groups.ConditionalProcessing,
    regular.Class,
    regular.ExternalResourcesRequired,
    regular.Height,
    regular.Rx,
    regular.Ry,
    regular.Style,
    regular.Transform,
    regular.Width,
    regular.XCoordinate,
    regular.YCoordinate,
    traits.BasicShape,
    traits.Element,
):
    pass


@final
class Script(traits.Element):
    pass


@final
class Set(traits.AnimationElement, traits.Element):
    pass


@final
class Stop(traits.Element):
    pass


@final
class Style(traits.Element):
    pass


@final
class Svg(
    groups.ConditionalProcessing,
    groups.DocumentEvents,
    regular.BaseProfile,
    regular.Class,
    regular.ContentScriptType,
    regular.ContentStyleType,
    regular.ExternalResourcesRequired,
    regular.Height,
    regular.PreserveAspectRatio,
    regular.Style,
    regular.Version,
    regular.ViewBox,
    regular.Width,
    regular.XCoordinate,
    regular.Xmlns,
    regular.YCoordinate,
    regular.ZoomAndPan,
    traits.StructuralElement,
    traits.ContainerElement,
):
    @overload
    def save(
        self,
        path: str | os.PathLike[str],
        /,
        *,
        pretty: bool = True,
        trailing_newline: bool = True,
        formatter: serialize.Formatter | None = None,
    ) -> None: ...

    @overload
    def save(
        self,
        file: utils.SupportsWrite[str],
        /,
        *,
        pretty: bool = True,
        trailing_newline: bool = True,
        formatter: serialize.Formatter | None = None,
    ) -> None: ...

    def save(
        self,
        path_or_file: str | os.PathLike[str] | utils.SupportsWrite[str],
        /,
        *,
        pretty: bool = True,
        trailing_newline: bool = True,
        formatter: serialize.Formatter | None = None,
    ) -> None:
        """Convert the SVG document fragment to XML and write it to a file.

        Args:
        path_or_file: The path to the file to save the XML to,
        or a file-like object.
        pretty: Whether to produce pretty-printed XML.
        indent: The number of spaces to indent each level of the document.
        trailing_newline: Whether to add a trailing newline to the file.
        formatter: The formatter to use for serialization.

        Examples:
        >>> import sys
        >>> svg = Svg(id="foo").add_child(Rect())
        >>> formatter = serialize.Formatter(indent=4)
        >>> svg.save(
        ...     sys.stdout,
        ...     pretty=True,
        ...     trailing_newline=False,
        ...     formatter=formatter,
        ... )
        <svg id="foo">
            <rect/>
        </svg>

        """
        with contextlib.ExitStack() as stack:
            output = self.to_xml(pretty=pretty, formatter=formatter)
            file: utils.SupportsWrite[str]

            match path_or_file:
                case str() | os.PathLike() as path:
                    file = stack.enter_context(
                        pathlib.Path(path).open("w")
                    )
                case utils.SupportsWrite() as file:
                    pass

            file.write(output)

            if trailing_newline:
                file.write("\n")


@final
class Switch(regular.Transform, traits.ContainerElement):
    pass


@final
class Symbol(traits.StructuralElement, traits.ContainerElement):
    pass


@final
class Text(
    regular.Transform,
    traits.GraphicsElement,
    traits.TextContentElement,
    traits.Element,
):
    pass


@final
class TextPath(
    traits.TextContentElement,
    traits.TextContentChildElement,
    traits.Element,
):
    pass


@final
class Title(traits.DescriptiveElement, traits.Element):
    pass


@final
class Tref(
    traits.TextContentElement,
    traits.TextContentChildElement,
    traits.Element,
):
    pass


@final
class Tspan(
    traits.TextContentElement,
    traits.TextContentChildElement,
    traits.TextContentBlockElement,
    traits.Element,
):
    pass


@final
class Use(
    regular.Transform,
    traits.GraphicsElement,
    traits.StructuralElement,
    traits.GraphicsReferencingElement,
    traits.Element,
):
    pass


@final
class View(traits.Element):
    pass


@final
class Vkern(traits.Element):
    pass
