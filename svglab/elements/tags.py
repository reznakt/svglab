from __future__ import annotations

import itertools

from typing_extensions import final, override

from svglab import models
from svglab.attrparse import d, length, point
from svglab.attrs import groups, regular
from svglab.elements import traits


# ! WARNING: `Element` and `ContainerElement` must always go last


def _length_or_zero(value: length.Length | None, /) -> length.Length:
    return value if value is not None else length.Length(0)


@final
class Path(
    groups.ConditionalProcessing,
    regular.Class,
    regular.D,
    regular.ExternalResourcesRequired,
    regular.Style,
    traits.SupportsTransform,
    traits.Shape,
    traits.Element,
):
    pass


def _basic_shape_to_path(basic_shape: traits.BasicShape, /) -> Path:
    """Convert a basic shape to a `Path` element."""
    # try to convert to D first, so we don't call convert() if the shape
    # is not convertible
    d = basic_shape.to_d()

    path = models.convert(basic_shape, Path)
    path.d = d

    return path


def _points_to_d(element: regular.Points) -> d.D:
    """Convert an element with a `points` attribute to a `D` instance."""
    points = element.points if element.points is not None else []
    path_data = d.D()

    if points:
        path_data.move_to(points[0])

        for point in itertools.islice(points, 1, None):
            path_data.line_to(point)

    return path_data


def _ellipse_to_d(
    *,
    cx: length.Length,
    cy: length.Length,
    rx: length.Length,
    ry: length.Length,
) -> d.D:
    """Convert an ellipse to a `D` instance.

    Args:
        cx: The x-coordinate of the center of the ellipse.
        cy: The y-coordinate of the center of the ellipse.
        rx: The x-radius of the ellipse.
        ry: The y-radius of the ellipse.

    Returns:
        A `D` instance representing the ellipse.

    References:
        https://stackoverflow.com/a/10477334
        https://aleen42.gitbooks.io/wiki/content/Programming/JavaScript/webgl/SVG/convert_shapes_to_path/convert_shapes_to_path.html

    """
    return (
        d.D()
        .move_to(point.Point(cx - rx, cy))
        .arc_to(
            point.Point(rx, ry),
            0,
            point.Point(2 * rx, 0),
            large=True,
            sweep=False,
            relative=True,
        )
        .arc_to(
            point.Point(rx, ry),
            0,
            point.Point(-2 * rx, 0),
            large=True,
            sweep=False,
            relative=True,
        )
    )


@final
class A(
    groups.ConditionalProcessing,
    groups.Xlink,
    regular.Class,
    regular.ExternalResourcesRequired,
    regular.Style,
    regular.Target,
    traits.SupportsTransform,
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
    traits.SupportsTransform,
    traits.BasicShape,
    traits.Element,
):
    @override
    def to_d(self) -> d.D:
        cx = _length_or_zero(self.cx)
        cy = _length_or_zero(self.cy)
        r = _length_or_zero(self.r)

        return _ellipse_to_d(cx=cx, cy=cy, rx=r, ry=r)

    @override
    def to_path(self) -> Path:
        return _basic_shape_to_path(self)


@final
class ClipPath(
    groups.ConditionalProcessing,
    regular.Class,
    regular.ClipPathUnits,
    regular.ExternalResourcesRequired,
    regular.Style,
    traits.SupportsTransform,
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
    traits.SupportsTransform,
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
    traits.SupportsTransform,
    traits.BasicShape,
    traits.Element,
):
    @override
    def to_d(self) -> d.D:
        cx = _length_or_zero(self.cx)
        cy = _length_or_zero(self.cy)
        rx = _length_or_zero(self.rx)
        ry = _length_or_zero(self.ry)

        return _ellipse_to_d(cx=cx, cy=cy, rx=rx, ry=ry)

    @override
    def to_path(self) -> Path:
        return _basic_shape_to_path(self)


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
    traits.SupportsTransform,
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
    traits.SupportsTransform,
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
    regular.LangGlyph,
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
    traits.SupportsTransform,
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
    traits.SupportsTransform,
    regular.X1,
    regular.X2,
    regular.Y1,
    regular.Y2,
    traits.BasicShape,
    traits.Element,
):
    @override
    def to_d(self) -> d.D:
        x1 = _length_or_zero(self.x1)
        y1 = _length_or_zero(self.y1)
        x2 = _length_or_zero(self.x2)
        y2 = _length_or_zero(self.y2)

        return (
            d.D().move_to(point.Point(x1, y1)).line_to(point.Point(x2, y2))
        )

    @override
    def to_path(self) -> Path:
        return _basic_shape_to_path(self)


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
    traits.SupportsTransform,
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
    traits.SupportsTransform,
    traits.BasicShape,
    traits.Element,
):
    @override
    def to_d(self) -> d.D:
        return _points_to_d(self).close()

    @override
    def to_path(self) -> Path:
        return _basic_shape_to_path(self)


@final
class Polyline(
    groups.ConditionalProcessing,
    regular.Class,
    regular.ExternalResourcesRequired,
    regular.Points,
    regular.Style,
    traits.SupportsTransform,
    traits.BasicShape,
    traits.Element,
):
    @override
    def to_d(self) -> d.D:
        return _points_to_d(self)

    @override
    def to_path(self) -> Path:
        return _basic_shape_to_path(self)


@final
class RadialGradient(
    groups.Xlink,
    regular.Class,
    regular.Cx,
    regular.Cy,
    regular.ExternalResourcesRequired,
    regular.Fr,
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
    traits.SupportsTransform,
    regular.Width,
    regular.XCoordinate,
    regular.YCoordinate,
    traits.BasicShape,
    traits.Element,
):
    @override
    def to_d(self) -> d.D:
        x = _length_or_zero(self.x)
        y = _length_or_zero(self.y)
        width = _length_or_zero(self.width)
        height = _length_or_zero(self.height)

        match self.rx, self.ry:
            case None, None:
                rx = ry = length.Length(0)
            case length.Length(), None:
                rx = ry = self.rx
            case None, length.Length():
                rx = ry = self.ry
            case length.Length(), length.Length():
                rx = self.rx
                ry = self.ry

        return (
            d.D()
            .move_to(point.Point(x + rx, y))
            .horizontal_line_to(x + width - rx)
            .arc_to(
                point.Point(rx, ry),
                0,
                point.Point(x + width, y + ry),
                large=False,
                sweep=True,
            )
            .vertical_line_to(y + height - ry)
            .arc_to(
                point.Point(rx, ry),
                0,
                point.Point(x + width - rx, y + height),
                large=False,
                sweep=True,
            )
            .horizontal_line_to(x + rx)
            .arc_to(
                point.Point(rx, ry),
                0,
                point.Point(x, y + height - ry),
                large=False,
                sweep=True,
            )
            .vertical_line_to(y + ry)
            .arc_to(
                point.Point(rx, ry),
                0,
                point.Point(x + rx, y),
                large=False,
                sweep=True,
            )
        )

    @override
    def to_path(self) -> Path:
        return _basic_shape_to_path(self)


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
class Switch(
    groups.ConditionalProcessing,
    regular.Class,
    regular.ExternalResourcesRequired,
    regular.Style,
    traits.SupportsTransform,
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
    traits.SupportsTransform,
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
    traits.SupportsTransform,
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
