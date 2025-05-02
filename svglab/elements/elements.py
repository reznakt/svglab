"""Definitions of SVG elements.

This module contains the definitions of all SVG elements, including their
attributes and methods.

The elements are defined as classes, which inherit traits from the `traits`
module and attributes from the `attrs` package.
"""

# ruff: noqa: D101

from __future__ import annotations

import itertools

from typing_extensions import final, override

from svglab import models
from svglab.attrparse import length, path_data, point
from svglab.attrs import groups, regular
from svglab.elements import traits


# ! WARNING: `Element` and `ContainerElement` must always go last


def _length_or_zero(value: length.Length | None, /) -> length.Length:
    return value if value is not None else length.Length(0)


@final
class Path(
    groups.ConditionalProcessingAttrs,
    regular.ClassAttr,
    regular.DAttr,
    regular.ExternalResourcesRequiredAttr,
    regular.StyleAttr,
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


def _points_to_d(element: regular.PointsAttr) -> path_data.PathData:
    """Convert element with a `points` attribute to a `PathData` instance."""
    points = element.points if element.points is not None else []
    d = path_data.PathData()

    if points:
        d.move_to(points[0])

        for point in itertools.islice(points, 1, None):
            d.line_to(point)

    return d


def _ellipse_to_d(
    *,
    cx: length.Length,
    cy: length.Length,
    rx: length.Length,
    ry: length.Length,
) -> path_data.PathData:
    """Convert an ellipse to a `PathData` instance.

    Args:
        cx: The x-coordinate of the center of the ellipse.
        cy: The y-coordinate of the center of the ellipse.
        rx: The x-radius of the ellipse.
        ry: The y-radius of the ellipse.

    Returns:
        A `PathData` instance representing the ellipse.

    References:
        https://stackoverflow.com/a/10477334
        https://aleen42.gitbooks.io/wiki/content/Programming/JavaScript/webgl/SVG/convert_shapes_to_path/convert_shapes_to_path.html

    """
    return (
        path_data.PathData()
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
    groups.ConditionalProcessingAttrs,
    groups.XlinkAttrs,
    regular.ClassAttr,
    regular.ExternalResourcesRequiredAttr,
    regular.StyleAttr,
    regular.TargetAttr,
    traits.ContainerElement,
):
    pass


@final
class AltGlyph(
    groups.ConditionalProcessingAttrs,
    groups.XlinkAttrs,
    regular.ClassAttr,
    regular.DxListOfLengthsAttr,
    regular.DyListOfLengthsAttr,
    regular.ExternalResourcesRequiredAttr,
    regular.FormatAttr,
    regular.GlyphRefAttr,
    regular.RotateListOfNumbersAttr,
    regular.StyleAttr,
    regular.XListOfCoordinatesAttr,
    regular.YListOfCoordinatesAttr,
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
    groups.AnimationAdditionAttrs,
    groups.AnimationAttributeTargetAttrs,
    groups.AnimationValueAttrs,
    groups.ConditionalProcessingAttrs,
    groups.XlinkAttrs,
    traits.AnimationElement,
    traits.Element,
):
    pass


@final
class AnimateColor(
    groups.AnimationAdditionAttrs,
    groups.AnimationAttributeTargetAttrs,
    groups.AnimationValueAttrs,
    groups.ConditionalProcessingAttrs,
    groups.XlinkAttrs,
    regular.ExternalResourcesRequiredAttr,
    traits.AnimationElement,
    traits.Element,
):
    pass


@final
class AnimateMotion(
    groups.AnimationAdditionAttrs,
    groups.AnimationValueAttrs,
    groups.ConditionalProcessingAttrs,
    groups.XlinkAttrs,
    regular.ExternalResourcesRequiredAttr,
    regular.KeyPointsAttr,
    regular.OriginAttr,
    regular.PathAttr,
    regular.RotateNumberAutoAutoReverseAttr,
    traits.AnimationElement,
    traits.Element,
):
    pass


@final
class AnimateTransform(
    groups.AnimationAdditionAttrs,
    groups.AnimationAttributeTargetAttrs,
    groups.AnimationValueAttrs,
    groups.ConditionalProcessingAttrs,
    groups.XlinkAttrs,
    regular.ExternalResourcesRequiredAttr,
    regular.TypeAnimateTransformAttr,
    traits.AnimationElement,
    traits.Element,
):
    pass


@final
class Circle(
    groups.ConditionalProcessingAttrs,
    regular.ClassAttr,
    regular.CxAttr,
    regular.CyAttr,
    regular.ExternalResourcesRequiredAttr,
    regular.RAttr,
    regular.StyleAttr,
    traits.BasicShape,
    traits.Element,
):
    @override
    def to_d(self) -> path_data.PathData:
        cx = _length_or_zero(self.cx)
        cy = _length_or_zero(self.cy)
        r = _length_or_zero(self.r)

        return _ellipse_to_d(cx=cx, cy=cy, rx=r, ry=r)

    @override
    def to_path(self) -> Path:
        return _basic_shape_to_path(self)


@final
class ClipPath(
    groups.ConditionalProcessingAttrs,
    regular.ClassAttr,
    regular.ClipPathUnitsAttr,
    regular.ExternalResourcesRequiredAttr,
    regular.StyleAttr,
    traits.Element,
):
    pass


@final
class ColorProfile(
    groups.XlinkAttrs,
    regular.LocalAttr,
    regular.NameNameAttr,
    regular.RenderingIntentAttr,
    traits.Element,
):
    pass


@final
class Cursor(
    groups.ConditionalProcessingAttrs,
    groups.XlinkAttrs,
    regular.ExternalResourcesRequiredAttr,
    regular.XCoordinateAttr,
    regular.YCoordinateAttr,
    traits.Element,
):
    pass


@final
class Defs(
    groups.ConditionalProcessingAttrs,
    regular.ClassAttr,
    regular.ExternalResourcesRequiredAttr,
    regular.StyleAttr,
    traits.StructuralElement,
    traits.ContainerElement,
):
    pass


@final
class Desc(
    regular.ClassAttr,
    regular.StyleAttr,
    traits.DescriptiveElement,
    traits.Element,
):
    pass


@final
class Ellipse(
    groups.ConditionalProcessingAttrs,
    regular.ClassAttr,
    regular.CxAttr,
    regular.CyAttr,
    regular.ExternalResourcesRequiredAttr,
    regular.RxAttr,
    regular.RyAttr,
    regular.StyleAttr,
    traits.BasicShape,
    traits.Element,
):
    @override
    def to_d(self) -> path_data.PathData:
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
    regular.ClassAttr,
    regular.InAttr,
    regular.In2Attr,
    regular.ModeAttr,
    regular.StyleAttr,
    traits.FilterPrimitiveElement,
    traits.Element,
):
    pass


@final
class FeColorMatrix(
    regular.ClassAttr,
    regular.InAttr,
    regular.In2Attr,
    regular.StyleAttr,
    regular.TypeFeColorMatrixAttr,
    regular.ValuesListOfNumbersAttr,
    traits.FilterPrimitiveElement,
    traits.Element,
):
    pass


@final
class FeComponentTransfer(
    regular.ClassAttr,
    regular.InAttr,
    regular.StyleAttr,
    traits.FilterPrimitiveElement,
    traits.Element,
):
    pass


@final
class FeComposite(
    regular.ClassAttr,
    regular.InAttr,
    regular.In2Attr,
    regular.K1Attr,
    regular.K2Attr,
    regular.K3Attr,
    regular.K4Attr,
    regular.OperatorFeCompositeAttr,
    regular.StyleAttr,
    traits.FilterPrimitiveElement,
    traits.Element,
):
    pass


@final
class FeConvolveMatrix(
    regular.BiasAttr,
    regular.ClassAttr,
    regular.DivisorAttr,
    regular.InAttr,
    regular.KernelMatrixAttr,
    regular.KernelUnitLengthAttr,
    regular.OrderAttr,
    regular.PreserveAlphaAttr,
    regular.StyleAttr,
    regular.TargetXAttr,
    regular.TargetYAttr,
    traits.FilterPrimitiveElement,
    traits.Element,
):
    pass


@final
class FeDiffuseLighting(
    regular.ClassAttr,
    regular.DiffuseConstantAttr,
    regular.InAttr,
    regular.KernelUnitLengthAttr,
    regular.StyleAttr,
    regular.SurfaceScaleAttr,
    traits.Element,
):
    pass


@final
class FeDisplacementMap(
    regular.ClassAttr,
    regular.InAttr,
    regular.In2Attr,
    regular.ScaleAttr,
    regular.StyleAttr,
    regular.XChannelSelectorAttr,
    regular.YChannelSelectorAttr,
    traits.FilterPrimitiveElement,
    traits.Element,
):
    pass


@final
class FeDistantLight(
    regular.AzimuthAttr,
    regular.ElevationAttr,
    traits.LightSourceElement,
    traits.Element,
):
    pass


@final
class FeFlood(
    regular.ClassAttr,
    regular.StyleAttr,
    traits.FilterPrimitiveElement,
    traits.Element,
):
    pass


@final
class FeFuncA(groups.TransferFunctionAttrs, traits.Element):
    pass


@final
class FeFuncB(groups.TransferFunctionAttrs, traits.Element):
    pass


@final
class FeFuncG(groups.TransferFunctionAttrs, traits.Element):
    pass


@final
class FeFuncR(groups.TransferFunctionAttrs, traits.Element):
    pass


@final
class FeGaussianBlur(
    regular.ClassAttr,
    regular.InAttr,
    regular.StdDeviationAttr,
    regular.StyleAttr,
    traits.FilterPrimitiveElement,
    traits.Element,
):
    pass


@final
class FeImage(
    groups.XlinkAttrs,
    regular.ClassAttr,
    regular.ExternalResourcesRequiredAttr,
    regular.PreserveAspectRatioAttr,
    regular.StyleAttr,
    traits.FilterPrimitiveElement,
    traits.Element,
):
    pass


@final
class FeMerge(
    regular.ClassAttr,
    regular.StyleAttr,
    traits.FilterPrimitiveElement,
    traits.Element,
):
    pass


@final
class FeMergeNode(regular.InAttr, traits.Element):
    pass


@final
class FeMorphology(
    regular.ClassAttr,
    regular.InAttr,
    regular.OperatorFeMorphologyAttr,
    regular.RadiusAttr,
    regular.StyleAttr,
    traits.FilterPrimitiveElement,
    traits.Element,
):
    pass


@final
class FeOffset(
    regular.ClassAttr,
    regular.DxNumberAttr,
    regular.DyNumberAttr,
    regular.InAttr,
    regular.StyleAttr,
    traits.FilterPrimitiveElement,
    traits.Element,
):
    pass


@final
class FePointLight(
    regular.XNumberAttr,
    regular.YNumberAttr,
    regular.ZAttr,
    traits.LightSourceElement,
    traits.Element,
):
    pass


@final
class FeSpecularLighting(
    regular.ClassAttr,
    regular.InAttr,
    regular.KernelUnitLengthAttr,
    regular.SpecularConstantAttr,
    regular.SpecularExponentAttr,
    regular.StyleAttr,
    regular.SurfaceScaleAttr,
    traits.FilterPrimitiveElement,
    traits.Element,
):
    pass


@final
class FeSpotLight(
    regular.LimitingConeAngleAttr,
    regular.PointsAtXAttr,
    regular.PointsAtYAttr,
    regular.PointsAtZAttr,
    regular.SpecularExponentAttr,
    regular.XNumberAttr,
    regular.YNumberAttr,
    regular.ZAttr,
    traits.LightSourceElement,
    traits.Element,
):
    pass


@final
class FeTile(
    regular.ClassAttr,
    regular.InAttr,
    regular.StyleAttr,
    traits.FilterPrimitiveElement,
    traits.Element,
):
    pass


@final
class FeTurbulence(
    regular.BaseFrequencyAttr,
    regular.ClassAttr,
    regular.NumOctavesAttr,
    regular.SeedAttr,
    regular.StitchTilesAttr,
    regular.StyleAttr,
    regular.TypeFeTurbluenceAttr,
    traits.FilterPrimitiveElement,
    traits.Element,
):
    pass


@final
class Filter(
    groups.XlinkAttrs,
    regular.ClassAttr,
    regular.ExternalResourcesRequiredAttr,
    regular.FilterResAttr,
    regular.FilterUnitsAttr,
    regular.HeightAttr,
    regular.PrimitiveUnitsAttr,
    regular.StyleAttr,
    regular.WidthAttr,
    regular.XCoordinateAttr,
    regular.YCoordinateAttr,
    traits.Element,
):
    pass


@final
class Font(
    regular.ClassAttr,
    regular.ExternalResourcesRequiredAttr,
    regular.HorizAdvXAttr,
    regular.HorizOriginXAttr,
    regular.HorizOriginYAttr,
    regular.StyleAttr,
    regular.VertAdvYAttr,
    regular.VertOriginXAttr,
    regular.VertOriginYAttr,
    traits.Element,
):
    pass


@final
class FontFace(
    regular.AccentHeightAttr,
    regular.AlphabeticAttr,
    regular.AscentAttr,
    regular.BboxAttr,
    regular.CapHeightAttr,
    regular.DescentAttr,
    regular.HangingAttr,
    regular.IdeographicAttr,
    regular.MathematicalAttr,
    regular.OverlinePositionAttr,
    regular.OverlineThicknessAttr,
    regular.Panose1Attr,
    regular.SlopeAttr,
    regular.StemhAttr,
    regular.StemvAttr,
    regular.StrikethroughPositionAttr,
    regular.StrikethroughThicknessAttr,
    regular.UnderlinePositionAttr,
    regular.UnderlineThicknessAttr,
    regular.UnicodeRangeAttr,
    regular.UnitsPerEmAttr,
    regular.VAlphabeticAttr,
    regular.VHangingAttr,
    regular.VIdeographicAttr,
    regular.VMathematicalAttr,
    regular.WidthsAttr,
    regular.XHeightAttr,
    traits.Element,
):
    pass


@final
class FontFaceFormat(regular.StringAttr, traits.Element):
    pass


@final
class FontFaceName(regular.StringAttr, traits.Element):
    pass


@final
class FontFaceSrc(traits.Element):
    pass


@final
class FontFaceUri(groups.XlinkAttrs, traits.Element):
    pass


@final
class ForeignObject(
    groups.ConditionalProcessingAttrs,
    regular.ClassAttr,
    regular.ExternalResourcesRequiredAttr,
    regular.HeightAttr,
    regular.StyleAttr,
    regular.WidthAttr,
    regular.XCoordinateAttr,
    regular.YCoordinateAttr,
    traits.Element,
):
    pass


@final
class G(
    groups.ConditionalProcessingAttrs,
    regular.ClassAttr,
    regular.ExternalResourcesRequiredAttr,
    regular.StyleAttr,
    traits.StructuralElement,
    traits.ContainerElement,
):
    pass


@final
class Glyph(
    regular.ArabicFormAttr,
    regular.ClassAttr,
    regular.DAttr,
    regular.GlyphNameAttr,
    regular.HorizAdvXAttr,
    regular.LangGlyphAttr,
    regular.OrientationAttr,
    regular.StyleAttr,
    regular.UnicodeAttr,
    regular.VertAdvYAttr,
    regular.VertOriginXAttr,
    regular.VertOriginYAttr,
    traits.ContainerElement,
):
    pass


@final
class GlyphRef(
    groups.XlinkAttrs,
    regular.ClassAttr,
    regular.DxNumberAttr,
    regular.DyNumberAttr,
    regular.FormatAttr,
    regular.GlyphRefAttr,
    regular.StyleAttr,
    regular.XNumberAttr,
    regular.YNumberAttr,
    traits.Element,
):
    pass


@final
class Hkern(
    regular.G1Attr,
    regular.G2Attr,
    regular.KAttr,
    regular.U1Attr,
    regular.U2Attr,
    traits.Element,
):
    pass


@final
class Image(
    groups.ConditionalProcessingAttrs,
    groups.XlinkAttrs,
    regular.ClassAttr,
    regular.ExternalResourcesRequiredAttr,
    regular.HeightAttr,
    regular.PreserveAspectRatioAttr,
    regular.StyleAttr,
    regular.WidthAttr,
    regular.XCoordinateAttr,
    regular.YCoordinateAttr,
    traits.GraphicsElement,
    traits.GraphicsReferencingElement,
    traits.Element,
):
    pass


@final
class Line(
    groups.ConditionalProcessingAttrs,
    regular.ClassAttr,
    regular.ExternalResourcesRequiredAttr,
    regular.StyleAttr,
    regular.X1Attr,
    regular.X2Attr,
    regular.Y1Attr,
    regular.Y2Attr,
    traits.BasicShape,
    traits.Element,
):
    @override
    def to_d(self) -> path_data.PathData:
        x1 = _length_or_zero(self.x1)
        y1 = _length_or_zero(self.y1)
        x2 = _length_or_zero(self.x2)
        y2 = _length_or_zero(self.y2)

        return (
            path_data.PathData()
            .move_to(point.Point(x1, y1))
            .line_to(point.Point(x2, y2))
        )

    @override
    def to_path(self) -> Path:
        return _basic_shape_to_path(self)


@final
class LinearGradient(
    groups.XlinkAttrs,
    regular.ClassAttr,
    regular.ExternalResourcesRequiredAttr,
    regular.GradientTransformAttr,
    regular.GradientUnitsAttr,
    regular.SpreadMethodAttr,
    regular.StyleAttr,
    regular.X1Attr,
    regular.X2Attr,
    regular.Y1Attr,
    regular.Y2Attr,
    traits.GradientElement,
    traits.Element,
):
    pass


@final
class Marker(
    regular.ClassAttr,
    regular.ExternalResourcesRequiredAttr,
    regular.MarkerHeightAttr,
    regular.MarkerUnitsAttr,
    regular.MarkerWidthAttr,
    regular.OrientAttr,
    regular.PreserveAspectRatioAttr,
    regular.RefXAttr,
    regular.RefYAttr,
    regular.StyleAttr,
    regular.ViewBoxAttr,
    traits.ContainerElement,
):
    pass


@final
class Mask(
    regular.ClassAttr,
    regular.ExternalResourcesRequiredAttr,
    regular.HeightAttr,
    regular.MaskContentUnitsAttr,
    regular.MaskUnitsAttr,
    regular.StyleAttr,
    regular.WidthAttr,
    regular.XCoordinateAttr,
    regular.YCoordinateAttr,
    traits.ContainerElement,
):
    pass


@final
class Metadata(traits.DescriptiveElement, traits.Element):
    pass


@final
class MissingGlyph(
    regular.ClassAttr,
    regular.DAttr,
    regular.HorizAdvXAttr,
    regular.StyleAttr,
    regular.VertAdvYAttr,
    regular.VertOriginXAttr,
    regular.VertOriginYAttr,
    traits.ContainerElement,
):
    pass


@final
class Mpath(
    groups.XlinkAttrs,
    regular.ExternalResourcesRequiredAttr,
    traits.Element,
):
    pass


@final
class Pattern(
    groups.XlinkAttrs,
    regular.ClassAttr,
    regular.ExternalResourcesRequiredAttr,
    regular.HeightAttr,
    regular.PatternContentUnitsAttr,
    regular.PatternTransformAttr,
    regular.PatternUnitsAttr,
    regular.PreserveAspectRatioAttr,
    regular.StyleAttr,
    regular.ViewBoxAttr,
    regular.WidthAttr,
    regular.XCoordinateAttr,
    regular.YCoordinateAttr,
    traits.ContainerElement,
):
    pass


@final
class Polygon(
    groups.ConditionalProcessingAttrs,
    regular.ClassAttr,
    regular.ExternalResourcesRequiredAttr,
    regular.PointsAttr,
    regular.StyleAttr,
    traits.BasicShape,
    traits.Element,
):
    @override
    def to_d(self) -> path_data.PathData:
        return _points_to_d(self).close()

    @override
    def to_path(self) -> Path:
        return _basic_shape_to_path(self)


@final
class Polyline(
    groups.ConditionalProcessingAttrs,
    regular.ClassAttr,
    regular.ExternalResourcesRequiredAttr,
    regular.PointsAttr,
    regular.StyleAttr,
    traits.BasicShape,
    traits.Element,
):
    @override
    def to_d(self) -> path_data.PathData:
        return _points_to_d(self)

    @override
    def to_path(self) -> Path:
        return _basic_shape_to_path(self)


@final
class RadialGradient(
    groups.XlinkAttrs,
    regular.ClassAttr,
    regular.CxAttr,
    regular.CyAttr,
    regular.ExternalResourcesRequiredAttr,
    regular.FrAttr,
    regular.FxAttr,
    regular.FyAttr,
    regular.GradientTransformAttr,
    regular.GradientUnitsAttr,
    regular.RAttr,
    regular.SpreadMethodAttr,
    regular.StyleAttr,
    traits.GradientElement,
    traits.Element,
):
    pass


@final
class Rect(
    groups.ConditionalProcessingAttrs,
    regular.ClassAttr,
    regular.ExternalResourcesRequiredAttr,
    regular.HeightAttr,
    regular.RxAttr,
    regular.RyAttr,
    regular.StyleAttr,
    regular.WidthAttr,
    regular.XCoordinateAttr,
    regular.YCoordinateAttr,
    traits.BasicShape,
    traits.Element,
):
    @override
    def to_d(self) -> path_data.PathData:
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
            path_data.PathData()
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
    groups.XlinkAttrs,
    regular.ExternalResourcesRequiredAttr,
    regular.TypeContentTypeAttr,
    traits.Element,
):
    pass


@final
class Set(
    groups.AnimationAttributeTargetAttrs,
    groups.XlinkAttrs,
    regular.ExternalResourcesRequiredAttr,
    regular.ToAttr,
    traits.AnimationElement,
    traits.Element,
):
    pass


@final
class Stop(
    regular.ClassAttr,
    regular.OffsetNumberPercentageAttr,
    regular.StyleAttr,
    traits.Element,
):
    pass


@final
class Style(
    regular.MediaAttr,
    regular.TitleAttr,
    regular.TypeContentTypeAttr,
    traits.Element,
):
    pass


@final
class Switch(
    groups.ConditionalProcessingAttrs,
    regular.ClassAttr,
    regular.ExternalResourcesRequiredAttr,
    regular.StyleAttr,
    traits.ContainerElement,
):
    pass


@final
class Symbol(
    regular.ClassAttr,
    regular.ExternalResourcesRequiredAttr,
    regular.PreserveAspectRatioAttr,
    regular.RefXAttr,
    regular.RefYAttr,
    regular.StyleAttr,
    regular.ViewBoxAttr,
    traits.StructuralElement,
    traits.ContainerElement,
):
    pass


@final
class Text(
    groups.ConditionalProcessingAttrs,
    regular.ClassAttr,
    regular.DxListOfLengthsAttr,
    regular.DyListOfLengthsAttr,
    regular.ExternalResourcesRequiredAttr,
    regular.LengthAdjustAttr,
    regular.RotateListOfNumbersAttr,
    regular.StyleAttr,
    regular.TextLengthAttr,
    regular.XListOfCoordinatesAttr,
    regular.YListOfCoordinatesAttr,
    traits.TextContentElement,
    traits.Element,
):
    pass


@final
class TextPath(
    groups.ConditionalProcessingAttrs,
    groups.XlinkAttrs,
    regular.ClassAttr,
    regular.ExternalResourcesRequiredAttr,
    regular.MethodAttr,
    regular.SpacingAttr,
    regular.StartOffsetAttr,
    regular.StyleAttr,
    traits.TextContentChildElement,
    traits.TextContentElement,
    traits.Element,
):
    pass


@final
class Title(
    regular.ClassAttr,
    regular.StyleAttr,
    traits.DescriptiveElement,
    traits.Element,
):
    pass


@final
class Tref(
    groups.ConditionalProcessingAttrs,
    groups.XlinkAttrs,
    regular.ClassAttr,
    regular.ExternalResourcesRequiredAttr,
    regular.StyleAttr,
    traits.TextContentChildElement,
    traits.TextContentElement,
    traits.Element,
):
    pass


@final
class Tspan(
    groups.ConditionalProcessingAttrs,
    regular.ClassAttr,
    regular.DxListOfLengthsAttr,
    regular.DyListOfLengthsAttr,
    regular.ExternalResourcesRequiredAttr,
    regular.LengthAdjustAttr,
    regular.RotateListOfNumbersAttr,
    regular.StyleAttr,
    regular.TextLengthAttr,
    regular.XListOfCoordinatesAttr,
    regular.YListOfCoordinatesAttr,
    traits.TextContentBlockElement,
    traits.TextContentChildElement,
    traits.TextContentElement,
    traits.Element,
):
    pass


@final
class Use(
    groups.ConditionalProcessingAttrs,
    groups.XlinkAttrs,
    regular.ClassAttr,
    regular.ExternalResourcesRequiredAttr,
    regular.HeightAttr,
    regular.StyleAttr,
    regular.WidthAttr,
    regular.XCoordinateAttr,
    regular.YCoordinateAttr,
    traits.GraphicsElement,
    traits.GraphicsReferencingElement,
    traits.StructuralElement,
    traits.Element,
):
    pass


@final
class View(
    regular.ExternalResourcesRequiredAttr,
    regular.PreserveAspectRatioAttr,
    regular.ViewBoxAttr,
    regular.ViewTargetAttr,
    regular.ZoomAndPanAttr,
    traits.Element,
):
    pass


@final
class Vkern(
    regular.G1Attr,
    regular.G2Attr,
    regular.KAttr,
    regular.U1Attr,
    regular.U2Attr,
    traits.Element,
):
    pass
