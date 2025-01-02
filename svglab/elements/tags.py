import contextlib
import os
import pathlib
from typing import final, overload

from svglab import serialize, utils
from svglab.attrs import groups, presentation, regular
from svglab.elements import common, traits


# ! WARNING: `PairedTag` and `Tag` must always go last in the inheritance list


@final
class A(regular.Transform, common.PairedTag):
    pass


@final
class AltGlyph(
    traits.TextContentElement, traits.TextContentChildElement, common.Tag
):
    pass


@final
class AltGlyphDef(common.Tag):
    pass


@final
class AltGlyphItem(common.Tag):
    pass


@final
class Animate(traits.AnimationElement, common.Tag):
    pass


@final
class AnimateColor(traits.AnimationElement, common.Tag):
    pass


@final
class AnimateMotion(traits.AnimationElement, common.Tag):
    pass


@final
class AnimateTransform(traits.AnimationElement, common.Tag):
    pass


@final
class Circle(
    groups.CxCy,
    groups.RxRy,
    regular.Transform,
    traits.BasicShape,
    common.Tag,
):
    pass


@final
class ClipPath(regular.Transform, common.Tag):
    pass


@final
class ColorProfile(common.Tag):
    pass


@final
class Cursor(common.Tag):
    pass


@final
class Defs(regular.Transform, traits.StructuralElement, common.PairedTag):
    pass


@final
class Desc(traits.DescriptiveElement, common.Tag):
    pass


@final
class Ellipse(
    groups.CxCy,
    groups.RxRy,
    regular.Transform,
    traits.BasicShape,
    common.Tag,
):
    pass


@final
class FeBlend(traits.FilterPrimitiveElement, common.Tag):
    pass


@final
class FeColorMatrix(traits.FilterPrimitiveElement, common.Tag):
    pass


@final
class FeComponentTransfer(traits.FilterPrimitiveElement, common.Tag):
    pass


@final
class FeComposite(traits.FilterPrimitiveElement, common.Tag):
    pass


@final
class FeConvolveMatrix(traits.FilterPrimitiveElement, common.Tag):
    pass


@final
class FeDiffuseLighting(common.Tag):
    pass


@final
class FeDisplacementMap(traits.FilterPrimitiveElement, common.Tag):
    pass


@final
class FeDistantLight(traits.LightSourceElement, common.Tag):
    pass


@final
class FeFlood(traits.FilterPrimitiveElement, common.Tag):
    pass


@final
class FeFuncA(common.Tag):
    pass


@final
class FeFuncB(common.Tag):
    pass


@final
class FeFuncG(common.Tag):
    pass


@final
class FeFuncR(common.Tag):
    pass


@final
class FeGaussianBlur(traits.FilterPrimitiveElement, common.Tag):
    pass


@final
class FeImage(traits.FilterPrimitiveElement, common.Tag):
    pass


@final
class FeMerge(traits.FilterPrimitiveElement, common.Tag):
    pass


@final
class FeMergeNode(common.Tag):
    pass


@final
class FeMorphology(traits.FilterPrimitiveElement, common.Tag):
    pass


@final
class FeOffset(traits.FilterPrimitiveElement, common.Tag):
    pass


@final
class FePointLight(traits.LightSourceElement, common.Tag):
    pass


@final
class FeSpecularLighting(traits.FilterPrimitiveElement, common.Tag):
    pass


@final
class FeSpotLight(traits.LightSourceElement, common.Tag):
    pass


@final
class FeTile(traits.FilterPrimitiveElement, common.Tag):
    pass


@final
class FeTurbulence(traits.FilterPrimitiveElement, common.Tag):
    pass


@final
class Filter(common.Tag):
    pass


@final
class Font(common.Tag):
    pass


@final
class FontFace(common.Tag):
    pass


@final
class FontFaceFormat(common.Tag):
    pass


@final
class FontFaceName(common.Tag):
    pass


@final
class FontFaceSrc(common.Tag):
    pass


@final
class FontFaceUri(common.Tag):
    pass


@final
class ForeignObject(regular.Transform, common.Tag):
    pass


@final
class G(regular.Transform, traits.StructuralElement, common.PairedTag):
    pass


@final
class Glyph(regular.D, common.PairedTag):
    pass


@final
class GlyphRef(common.Tag):
    pass


@final
class Hkern(common.Tag):
    pass


@final
class Image(
    regular.Transform, traits.GraphicsReferencingElement, common.Tag
):
    pass


@final
class Line(
    regular.Transform,
    regular.X1,
    regular.X2,
    regular.Y1,
    regular.Y2,
    traits.BasicShape,
    common.Tag,
):
    pass


@final
class LinearGradient(traits.GradientElement, common.Tag):
    pass


@final
class Marker(common.PairedTag):
    pass


@final
class Mask(common.PairedTag):
    pass


@final
class Metadata(traits.DescriptiveElement, common.Tag):
    pass


@final
class MissingGlyph(regular.D, regular.Transform, common.PairedTag):
    pass


@final
class Mpath(common.Tag):
    pass


@final
class Path(regular.D, traits.Shape, common.Tag):
    pass


@final
class Pattern(common.PairedTag):
    pass


@final
class Polygon(
    regular.Points, regular.Transform, traits.BasicShape, common.Tag
):
    pass


@final
class Polyline(
    regular.Points, regular.Transform, traits.BasicShape, common.Tag
):
    pass


@final
class RadialGradient(traits.GradientElement, common.Tag):
    pass


@final
class Rect(
    groups.RxRy,
    groups.WidthHeight,
    presentation.Color,
    regular.Transform,
    regular.XCoordinate,
    regular.YCoordinate,
    traits.BasicShape,
    common.Tag,
):
    pass


@final
class Script(common.Tag):
    pass


@final
class Set(traits.AnimationElement, common.Tag):
    pass


@final
class Stop(common.Tag):
    pass


@final
class Style(common.Tag):
    pass


@final
class Svg(
    regular.Xmlns,
    groups.WidthHeight,
    traits.StructuralElement,
    common.PairedTag,
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
class Switch(regular.Transform, common.PairedTag):
    pass


@final
class Symbol(traits.StructuralElement, common.PairedTag):
    pass


@final
class Text(
    regular.Transform,
    traits.GraphicsElement,
    traits.TextContentElement,
    common.Tag,
):
    pass


@final
class TextPath(
    traits.TextContentElement, traits.TextContentChildElement, common.Tag
):
    pass


@final
class Title(traits.DescriptiveElement, common.Tag):
    pass


@final
class Tref(
    traits.TextContentElement, traits.TextContentChildElement, common.Tag
):
    pass


@final
class Tspan(
    traits.TextContentElement,
    traits.TextContentChildElement,
    traits.TextContentBlockElement,
    common.Tag,
):
    pass


@final
class Use(
    regular.Transform,
    traits.GraphicsElement,
    traits.StructuralElement,
    traits.GraphicsReferencingElement,
    common.Tag,
):
    pass


@final
class View(common.Tag):
    pass


@final
class Vkern(common.Tag):
    pass
