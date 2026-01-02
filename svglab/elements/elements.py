"""Definitions of SVG elements.

This module contains the definitions of all SVG elements, including their
attributes and methods.

The elements are defined as classes, which inherit traits from the `traits`
module and attributes from the `attrs` package.
"""

# ruff: noqa: D101

from __future__ import annotations

import base64
import contextlib
import itertools
import os
import pathlib
from collections.abc import Iterable

import PIL.Image
from typing_extensions import Literal, final, overload, override

from svglab import graphics, models, protocols, serialize
from svglab.attrparse import color, length, path_data, point, transform
from svglab.attrs import attrdefs, attrgroups
from svglab.elements import traits
from svglab.utils import mathutils


# ! WARNING: `Element` and `ContainerElement` must always go last


def _length_or_zero(value: length.Length | None, /) -> length.Length:
    return value if value is not None else length.Length(0)


@final
class Path(
    attrgroups.ConditionalProcessingAttrs,
    attrdefs.ClassAttr,
    attrdefs.DAttr,
    attrdefs.ExternalResourcesRequiredAttr,
    attrdefs.StyleAttr,
    traits.Shape,
    traits.Element,
):
    pass


def _basic_shape_to_path(basic_shape: traits.BasicShape, /) -> Path:
    """Convert a basic shape to a `Path` element."""
    # try to convert to PathData first, so we don't call convert() if the shape
    # is not convertible
    d = basic_shape.to_path_data()

    path = models.convert(basic_shape, Path)
    path.d = d

    return path


def _points_to_path_data(
    element: attrdefs.PointsAttr,
) -> path_data.PathData:
    """Convert element with a `points` attribute to a `PathData` instance."""
    points = element.points if element.points is not None else []
    d = path_data.PathData()

    if points:
        d.move_to(points[0])

        for point in itertools.islice(points, 1, None):
            d.line_to(point)

    return d


def _ellipse_to_path_data(
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
    attrgroups.ConditionalProcessingAttrs,
    attrgroups.XlinkAttrs,
    attrdefs.ClassAttr,
    attrdefs.ExternalResourcesRequiredAttr,
    attrdefs.StyleAttr,
    attrdefs.TargetAttr,
    traits.ContainerElement,
):
    pass


@final
class AltGlyph(
    attrgroups.ConditionalProcessingAttrs,
    attrgroups.XlinkAttrs,
    attrdefs.ClassAttr,
    attrdefs.DxListOfLengthsAttr,
    attrdefs.DyListOfLengthsAttr,
    attrdefs.ExternalResourcesRequiredAttr,
    attrdefs.FormatAttr,
    attrdefs.GlyphRefAttr,
    attrdefs.RotateListOfNumbersAttr,
    attrdefs.StyleAttr,
    attrdefs.XListOfCoordinatesAttr,
    attrdefs.YListOfCoordinatesAttr,
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
    attrgroups.AnimationAdditionAttrs,
    attrgroups.AnimationAttributeTargetAttrs,
    attrgroups.AnimationValueAttrs,
    attrgroups.ConditionalProcessingAttrs,
    attrgroups.XlinkAttrs,
    traits.AnimationElement,
    traits.Element,
):
    pass


@final
class AnimateColor(
    attrgroups.AnimationAdditionAttrs,
    attrgroups.AnimationAttributeTargetAttrs,
    attrgroups.AnimationValueAttrs,
    attrgroups.ConditionalProcessingAttrs,
    attrgroups.XlinkAttrs,
    attrdefs.ExternalResourcesRequiredAttr,
    traits.AnimationElement,
    traits.Element,
):
    pass


@final
class AnimateMotion(
    attrgroups.AnimationAdditionAttrs,
    attrgroups.AnimationValueAttrs,
    attrgroups.ConditionalProcessingAttrs,
    attrgroups.XlinkAttrs,
    attrdefs.ExternalResourcesRequiredAttr,
    attrdefs.KeyPointsAttr,
    attrdefs.OriginAttr,
    attrdefs.PathAttr,
    attrdefs.RotateNumberAutoAutoReverseAttr,
    traits.AnimationElement,
    traits.Element,
):
    pass


@final
class AnimateTransform(
    attrgroups.AnimationAdditionAttrs,
    attrgroups.AnimationAttributeTargetAttrs,
    attrgroups.AnimationValueAttrs,
    attrgroups.ConditionalProcessingAttrs,
    attrgroups.XlinkAttrs,
    attrdefs.ExternalResourcesRequiredAttr,
    attrdefs.TypeAnimateTransformAttr,
    traits.AnimationElement,
    traits.Element,
):
    pass


@final
class Circle(
    attrgroups.ConditionalProcessingAttrs,
    attrdefs.ClassAttr,
    attrdefs.CxAttr,
    attrdefs.CyAttr,
    attrdefs.ExternalResourcesRequiredAttr,
    attrdefs.RAttr,
    attrdefs.StyleAttr,
    traits.BasicShape,
    traits.Element,
):
    @override
    def to_path_data(self) -> path_data.PathData:
        cx = _length_or_zero(self.cx)
        cy = _length_or_zero(self.cy)
        r = _length_or_zero(self.r)

        return _ellipse_to_path_data(cx=cx, cy=cy, rx=r, ry=r)

    @override
    def to_path(self) -> Path:
        return _basic_shape_to_path(self)


@final
class ClipPath(
    attrgroups.ConditionalProcessingAttrs,
    attrdefs.ClassAttr,
    attrdefs.ClipPathUnitsAttr,
    attrdefs.ExternalResourcesRequiredAttr,
    attrdefs.StyleAttr,
    traits.Element,
):
    pass


@final
class ColorProfile(
    attrgroups.XlinkAttrs,
    attrdefs.LocalAttr,
    attrdefs.NameNameAttr,
    attrdefs.RenderingIntentAttr,
    traits.Element,
):
    pass


@final
class Cursor(
    attrgroups.ConditionalProcessingAttrs,
    attrgroups.XlinkAttrs,
    attrdefs.ExternalResourcesRequiredAttr,
    attrdefs.XCoordinateAttr,
    attrdefs.YCoordinateAttr,
    traits.Element,
):
    pass


@final
class Defs(
    attrgroups.ConditionalProcessingAttrs,
    attrdefs.ClassAttr,
    attrdefs.ExternalResourcesRequiredAttr,
    attrdefs.StyleAttr,
    traits.StructuralElement,
    traits.ContainerElement,
):
    pass


@final
class Desc(
    attrdefs.ClassAttr,
    attrdefs.StyleAttr,
    traits.DescriptiveElement,
    traits.Element,
):
    pass


@final
class Ellipse(
    attrgroups.ConditionalProcessingAttrs,
    attrdefs.ClassAttr,
    attrdefs.CxAttr,
    attrdefs.CyAttr,
    attrdefs.ExternalResourcesRequiredAttr,
    attrdefs.RxAttr,
    attrdefs.RyAttr,
    attrdefs.StyleAttr,
    traits.BasicShape,
    traits.Element,
):
    @override
    def to_path_data(self) -> path_data.PathData:
        cx = _length_or_zero(self.cx)
        cy = _length_or_zero(self.cy)
        rx = _length_or_zero(self.rx)
        ry = _length_or_zero(self.ry)

        return _ellipse_to_path_data(cx=cx, cy=cy, rx=rx, ry=ry)

    @override
    def to_path(self) -> Path:
        return _basic_shape_to_path(self)


@final
class FeBlend(
    attrdefs.ClassAttr,
    attrdefs.InAttr,
    attrdefs.In2Attr,
    attrdefs.ModeAttr,
    attrdefs.StyleAttr,
    traits.FilterPrimitiveElement,
    traits.Element,
):
    pass


@final
class FeColorMatrix(
    attrdefs.ClassAttr,
    attrdefs.InAttr,
    attrdefs.In2Attr,
    attrdefs.StyleAttr,
    attrdefs.TypeFeColorMatrixAttr,
    attrdefs.ValuesListOfNumbersAttr,
    traits.FilterPrimitiveElement,
    traits.Element,
):
    pass


@final
class FeComponentTransfer(
    attrdefs.ClassAttr,
    attrdefs.InAttr,
    attrdefs.StyleAttr,
    traits.FilterPrimitiveElement,
    traits.Element,
):
    pass


@final
class FeComposite(
    attrdefs.ClassAttr,
    attrdefs.InAttr,
    attrdefs.In2Attr,
    attrdefs.K1Attr,
    attrdefs.K2Attr,
    attrdefs.K3Attr,
    attrdefs.K4Attr,
    attrdefs.OperatorFeCompositeAttr,
    attrdefs.StyleAttr,
    traits.FilterPrimitiveElement,
    traits.Element,
):
    pass


@final
class FeConvolveMatrix(
    attrdefs.BiasAttr,
    attrdefs.ClassAttr,
    attrdefs.DivisorAttr,
    attrdefs.InAttr,
    attrdefs.KernelMatrixAttr,
    attrdefs.KernelUnitLengthAttr,
    attrdefs.OrderAttr,
    attrdefs.PreserveAlphaAttr,
    attrdefs.StyleAttr,
    attrdefs.TargetXAttr,
    attrdefs.TargetYAttr,
    traits.FilterPrimitiveElement,
    traits.Element,
):
    pass


@final
class FeDiffuseLighting(
    attrdefs.ClassAttr,
    attrdefs.DiffuseConstantAttr,
    attrdefs.InAttr,
    attrdefs.KernelUnitLengthAttr,
    attrdefs.StyleAttr,
    attrdefs.SurfaceScaleAttr,
    traits.Element,
):
    pass


@final
class FeDisplacementMap(
    attrdefs.ClassAttr,
    attrdefs.InAttr,
    attrdefs.In2Attr,
    attrdefs.ScaleAttr,
    attrdefs.StyleAttr,
    attrdefs.XChannelSelectorAttr,
    attrdefs.YChannelSelectorAttr,
    traits.FilterPrimitiveElement,
    traits.Element,
):
    pass


@final
class FeDistantLight(
    attrdefs.AzimuthAttr,
    attrdefs.ElevationAttr,
    traits.LightSourceElement,
    traits.Element,
):
    pass


@final
class FeFlood(
    attrdefs.ClassAttr,
    attrdefs.StyleAttr,
    traits.FilterPrimitiveElement,
    traits.Element,
):
    pass


@final
class FeFuncA(attrgroups.TransferFunctionAttrs, traits.Element):
    pass


@final
class FeFuncB(attrgroups.TransferFunctionAttrs, traits.Element):
    pass


@final
class FeFuncG(attrgroups.TransferFunctionAttrs, traits.Element):
    pass


@final
class FeFuncR(attrgroups.TransferFunctionAttrs, traits.Element):
    pass


@final
class FeGaussianBlur(
    attrdefs.ClassAttr,
    attrdefs.InAttr,
    attrdefs.StdDeviationAttr,
    attrdefs.StyleAttr,
    traits.FilterPrimitiveElement,
    traits.Element,
):
    pass


@final
class FeImage(
    attrgroups.XlinkAttrs,
    attrdefs.ClassAttr,
    attrdefs.ExternalResourcesRequiredAttr,
    attrdefs.PreserveAspectRatioAttr,
    attrdefs.StyleAttr,
    traits.FilterPrimitiveElement,
    traits.Element,
):
    pass


@final
class FeMerge(
    attrdefs.ClassAttr,
    attrdefs.StyleAttr,
    traits.FilterPrimitiveElement,
    traits.Element,
):
    pass


@final
class FeMergeNode(attrdefs.InAttr, traits.Element):
    pass


@final
class FeMorphology(
    attrdefs.ClassAttr,
    attrdefs.InAttr,
    attrdefs.OperatorFeMorphologyAttr,
    attrdefs.RadiusAttr,
    attrdefs.StyleAttr,
    traits.FilterPrimitiveElement,
    traits.Element,
):
    pass


@final
class FeOffset(
    attrdefs.ClassAttr,
    attrdefs.DxNumberAttr,
    attrdefs.DyNumberAttr,
    attrdefs.InAttr,
    attrdefs.StyleAttr,
    traits.FilterPrimitiveElement,
    traits.Element,
):
    pass


@final
class FePointLight(
    attrdefs.XNumberAttr,
    attrdefs.YNumberAttr,
    attrdefs.ZAttr,
    traits.LightSourceElement,
    traits.Element,
):
    pass


@final
class FeSpecularLighting(
    attrdefs.ClassAttr,
    attrdefs.InAttr,
    attrdefs.KernelUnitLengthAttr,
    attrdefs.SpecularConstantAttr,
    attrdefs.SpecularExponentAttr,
    attrdefs.StyleAttr,
    attrdefs.SurfaceScaleAttr,
    traits.FilterPrimitiveElement,
    traits.Element,
):
    pass


@final
class FeSpotLight(
    attrdefs.LimitingConeAngleAttr,
    attrdefs.PointsAtXAttr,
    attrdefs.PointsAtYAttr,
    attrdefs.PointsAtZAttr,
    attrdefs.SpecularExponentAttr,
    attrdefs.XNumberAttr,
    attrdefs.YNumberAttr,
    attrdefs.ZAttr,
    traits.LightSourceElement,
    traits.Element,
):
    pass


@final
class FeTile(
    attrdefs.ClassAttr,
    attrdefs.InAttr,
    attrdefs.StyleAttr,
    traits.FilterPrimitiveElement,
    traits.Element,
):
    pass


@final
class FeTurbulence(
    attrdefs.BaseFrequencyAttr,
    attrdefs.ClassAttr,
    attrdefs.NumOctavesAttr,
    attrdefs.SeedAttr,
    attrdefs.StitchTilesAttr,
    attrdefs.StyleAttr,
    attrdefs.TypeFeTurbluenceAttr,
    traits.FilterPrimitiveElement,
    traits.Element,
):
    pass


@final
class Filter(
    attrgroups.XlinkAttrs,
    attrdefs.ClassAttr,
    attrdefs.ExternalResourcesRequiredAttr,
    attrdefs.FilterResAttr,
    attrdefs.FilterUnitsAttr,
    attrdefs.HeightAttr,
    attrdefs.PrimitiveUnitsAttr,
    attrdefs.StyleAttr,
    attrdefs.WidthAttr,
    attrdefs.XCoordinateAttr,
    attrdefs.YCoordinateAttr,
    traits.Element,
):
    pass


@final
class Font(
    attrdefs.ClassAttr,
    attrdefs.ExternalResourcesRequiredAttr,
    attrdefs.HorizAdvXAttr,
    attrdefs.HorizOriginXAttr,
    attrdefs.HorizOriginYAttr,
    attrdefs.StyleAttr,
    attrdefs.VertAdvYAttr,
    attrdefs.VertOriginXAttr,
    attrdefs.VertOriginYAttr,
    traits.Element,
):
    pass


@final
class FontFace(
    attrdefs.AccentHeightAttr,
    attrdefs.AlphabeticAttr,
    attrdefs.AscentAttr,
    attrdefs.BboxAttr,
    attrdefs.CapHeightAttr,
    attrdefs.DescentAttr,
    attrdefs.HangingAttr,
    attrdefs.IdeographicAttr,
    attrdefs.MathematicalAttr,
    attrdefs.OverlinePositionAttr,
    attrdefs.OverlineThicknessAttr,
    attrdefs.Panose1Attr,
    attrdefs.SlopeAttr,
    attrdefs.StemhAttr,
    attrdefs.StemvAttr,
    attrdefs.StrikethroughPositionAttr,
    attrdefs.StrikethroughThicknessAttr,
    attrdefs.UnderlinePositionAttr,
    attrdefs.UnderlineThicknessAttr,
    attrdefs.UnicodeRangeAttr,
    attrdefs.UnitsPerEmAttr,
    attrdefs.VAlphabeticAttr,
    attrdefs.VHangingAttr,
    attrdefs.VIdeographicAttr,
    attrdefs.VMathematicalAttr,
    attrdefs.WidthsAttr,
    attrdefs.XHeightAttr,
    traits.Element,
):
    pass


@final
class FontFaceFormat(attrdefs.StringAttr, traits.Element):
    pass


@final
class FontFaceName(attrdefs.StringAttr, traits.Element):
    pass


@final
class FontFaceSrc(traits.Element):
    pass


@final
class FontFaceUri(attrgroups.XlinkAttrs, traits.Element):
    pass


@final
class ForeignObject(
    attrgroups.ConditionalProcessingAttrs,
    attrdefs.ClassAttr,
    attrdefs.ExternalResourcesRequiredAttr,
    attrdefs.HeightAttr,
    attrdefs.StyleAttr,
    attrdefs.WidthAttr,
    attrdefs.XCoordinateAttr,
    attrdefs.YCoordinateAttr,
    traits.Element,
):
    pass


@final
class G(
    attrgroups.ConditionalProcessingAttrs,
    attrdefs.ClassAttr,
    attrdefs.ExternalResourcesRequiredAttr,
    attrdefs.StyleAttr,
    traits.StructuralElement,
    traits.ContainerElement,
):
    pass


@final
class Glyph(
    attrdefs.ArabicFormAttr,
    attrdefs.ClassAttr,
    attrdefs.DAttr,
    attrdefs.GlyphNameAttr,
    attrdefs.HorizAdvXAttr,
    attrdefs.LangGlyphAttr,
    attrdefs.OrientationAttr,
    attrdefs.StyleAttr,
    attrdefs.UnicodeAttr,
    attrdefs.VertAdvYAttr,
    attrdefs.VertOriginXAttr,
    attrdefs.VertOriginYAttr,
    traits.ContainerElement,
):
    pass


@final
class GlyphRef(
    attrgroups.XlinkAttrs,
    attrdefs.ClassAttr,
    attrdefs.DxNumberAttr,
    attrdefs.DyNumberAttr,
    attrdefs.FormatAttr,
    attrdefs.GlyphRefAttr,
    attrdefs.StyleAttr,
    attrdefs.XNumberAttr,
    attrdefs.YNumberAttr,
    traits.Element,
):
    pass


@final
class Hkern(
    attrdefs.G1Attr,
    attrdefs.G2Attr,
    attrdefs.KAttr,
    attrdefs.U1Attr,
    attrdefs.U2Attr,
    traits.Element,
):
    pass


@final
class Image(
    attrgroups.ConditionalProcessingAttrs,
    attrgroups.XlinkAttrs,
    attrdefs.ClassAttr,
    attrdefs.ExternalResourcesRequiredAttr,
    attrdefs.HeightAttr,
    attrdefs.PreserveAspectRatioAttr,
    attrdefs.StyleAttr,
    attrdefs.WidthAttr,
    attrdefs.XCoordinateAttr,
    attrdefs.YCoordinateAttr,
    traits.GraphicsElement,
    traits.GraphicsReferencingElement,
    traits.Element,
):
    pass


@final
class Line(
    attrgroups.ConditionalProcessingAttrs,
    attrdefs.ClassAttr,
    attrdefs.ExternalResourcesRequiredAttr,
    attrdefs.StyleAttr,
    attrdefs.X1Attr,
    attrdefs.X2Attr,
    attrdefs.Y1Attr,
    attrdefs.Y2Attr,
    traits.BasicShape,
    traits.Element,
):
    @override
    def to_path_data(self) -> path_data.PathData:
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
    attrgroups.XlinkAttrs,
    attrdefs.ClassAttr,
    attrdefs.ExternalResourcesRequiredAttr,
    attrdefs.GradientTransformAttr,
    attrdefs.GradientUnitsAttr,
    attrdefs.SpreadMethodAttr,
    attrdefs.StyleAttr,
    attrdefs.X1Attr,
    attrdefs.X2Attr,
    attrdefs.Y1Attr,
    attrdefs.Y2Attr,
    traits.GradientElement,
    traits.Element,
):
    pass


@final
class Marker(
    attrdefs.ClassAttr,
    attrdefs.ExternalResourcesRequiredAttr,
    attrdefs.MarkerHeightAttr,
    attrdefs.MarkerUnitsAttr,
    attrdefs.MarkerWidthAttr,
    attrdefs.OrientAttr,
    attrdefs.PreserveAspectRatioAttr,
    attrdefs.RefXAttr,
    attrdefs.RefYAttr,
    attrdefs.StyleAttr,
    attrdefs.ViewBoxAttr,
    traits.ContainerElement,
):
    pass


@final
class Mask(
    attrdefs.ClassAttr,
    attrdefs.ExternalResourcesRequiredAttr,
    attrdefs.HeightAttr,
    attrdefs.MaskContentUnitsAttr,
    attrdefs.MaskUnitsAttr,
    attrdefs.StyleAttr,
    attrdefs.WidthAttr,
    attrdefs.XCoordinateAttr,
    attrdefs.YCoordinateAttr,
    traits.ContainerElement,
):
    pass


@final
class Metadata(traits.DescriptiveElement, traits.Element):
    pass


@final
class MissingGlyph(
    attrdefs.ClassAttr,
    attrdefs.DAttr,
    attrdefs.HorizAdvXAttr,
    attrdefs.StyleAttr,
    attrdefs.VertAdvYAttr,
    attrdefs.VertOriginXAttr,
    attrdefs.VertOriginYAttr,
    traits.ContainerElement,
):
    pass


@final
class Mpath(
    attrgroups.XlinkAttrs,
    attrdefs.ExternalResourcesRequiredAttr,
    traits.Element,
):
    pass


@final
class Pattern(
    attrgroups.XlinkAttrs,
    attrdefs.ClassAttr,
    attrdefs.ExternalResourcesRequiredAttr,
    attrdefs.HeightAttr,
    attrdefs.PatternContentUnitsAttr,
    attrdefs.PatternTransformAttr,
    attrdefs.PatternUnitsAttr,
    attrdefs.PreserveAspectRatioAttr,
    attrdefs.StyleAttr,
    attrdefs.ViewBoxAttr,
    attrdefs.WidthAttr,
    attrdefs.XCoordinateAttr,
    attrdefs.YCoordinateAttr,
    traits.ContainerElement,
):
    pass


@final
class Polygon(
    attrgroups.ConditionalProcessingAttrs,
    attrdefs.ClassAttr,
    attrdefs.ExternalResourcesRequiredAttr,
    attrdefs.PointsAttr,
    attrdefs.StyleAttr,
    traits.BasicShape,
    traits.Element,
):
    @override
    def to_path_data(self) -> path_data.PathData:
        return _points_to_path_data(self).close()

    @override
    def to_path(self) -> Path:
        return _basic_shape_to_path(self)


@final
class Polyline(
    attrgroups.ConditionalProcessingAttrs,
    attrdefs.ClassAttr,
    attrdefs.ExternalResourcesRequiredAttr,
    attrdefs.PointsAttr,
    attrdefs.StyleAttr,
    traits.BasicShape,
    traits.Element,
):
    @override
    def to_path_data(self) -> path_data.PathData:
        return _points_to_path_data(self)

    @override
    def to_path(self) -> Path:
        return _basic_shape_to_path(self)


@final
class RadialGradient(
    attrgroups.XlinkAttrs,
    attrdefs.ClassAttr,
    attrdefs.CxAttr,
    attrdefs.CyAttr,
    attrdefs.ExternalResourcesRequiredAttr,
    attrdefs.FrAttr,
    attrdefs.FxAttr,
    attrdefs.FyAttr,
    attrdefs.GradientTransformAttr,
    attrdefs.GradientUnitsAttr,
    attrdefs.RAttr,
    attrdefs.SpreadMethodAttr,
    attrdefs.StyleAttr,
    traits.GradientElement,
    traits.Element,
):
    pass


@final
class Rect(
    attrgroups.ConditionalProcessingAttrs,
    attrdefs.ClassAttr,
    attrdefs.ExternalResourcesRequiredAttr,
    attrdefs.HeightAttr,
    attrdefs.RxAttr,
    attrdefs.RyAttr,
    attrdefs.StyleAttr,
    attrdefs.WidthAttr,
    attrdefs.XCoordinateAttr,
    attrdefs.YCoordinateAttr,
    traits.BasicShape,
    traits.Element,
):
    @override
    def to_path_data(self) -> path_data.PathData:
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
    attrgroups.XlinkAttrs,
    attrdefs.ExternalResourcesRequiredAttr,
    attrdefs.TypeContentTypeAttr,
    traits.Element,
):
    pass


@final
class Set(
    attrgroups.AnimationAttributeTargetAttrs,
    attrgroups.XlinkAttrs,
    attrdefs.ExternalResourcesRequiredAttr,
    attrdefs.ToAttr,
    traits.AnimationElement,
    traits.Element,
):
    pass


@final
class Stop(
    attrdefs.ClassAttr,
    attrdefs.OffsetNumberPercentageAttr,
    attrdefs.StyleAttr,
    traits.Element,
):
    pass


@final
class Style(
    attrdefs.MediaAttr,
    attrdefs.TitleAttr,
    attrdefs.TypeContentTypeAttr,
    traits.Element,
):
    pass


@final
class Svg(
    attrgroups.ConditionalProcessingAttrs,
    attrgroups.DocumentEventsAttrs,
    attrdefs.BaseProfileAttr,
    attrdefs.ClassAttr,
    attrdefs.ContentScriptTypeAttr,
    attrdefs.ContentStyleTypeAttr,
    attrdefs.ExternalResourcesRequiredAttr,
    attrdefs.HeightAttr,
    attrdefs.PreserveAspectRatioAttr,
    attrdefs.StyleAttr,
    attrdefs.VersionAttr,
    attrdefs.ViewBoxAttr,
    attrdefs.WidthAttr,
    attrdefs.XCoordinateAttr,
    attrdefs.XmlnsAttr,
    attrdefs.YCoordinateAttr,
    attrdefs.ZoomAndPanAttr,
    traits.StructuralElement,
    traits.ContainerElement,
):
    """The `<svg>` element.

    The `<svg>` element is the root of an SVG document fragment.

    You can either create a new SVG document from scratch by creating an
    instance of this class, or you can parse an existing SVG document
    using the `parse_svg` function.
    """

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
        file: protocols.SupportsWrite[str],
        /,
        *,
        pretty: bool = True,
        trailing_newline: bool = True,
        formatter: serialize.Formatter | None = None,
    ) -> None: ...

    def save(
        self,
        path_or_file: str
        | os.PathLike[str]
        | protocols.SupportsWrite[str],
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
        >>> from svglab import Rect, Svg
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
            file: protocols.SupportsWrite[str]

            match path_or_file:
                case str() | os.PathLike() as path:
                    file = stack.enter_context(
                        pathlib.Path(path).open("w")
                    )
                case protocols.SupportsWrite() as file:
                    pass

            file.write(output)

            if trailing_newline:
                file.write("\n")

    def set_viewbox(
        self, viewbox: tuple[float, float, float, float]
    ) -> None:
        """Set a new value for the `viewBox` attribute.

        This method sets a new value for the `viewBox` attribute and scales and
        translates the SVG content so that the visual representation of the SVG
        remains unchanged.

        If the `viewBox` is not set, the method uses the `width` and `height`
        attributes to calculate the initial viewBox. If the `width`
        and `height` attributes are not set, the method raises an exception.

        The new `viewBox` must have the same aspect ratio as the old `viewBox`.
        If the aspect ratios differ, the method raises an exception.

        Any attributes of type `Length` in the SVG must be convertible to
        user units. If an attribute is not convertible, the method raises an
        exception.

        Args:
        viewbox: A tuple of four numbers representing the new viewBox.

        Raises:
        ValueError: If `viewBox` is not set and `width` and `height` are not
            set or if the aspect ratios of the old and new viewBox differ.
        SvgUnitConversionError: If an attribute is not convertible to user
            units.

        """
        if self.viewBox is None:
            if self.width is None or self.height is None:
                raise ValueError(
                    "Either viewBox or width and height must be set"
                )
            old_viewbox = (0, 0, float(self.width), float(self.height))
        else:
            old_viewbox = self.viewBox

        old_min_x, old_min_y, old_width, old_height = old_viewbox
        min_x, min_y, width, height = viewbox

        tx = min_x - old_min_x
        ty = min_y - old_min_y

        sx = width / old_width
        sy = height / old_height

        if not mathutils.is_close(sx, sy):
            raise ValueError("Aspect ratios of old and new viewBox differ")

        # skip self; this can be done in a single for loop because the
        # SVG is a tree (probably)
        for child in self.find_all(recursive=False):
            # this is normally done in the reify method, but we need to do it
            # before we prepend the new transformations
            child.decompose_transform_origin()

            child.transform = [
                transform.Translate(tx, ty),
                transform.Scale(sx, sy),
                *(child.transform or []),
            ]

            child.reify(limit=2, recursive=False)

        self.viewBox = viewbox

    def render(
        self,
        *,
        background: color.Color | None = None,
        cursive_family: str | None = None,
        dpi: int = 96,
        fantasy_family: str | None = None,
        font_dirs: Iterable[pathlib.Path] = (),
        font_family: str | None = None,
        font_files: Iterable[pathlib.Path] = (),
        font_size: int = 16,
        height: float | None = None,
        image_rendering: Literal[
            "optimize_quality", "optimize_speed"
        ] = "optimize_quality",
        languages: Iterable[str] = ["en"],
        monospace_family: str | None = None,
        resources_dir: pathlib.Path | None = None,
        sans_serif_family: str | None = None,
        serif_family: str | None = None,
        shape_rendering: Literal[
            "optimize_speed", "crisp_edges", "geometric_precision"
        ] = "geometric_precision",
        skip_system_fonts: bool = False,
        text_rendering: Literal[
            "optimize_speed", "optimize_legibility"
        ] = "optimize_legibility",
        width: float | None = None,
        zoom: int = 1,
    ) -> PIL.Image.Image:
        """Render an SVG document fragment into a Pillow image.

        If the width and height are not specified, the dimensions of the SVG
        element are used. If only one dimension is specified, the other
        dimension is calculated in a way that preserves the aspect ratio set
        in the SVG element. If both dimensions are specified, the SVG is
        scaled so that the aspect ratio is preserved.

        Args:
        background: The background color of the rendered image. If `None`,
            the background is transparent.
        cursive_family: The font family to use for `cursive` fonts.
        dpi: The resolution of the rendered image, in dots per inch.
        fantasy_family: The font family to use for `fantasy` fonts.
        font_dirs: A list of directories to search for extra fonts.
        font_family: The default font family (when no `font-family` is
            specified).
        font_files: A list of extra font files to load.
        font_size: The default font size (when no `font-size` is specified); in
            points.
        height: The height of the rendered image, in pixels. If `None`, the
            height attribute of the SVG element is used.
        image_rendering: The default image rendering method (when no
            `image-rendering` is specified).
        languages: A list of language codes to use when resolving the
            `systemLanguage` attribute. Example: ["de", "en-US"].
        monospace_family: The font family to use for `monospace` fonts.
        resources_dir: A directory containing resources such as images
            referenced by relative URLs in the SVG document.
        sans_serif_family: The font family to use for `sans-serif` fonts.
        serif_family: The font family to use for `serif` fonts.
        shape_rendering: The default shape rendering method (when no
            `shape-rendering` is specified).
        skip_system_fonts: If `True`, do not load system fonts. In this case,
            only the fonts specified in `font_dirs` and `font_files` are used.
        svg: The SVG document fragment to render.
        text_rendering: The default text rendering method (when no
            `text-rendering` is specified).
        width: The width of the rendered image, in pixels. If `None`, the width
            attribute of the SVG element is used.
        zoom: The zoom level to use when rendering the image. A zoom level of
            1 means no zoom, 2 means 200%, and so on.

        Returns:
        The rendered image.

        """
        return graphics.render(
            self,
            background=background,
            cursive_family=cursive_family,
            dpi=dpi,
            fantasy_family=fantasy_family,
            font_dirs=font_dirs,
            font_family=font_family,
            font_files=font_files,
            font_size=font_size,
            height=height,
            image_rendering=image_rendering,
            languages=languages,
            monospace_family=monospace_family,
            resources_dir=resources_dir,
            sans_serif_family=sans_serif_family,
            serif_family=serif_family,
            shape_rendering=shape_rendering,
            skip_system_fonts=skip_system_fonts,
            text_rendering=text_rendering,
            width=width,
            zoom=zoom,
        )

    def show(self) -> None:
        """Render this SVG document fragment and display it on the screen.

        See `PIL.Image.Image.show` for more information.

        """
        self.render().show()

    def to_data_uri(self) -> str:
        """Convert the SVG document fragment to a base64-encoded data URI."""
        xml = self.to_xml(formatter=serialize.MINIMAL_FORMATTER)
        b64 = base64.b64encode(xml.encode()).decode()

        return f"data:image/svg+xml;base64,{b64}"


@final
class Switch(
    attrgroups.ConditionalProcessingAttrs,
    attrdefs.ClassAttr,
    attrdefs.ExternalResourcesRequiredAttr,
    attrdefs.StyleAttr,
    traits.ContainerElement,
):
    pass


@final
class Symbol(
    attrdefs.ClassAttr,
    attrdefs.ExternalResourcesRequiredAttr,
    attrdefs.PreserveAspectRatioAttr,
    attrdefs.RefXAttr,
    attrdefs.RefYAttr,
    attrdefs.StyleAttr,
    attrdefs.ViewBoxAttr,
    traits.StructuralElement,
    traits.ContainerElement,
):
    pass


@final
class Text(
    attrgroups.ConditionalProcessingAttrs,
    attrdefs.ClassAttr,
    attrdefs.DxListOfLengthsAttr,
    attrdefs.DyListOfLengthsAttr,
    attrdefs.ExternalResourcesRequiredAttr,
    attrdefs.LengthAdjustAttr,
    attrdefs.RotateListOfNumbersAttr,
    attrdefs.StyleAttr,
    attrdefs.TextLengthAttr,
    attrdefs.XListOfCoordinatesAttr,
    attrdefs.YListOfCoordinatesAttr,
    traits.TextContentElement,
    traits.Element,
):
    pass


@final
class TextPath(
    attrgroups.ConditionalProcessingAttrs,
    attrgroups.XlinkAttrs,
    attrdefs.ClassAttr,
    attrdefs.ExternalResourcesRequiredAttr,
    attrdefs.MethodAttr,
    attrdefs.SpacingAttr,
    attrdefs.StartOffsetAttr,
    attrdefs.StyleAttr,
    traits.TextContentChildElement,
    traits.TextContentElement,
    traits.Element,
):
    pass


@final
class Title(
    attrdefs.ClassAttr,
    attrdefs.StyleAttr,
    traits.DescriptiveElement,
    traits.Element,
):
    pass


@final
class Tref(
    attrgroups.ConditionalProcessingAttrs,
    attrgroups.XlinkAttrs,
    attrdefs.ClassAttr,
    attrdefs.ExternalResourcesRequiredAttr,
    attrdefs.StyleAttr,
    traits.TextContentChildElement,
    traits.TextContentElement,
    traits.Element,
):
    pass


@final
class Tspan(
    attrgroups.ConditionalProcessingAttrs,
    attrdefs.ClassAttr,
    attrdefs.DxListOfLengthsAttr,
    attrdefs.DyListOfLengthsAttr,
    attrdefs.ExternalResourcesRequiredAttr,
    attrdefs.LengthAdjustAttr,
    attrdefs.RotateListOfNumbersAttr,
    attrdefs.StyleAttr,
    attrdefs.TextLengthAttr,
    attrdefs.XListOfCoordinatesAttr,
    attrdefs.YListOfCoordinatesAttr,
    traits.TextContentBlockElement,
    traits.TextContentChildElement,
    traits.TextContentElement,
    traits.Element,
):
    pass


@final
class Use(
    attrgroups.ConditionalProcessingAttrs,
    attrgroups.XlinkAttrs,
    attrdefs.ClassAttr,
    attrdefs.ExternalResourcesRequiredAttr,
    attrdefs.HeightAttr,
    attrdefs.StyleAttr,
    attrdefs.WidthAttr,
    attrdefs.XCoordinateAttr,
    attrdefs.YCoordinateAttr,
    traits.GraphicsElement,
    traits.GraphicsReferencingElement,
    traits.StructuralElement,
    traits.Element,
):
    pass


@final
class View(
    attrdefs.ExternalResourcesRequiredAttr,
    attrdefs.PreserveAspectRatioAttr,
    attrdefs.ViewBoxAttr,
    attrdefs.ViewTargetAttr,
    attrdefs.ZoomAndPanAttr,
    traits.Element,
):
    pass


@final
class Vkern(
    attrdefs.G1Attr,
    attrdefs.G2Attr,
    attrdefs.KAttr,
    attrdefs.U1Attr,
    attrdefs.U2Attr,
    traits.Element,
):
    pass
