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
class Animate(
    groups.AnimationAddition,
    groups.AnimationAttributeTarget,
    groups.AnimationValue,
    groups.ConditionalProcessing,
    groups.Xlink,
    traits.AnimationElement,
    traits.Element,
):
    pass


@final
class AnimateColor(
    groups.AnimationAddition,
    groups.AnimationAttributeTarget,
    groups.AnimationValue,
    groups.ConditionalProcessing,
    groups.Xlink,
    regular.ExternalResourcesRequired,
    traits.AnimationElement,
    traits.Element,
):
    pass


@final
class AnimateMotion(
    groups.AnimationAddition,
    groups.AnimationValue,
    groups.ConditionalProcessing,
    groups.Xlink,
    regular.ExternalResourcesRequired,
    regular.KeyPoints,
    regular.Origin,
    regular.Path,
    regular.RotateNumberAutoAutoReverse,
    traits.AnimationElement,
    traits.Element,
):
    pass


@final
class AnimateTransform(
    groups.AnimationAddition,
    groups.AnimationAttributeTarget,
    groups.AnimationValue,
    groups.ConditionalProcessing,
    groups.Xlink,
    regular.ExternalResourcesRequired,
    regular.TypeAnimateTransform,
    traits.AnimationElement,
    traits.Element,
):
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
class ClipPath(
    groups.ConditionalProcessing,
    regular.Class,
    regular.ClipPathUnits,
    regular.ExternalResourcesRequired,
    regular.Style,
    regular.Transform,
    traits.Element,
):
    pass


@final
class ColorProfile(
    groups.Xlink,
    regular.Local,
    regular.NameName,
    regular.RenderingIntent,
    traits.Element,
):
    pass


@final
class Cursor(
    groups.ConditionalProcessing,
    groups.Xlink,
    regular.ExternalResourcesRequired,
    regular.XCoordinate,
    regular.YCoordinate,
    traits.Element,
):
    pass


@final
class Defs(
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
class Desc(
    regular.Class, regular.Style, traits.DescriptiveElement, traits.Element
):
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
class FeBlend(
    regular.Class,
    regular.In,
    regular.In2,
    regular.Mode,
    regular.Style,
    traits.FilterPrimitiveElement,
    traits.Element,
):
    pass


@final
class FeColorMatrix(
    regular.Class,
    regular.In,
    regular.In2,
    regular.Style,
    regular.TypeFeColorMatrix,
    regular.ValuesListOfNumbers,
    traits.FilterPrimitiveElement,
    traits.Element,
):
    pass


@final
class FeComponentTransfer(
    regular.Class,
    regular.In,
    regular.Style,
    traits.FilterPrimitiveElement,
    traits.Element,
):
    pass


@final
class FeComposite(
    regular.Class,
    regular.In,
    regular.In2,
    regular.K1,
    regular.K2,
    regular.K3,
    regular.K4,
    regular.OperatorFeComposite,
    regular.Style,
    traits.FilterPrimitiveElement,
    traits.Element,
):
    pass


@final
class FeConvolveMatrix(
    regular.Bias,
    regular.Class,
    regular.Divisor,
    regular.In,
    regular.KernelMatrix,
    regular.KernelUnitLength,
    regular.Order,
    regular.PreserveAlpha,
    regular.Style,
    regular.TargetX,
    regular.TargetY,
    traits.FilterPrimitiveElement,
    traits.Element,
):
    pass


@final
class FeDiffuseLighting(
    regular.Class,
    regular.DiffuseConstant,
    regular.In,
    regular.KernelUnitLength,
    regular.Style,
    regular.SurfaceScale,
    traits.Element,
):
    pass


@final
class FeDisplacementMap(
    regular.Class,
    regular.In,
    regular.In2,
    regular.Scale,
    regular.Style,
    regular.XChannelSelector,
    regular.YChannelSelector,
    traits.FilterPrimitiveElement,
    traits.Element,
):
    pass


@final
class FeDistantLight(
    regular.Azimuth,
    regular.Elevation,
    traits.LightSourceElement,
    traits.Element,
):
    pass


@final
class FeFlood(
    regular.Class,
    regular.Style,
    traits.FilterPrimitiveElement,
    traits.Element,
):
    pass


@final
class FeFuncA(groups.TransferFunction, traits.Element):
    pass


@final
class FeFuncB(groups.TransferFunction, traits.Element):
    pass


@final
class FeFuncG(groups.TransferFunction, traits.Element):
    pass


@final
class FeFuncR(groups.TransferFunction, traits.Element):
    pass


@final
class FeGaussianBlur(
    regular.Class,
    regular.In,
    regular.StdDeviation,
    regular.Style,
    traits.FilterPrimitiveElement,
    traits.Element,
):
    pass


@final
class FeImage(
    groups.Xlink,
    regular.Class,
    regular.ExternalResourcesRequired,
    regular.PreserveAspectRatio,
    regular.Style,
    traits.FilterPrimitiveElement,
    traits.Element,
):
    pass


@final
class FeMerge(
    regular.Class,
    regular.Style,
    traits.FilterPrimitiveElement,
    traits.Element,
):
    pass


@final
class FeMergeNode(regular.In, traits.Element):
    pass


@final
class FeMorphology(
    regular.Class,
    regular.In,
    regular.OperatorFeMorphology,
    regular.Radius,
    regular.Style,
    traits.FilterPrimitiveElement,
    traits.Element,
):
    pass


@final
class FeOffset(
    regular.Class,
    regular.DxNumber,
    regular.DyNumber,
    regular.In,
    regular.Style,
    traits.FilterPrimitiveElement,
    traits.Element,
):
    pass


@final
class FePointLight(
    regular.XNumber,
    regular.YNumber,
    regular.Z,
    traits.LightSourceElement,
    traits.Element,
):
    pass


@final
class FeSpecularLighting(
    regular.Class,
    regular.In,
    regular.KernelUnitLength,
    regular.SpecularConstant,
    regular.SpecularExponent,
    regular.Style,
    regular.SurfaceScale,
    traits.FilterPrimitiveElement,
    traits.Element,
):
    pass


@final
class FeSpotLight(
    regular.LimitingConeAngle,
    regular.PointsAtX,
    regular.PointsAtY,
    regular.PointsAtZ,
    regular.SpecularExponent,
    regular.XNumber,
    regular.YNumber,
    regular.Z,
    traits.LightSourceElement,
    traits.Element,
):
    pass


@final
class FeTile(
    regular.Class,
    regular.In,
    regular.Style,
    traits.FilterPrimitiveElement,
    traits.Element,
):
    pass


@final
class FeTurbulence(
    regular.BaseFrequency,
    regular.Class,
    regular.NumOctaves,
    regular.Seed,
    regular.StitchTiles,
    regular.Style,
    regular.TypeFeTurbluence,
    traits.FilterPrimitiveElement,
    traits.Element,
):
    pass


@final
class Filter(
    groups.Xlink,
    regular.Class,
    regular.ExternalResourcesRequired,
    regular.FilterRes,
    regular.FilterUnits,
    regular.Height,
    regular.PrimitiveUnits,
    regular.Style,
    regular.Width,
    regular.XCoordinate,
    regular.YCoordinate,
    traits.Element,
):
    pass


@final
class Font(
    regular.Class,
    regular.ExternalResourcesRequired,
    regular.HorizAdvX,
    regular.HorizOriginX,
    regular.HorizOriginY,
    regular.Style,
    regular.VertAdvY,
    regular.VertOriginX,
    regular.VertOriginY,
    traits.Element,
):
    pass


@final
class FontFace(
    regular.AccentHeight,
    regular.Alphabetic,
    regular.Ascent,
    regular.Bbox,
    regular.CapHeight,
    regular.Descent,
    regular.FontFamily,
    regular.FontSize,
    regular.Hanging,
    regular.Ideographic,
    regular.Mathematical,
    regular.OverlinePosition,
    regular.OverlineThickness,
    regular.Panose1,
    regular.Slope,
    regular.Stemh,
    regular.Stemv,
    regular.StrikethroughPosition,
    regular.StrikethroughThickness,
    regular.UnderlinePosition,
    regular.UnderlineThickness,
    regular.UnicodeRange,
    regular.UnitsPerEm,
    regular.VAlphabetic,
    regular.VHanging,
    regular.VIdeographic,
    regular.VMathematical,
    regular.Widths,
    regular.XHeight,
    traits.Element,
):
    pass


@final
class FontFaceFormat(regular.String, traits.Element):
    pass


@final
class FontFaceName(regular.String, traits.Element):
    pass


@final
class FontFaceSrc(traits.Element):
    pass


@final
class FontFaceUri(groups.Xlink, traits.Element):
    pass


@final
class ForeignObject(
    groups.ConditionalProcessing,
    regular.Class,
    regular.ExternalResourcesRequired,
    regular.Height,
    regular.Style,
    regular.Transform,
    regular.Width,
    regular.XCoordinate,
    regular.YCoordinate,
    traits.Element,
):
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
class Glyph(
    regular.ArabicForm,
    regular.Class,
    regular.D,
    regular.GlyphName,
    regular.HorizAdvX,
    regular.Lang,
    regular.Orientation,
    regular.Style,
    regular.Unicode,
    regular.VertAdvY,
    regular.VertOriginX,
    regular.VertOriginY,
    traits.ContainerElement,
):
    pass


@final
class GlyphRef(
    groups.Xlink,
    regular.Class,
    regular.DxNumber,
    regular.DyNumber,
    regular.Format,
    regular.GlyphRef,
    regular.Style,
    regular.XNumber,
    regular.YNumber,
    traits.Element,
):
    pass


@final
class Hkern(
    regular.G1,
    regular.G2,
    regular.K,
    regular.U1,
    regular.U2,
    traits.Element,
):
    pass


@final
class Image(
    groups.ConditionalProcessing,
    groups.Xlink,
    regular.Class,
    regular.ExternalResourcesRequired,
    regular.Height,
    regular.PreserveAspectRatio,
    regular.Style,
    regular.Transform,
    regular.Width,
    regular.XCoordinate,
    regular.YCoordinate,
    traits.GraphicsElement,
    traits.GraphicsReferencingElement,
    traits.Element,
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
class LinearGradient(
    groups.Xlink,
    regular.Class,
    regular.ExternalResourcesRequired,
    regular.GradientTransform,
    regular.GradientUnits,
    regular.SpreadMethod,
    regular.Style,
    regular.X1,
    regular.X2,
    regular.Y1,
    regular.Y2,
    traits.GradientElement,
    traits.Element,
):
    pass


@final
class Marker(
    regular.Class,
    regular.ExternalResourcesRequired,
    regular.MarkerHeight,
    regular.MarkerUnits,
    regular.MarkerWidth,
    regular.Orient,
    regular.PreserveAspectRatio,
    regular.RefX,
    regular.RefY,
    regular.Style,
    regular.ViewBox,
    traits.ContainerElement,
):
    pass


@final
class Mask(
    regular.Class,
    regular.ExternalResourcesRequired,
    regular.Height,
    regular.MaskContentUnits,
    regular.MaskUnits,
    regular.Style,
    regular.Width,
    regular.XCoordinate,
    regular.YCoordinate,
    traits.ContainerElement,
):
    pass


@final
class Metadata(traits.DescriptiveElement, traits.Element):
    pass


@final
class MissingGlyph(
    regular.Class,
    regular.D,
    regular.HorizAdvX,
    regular.Style,
    regular.Transform,
    regular.VertAdvY,
    regular.VertOriginX,
    regular.VertOriginY,
    traits.ContainerElement,
):
    pass


@final
class Mpath(
    groups.Xlink, regular.ExternalResourcesRequired, traits.Element
):
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
class Pattern(
    groups.Xlink,
    regular.Class,
    regular.ExternalResourcesRequired,
    regular.Height,
    regular.PatternContentUnits,
    regular.PatternTransform,
    regular.PatternUnits,
    regular.PreserveAspectRatio,
    regular.Style,
    regular.ViewBox,
    regular.Width,
    regular.XCoordinate,
    regular.YCoordinate,
    traits.ContainerElement,
):
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
class RadialGradient(
    groups.Xlink,
    regular.Class,
    regular.Cx,
    regular.Cy,
    regular.ExternalResourcesRequired,
    regular.Fx,
    regular.Fy,
    regular.GradientTransform,
    regular.GradientUnits,
    regular.R,
    regular.SpreadMethod,
    regular.Style,
    traits.GradientElement,
    traits.Element,
):
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
class Script(
    groups.Xlink,
    regular.ExternalResourcesRequired,
    regular.TypeContentType,
    traits.Element,
):
    pass


@final
class Set(
    groups.AnimationAttributeTarget,
    groups.Xlink,
    regular.ExternalResourcesRequired,
    regular.To,
    traits.AnimationElement,
    traits.Element,
):
    pass


@final
class Stop(
    regular.Class,
    regular.OffsetNumberPercentage,
    regular.Style,
    traits.Element,
):
    pass


@final
class Style(
    regular.Media, regular.Title, regular.TypeContentType, traits.Element
):
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
class Switch(
    groups.ConditionalProcessing,
    regular.Class,
    regular.ExternalResourcesRequired,
    regular.Style,
    regular.Transform,
    traits.ContainerElement,
):
    pass


@final
class Symbol(
    regular.Class,
    regular.ExternalResourcesRequired,
    regular.PreserveAspectRatio,
    regular.Style,
    regular.ViewBox,
    traits.StructuralElement,
    traits.ContainerElement,
):
    pass


@final
class Text(
    groups.ConditionalProcessing,
    regular.Class,
    regular.DxListOfLengths,
    regular.DyListOfLengths,
    regular.ExternalResourcesRequired,
    regular.LengthAdjust,
    regular.RotateListOfNumbers,
    regular.Style,
    regular.TextLength,
    regular.Transform,
    regular.XListOfCoordinates,
    regular.YListOfCoordinates,
    traits.TextContentElement,
    traits.Element,
):
    pass


@final
class TextPath(
    groups.ConditionalProcessing,
    groups.Xlink,
    regular.Class,
    regular.ExternalResourcesRequired,
    regular.Method,
    regular.Spacing,
    regular.StartOffset,
    regular.Style,
    traits.TextContentChildElement,
    traits.TextContentElement,
    traits.Element,
):
    pass


@final
class Title(
    regular.Class, regular.Style, traits.DescriptiveElement, traits.Element
):
    pass


@final
class Tref(
    groups.ConditionalProcessing,
    groups.Xlink,
    regular.Class,
    regular.ExternalResourcesRequired,
    regular.Style,
    traits.TextContentChildElement,
    traits.TextContentElement,
    traits.Element,
):
    pass


@final
class Tspan(
    groups.ConditionalProcessing,
    regular.Class,
    regular.DxListOfLengths,
    regular.DyListOfLengths,
    regular.ExternalResourcesRequired,
    regular.LengthAdjust,
    regular.RotateListOfNumbers,
    regular.Style,
    regular.TextLength,
    regular.XListOfCoordinates,
    regular.YListOfCoordinates,
    traits.TextContentBlockElement,
    traits.TextContentChildElement,
    traits.TextContentElement,
    traits.Element,
):
    pass


@final
class Use(
    groups.ConditionalProcessing,
    groups.Xlink,
    regular.Class,
    regular.ExternalResourcesRequired,
    regular.Height,
    regular.Style,
    regular.Transform,
    regular.Width,
    regular.XCoordinate,
    regular.YCoordinate,
    traits.GraphicsElement,
    traits.GraphicsReferencingElement,
    traits.StructuralElement,
    traits.Element,
):
    pass


@final
class View(
    regular.ExternalResourcesRequired,
    regular.PreserveAspectRatio,
    regular.ViewBox,
    regular.ViewTarget,
    regular.ZoomAndPan,
    traits.Element,
):
    pass


@final
class Vkern(
    regular.G1,
    regular.G2,
    regular.K,
    regular.U1,
    regular.U2,
    traits.Element,
):
    pass
