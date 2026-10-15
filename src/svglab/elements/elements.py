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
import copy
import itertools
import os
import pathlib

import PIL.Image
from typing_extensions import Final, final, overload, override

from svglab.attrparse.color import Color
from svglab.attrparse.length import Length
from svglab.attrparse.path_data import PathData
from svglab.attrparse.point import Point
from svglab.attrparse.transform import Scale, Transform, Translate
from svglab.attrs.attrdefs import (
    AccentHeightAttr,
    AlphabeticAttr,
    ArabicFormAttr,
    AscentAttr,
    AzimuthAttr,
    BaseFrequencyAttr,
    BaseProfileAttr,
    BboxAttr,
    BiasAttr,
    CapHeightAttr,
    ClassAttr,
    ClipPathUnitsAttr,
    ContentScriptTypeAttr,
    ContentStyleTypeAttr,
    CxAttr,
    CyAttr,
    DAttr,
    DescentAttr,
    DiffuseConstantAttr,
    DivisorAttr,
    DxListOfLengthsAttr,
    DxNumberAttr,
    DyListOfLengthsAttr,
    DyNumberAttr,
    ElevationAttr,
    ExternalResourcesRequiredAttr,
    FilterResAttr,
    FilterUnitsAttr,
    FormatAttr,
    FrAttr,
    FxAttr,
    FyAttr,
    G1Attr,
    G2Attr,
    GlyphNameAttr,
    GlyphRefAttr,
    GradientTransformAttr,
    GradientUnitsAttr,
    HangingAttr,
    HeightAttr,
    HorizAdvXAttr,
    HorizOriginXAttr,
    HorizOriginYAttr,
    IdeographicAttr,
    In2Attr,
    InAttr,
    K1Attr,
    K2Attr,
    K3Attr,
    K4Attr,
    KAttr,
    KernelMatrixAttr,
    KernelUnitLengthAttr,
    KeyPointsAttr,
    LangGlyphAttr,
    LengthAdjustAttr,
    LimitingConeAngleAttr,
    LocalAttr,
    MarkerHeightAttr,
    MarkerUnitsAttr,
    MarkerWidthAttr,
    MaskContentUnitsAttr,
    MaskUnitsAttr,
    MathematicalAttr,
    MediaAttr,
    MethodAttr,
    ModeAttr,
    NameNameAttr,
    NumOctavesAttr,
    OffsetNumberPercentageAttr,
    OperatorFeCompositeAttr,
    OperatorFeMorphologyAttr,
    OrderAttr,
    OrientationAttr,
    OrientAttr,
    OriginAttr,
    OverlinePositionAttr,
    OverlineThicknessAttr,
    Panose1Attr,
    PathAttr,
    PatternContentUnitsAttr,
    PatternTransformAttr,
    PatternUnitsAttr,
    PointsAttr,
    PointsAtXAttr,
    PointsAtYAttr,
    PointsAtZAttr,
    PreserveAlphaAttr,
    PreserveAspectRatioAttr,
    PrimitiveUnitsAttr,
    RadiusAttr,
    RAttr,
    RefXAttr,
    RefYAttr,
    RenderingIntentAttr,
    RotateListOfNumbersAttr,
    RotateNumberAutoAutoReverseAttr,
    RxAttr,
    RyAttr,
    ScaleAttr,
    SeedAttr,
    SlopeAttr,
    SpacingAttr,
    SpecularConstantAttr,
    SpecularExponentAttr,
    SpreadMethodAttr,
    StartOffsetAttr,
    StdDeviationAttr,
    StemhAttr,
    StemvAttr,
    StitchTilesAttr,
    StrikethroughPositionAttr,
    StrikethroughThicknessAttr,
    StringAttr,
    StyleAttr,
    SurfaceScaleAttr,
    TargetAttr,
    TargetXAttr,
    TargetYAttr,
    TextLengthAttr,
    TitleAttr,
    ToAttr,
    TypeAnimateTransformAttr,
    TypeContentTypeAttr,
    TypeFeColorMatrixAttr,
    TypeFeTurbluenceAttr,
    U1Attr,
    U2Attr,
    UnderlinePositionAttr,
    UnderlineThicknessAttr,
    UnicodeAttr,
    UnicodeRangeAttr,
    UnitsPerEmAttr,
    VAlphabeticAttr,
    ValuesListOfNumbersAttr,
    VersionAttr,
    VertAdvYAttr,
    VertOriginXAttr,
    VertOriginYAttr,
    VHangingAttr,
    VIdeographicAttr,
    ViewBoxAttr,
    ViewTargetAttr,
    VMathematicalAttr,
    WidthAttr,
    WidthsAttr,
    X1Attr,
    X2Attr,
    XChannelSelectorAttr,
    XCoordinateAttr,
    XHeightAttr,
    XListOfCoordinatesAttr,
    XmlnsAttr,
    XNumberAttr,
    Y1Attr,
    Y2Attr,
    YChannelSelectorAttr,
    YCoordinateAttr,
    YListOfCoordinatesAttr,
    YNumberAttr,
    ZAttr,
    ZoomAndPanAttr,
)
from svglab.attrs.attrgroups import (
    AnimationAdditionAttrs,
    AnimationAttributeTargetAttrs,
    AnimationValueAttrs,
    ConditionalProcessingAttrs,
    DocumentEventsAttrs,
    TransferFunctionAttrs,
    XlinkAttrs,
)
from svglab.elements.traits import (
    AnimationElement,
    BasicShape,
    ContainerElement,
    DescriptiveElement,
    Element,
    FilterPrimitiveElement,
    GradientElement,
    GraphicsElement,
    GraphicsReferencingElement,
    LightSourceElement,
    Shape,
    StructuralElement,
    TextContentBlockElement,
    TextContentChildElement,
    TextContentElement,
)
from svglab.entities import referenced_elements
from svglab.graphics import render
from svglab.models import convert
from svglab.protocols import SupportsWrite
from svglab.reify import (
    AffineGeometry,
    DocumentFragmentRoot,
    Grouping,
    ImplicitlyOrientedShape,
    PositionDefaultsToOrigin,
    PositionedByReference,
    RectilinearGeometry,
    RenderedIndirectly,
    SelectsAChild,
    SimilarityGeometry,
    Stylesheet,
    TransformInheritedByChildren,
    TranslatableGeometry,
    UniformlyScalableGeometry,
    ViewportEstablishing,
    style_declarations,
)
from svglab.resvg import RenderOptions
from svglab.serialize import MINIMAL_FORMATTER, Formatter
from svglab.utils.mathutils import is_close


# ! WARNING: `Element` and `ContainerElement` must always go last


def _length_or_zero(value: Length | None, /) -> Length:
    return value if value is not None else Length(0)


@final
class Path(
    AffineGeometry,
    ConditionalProcessingAttrs,
    ClassAttr,
    DAttr,
    ExternalResourcesRequiredAttr,
    StyleAttr,
    Shape,
    Element,
):
    pass


def _basic_shape_to_path(basic_shape: BasicShape, /) -> Path:
    """Convert a basic shape to a `Path` element."""
    # try to convert to PathData first, so we don't call convert() if the shape
    # is not convertible
    d = basic_shape.to_path_data()

    path = convert(basic_shape, Path)
    path.d = d

    # the resulting path is detached from the tree, so the children have to be
    # copied; otherwise they would end up with two parents. mapping the shape
    # to `None` up front detaches the copies and keeps the copy from reaching
    # the rest of the document through the parent links
    memo: dict[int, object] = {id(basic_shape): None}
    path.add_children(
        *(copy.deepcopy(child, memo) for child in basic_shape.children)
    )

    return path


def _points_to_path_data(element: PointsAttr) -> PathData:
    """Convert element with a `points` attribute to a `PathData` instance."""
    points = element.points if element.points is not None else []
    d = PathData()

    if points:
        d.move_to(points[0])

        for point in itertools.islice(points, 1, None):
            d.line_to(point)

    return d


def _ellipse_to_path_data(
    *, cx: Length, cy: Length, rx: Length, ry: Length
) -> PathData:
    """Convert an ellipse to a `PathData` instance.

    Args:
        cx: The x-coordinate of the center of the ellipse.
        cy: The y-coordinate of the center of the ellipse.
        rx: The x-radius of the ellipse.
        ry: The y-radius of the ellipse.

    Returns:
        A `PathData` instance representing the ellipse. It starts at the
        point `(cx + rx, cy)` and runs in the positive angle direction, the
        way the specification says the outline of an ellipse is drawn, so a
        dash pattern falls where it did on the ellipse. An ellipse without a
        radius is not rendered, and neither is its path.

    References:
        https://stackoverflow.com/a/10477334
        https://www.w3.org/TR/SVG11/shapes.html#EllipseElement

    """
    if not rx or not ry:
        return PathData()

    return (
        PathData()
        .move_to(Point(cx + rx, cy))
        .arc_to(
            Point(rx, ry),
            0,
            Point(-2 * rx, 0),
            large=True,
            sweep=True,
            relative=True,
        )
        .arc_to(
            Point(rx, ry),
            0,
            Point(2 * rx, 0),
            large=True,
            sweep=True,
            relative=True,
        )
    )


@final
class A(
    TransformInheritedByChildren,
    ConditionalProcessingAttrs,
    XlinkAttrs,
    ClassAttr,
    ExternalResourcesRequiredAttr,
    StyleAttr,
    TargetAttr,
    ContainerElement,
):
    pass


@final
class AltGlyph(
    ConditionalProcessingAttrs,
    XlinkAttrs,
    ClassAttr,
    DxListOfLengthsAttr,
    DyListOfLengthsAttr,
    ExternalResourcesRequiredAttr,
    FormatAttr,
    GlyphRefAttr,
    RotateListOfNumbersAttr,
    StyleAttr,
    XListOfCoordinatesAttr,
    YListOfCoordinatesAttr,
    TextContentChildElement,
    TextContentElement,
    Element,
):
    pass


@final
class AltGlyphDef(RenderedIndirectly, Element):
    pass


@final
class AltGlyphItem(RenderedIndirectly, Element):
    pass


@final
class Animate(
    AnimationAdditionAttrs,
    AnimationAttributeTargetAttrs,
    AnimationValueAttrs,
    ConditionalProcessingAttrs,
    XlinkAttrs,
    AnimationElement,
    Element,
):
    pass


@final
class AnimateColor(
    AnimationAdditionAttrs,
    AnimationAttributeTargetAttrs,
    AnimationValueAttrs,
    ConditionalProcessingAttrs,
    XlinkAttrs,
    ExternalResourcesRequiredAttr,
    AnimationElement,
    Element,
):
    pass


@final
class AnimateMotion(
    AnimationAdditionAttrs,
    AnimationValueAttrs,
    ConditionalProcessingAttrs,
    XlinkAttrs,
    ExternalResourcesRequiredAttr,
    KeyPointsAttr,
    OriginAttr,
    PathAttr,
    RotateNumberAutoAutoReverseAttr,
    AnimationElement,
    Element,
):
    pass


@final
class AnimateTransform(
    AnimationAdditionAttrs,
    AnimationAttributeTargetAttrs,
    AnimationValueAttrs,
    ConditionalProcessingAttrs,
    XlinkAttrs,
    ExternalResourcesRequiredAttr,
    TypeAnimateTransformAttr,
    AnimationElement,
    Element,
):
    pass


@final
class Circle(
    SimilarityGeometry,
    ImplicitlyOrientedShape,
    ConditionalProcessingAttrs,
    ClassAttr,
    CxAttr,
    CyAttr,
    ExternalResourcesRequiredAttr,
    RAttr,
    StyleAttr,
    BasicShape,
    Element,
):
    @override
    def to_path_data(self) -> PathData:
        cx = _length_or_zero(self.cx)
        cy = _length_or_zero(self.cy)
        r = _length_or_zero(self.r)

        return _ellipse_to_path_data(cx=cx, cy=cy, rx=r, ry=r)

    @override
    def to_path(self) -> Path:
        return _basic_shape_to_path(self)


@final
class ClipPath(
    TransformInheritedByChildren,
    RenderedIndirectly,
    ConditionalProcessingAttrs,
    ClassAttr,
    ClipPathUnitsAttr,
    ExternalResourcesRequiredAttr,
    StyleAttr,
    Element,
):
    pass


@final
class ColorProfile(
    RenderedIndirectly,
    XlinkAttrs,
    LocalAttr,
    NameNameAttr,
    RenderingIntentAttr,
    Element,
):
    pass


@final
class Cursor(
    RenderedIndirectly,
    ConditionalProcessingAttrs,
    XlinkAttrs,
    ExternalResourcesRequiredAttr,
    XCoordinateAttr,
    YCoordinateAttr,
    Element,
):
    pass


@final
class Defs(
    RenderedIndirectly,
    ConditionalProcessingAttrs,
    ClassAttr,
    ExternalResourcesRequiredAttr,
    StyleAttr,
    StructuralElement,
    ContainerElement,
):
    pass


@final
class Desc(ClassAttr, StyleAttr, DescriptiveElement, Element):
    pass


@final
class Ellipse(
    RectilinearGeometry,
    ImplicitlyOrientedShape,
    ConditionalProcessingAttrs,
    ClassAttr,
    CxAttr,
    CyAttr,
    ExternalResourcesRequiredAttr,
    RxAttr,
    RyAttr,
    StyleAttr,
    BasicShape,
    Element,
):
    @override
    def to_path_data(self) -> PathData:
        cx = _length_or_zero(self.cx)
        cy = _length_or_zero(self.cy)
        # a radius left out follows the other, as SVG 2 has it
        rx = self.rx if self.rx is not None else self.ry
        ry = self.ry if self.ry is not None else self.rx

        return _ellipse_to_path_data(
            cx=cx, cy=cy, rx=_length_or_zero(rx), ry=_length_or_zero(ry)
        )

    @override
    def to_path(self) -> Path:
        return _basic_shape_to_path(self)


@final
class FeBlend(
    ClassAttr,
    InAttr,
    In2Attr,
    ModeAttr,
    StyleAttr,
    FilterPrimitiveElement,
    Element,
):
    pass


@final
class FeColorMatrix(
    ClassAttr,
    InAttr,
    In2Attr,
    StyleAttr,
    TypeFeColorMatrixAttr,
    ValuesListOfNumbersAttr,
    FilterPrimitiveElement,
    Element,
):
    pass


@final
class FeComponentTransfer(
    ClassAttr, InAttr, StyleAttr, FilterPrimitiveElement, Element
):
    pass


@final
class FeComposite(
    ClassAttr,
    InAttr,
    In2Attr,
    K1Attr,
    K2Attr,
    K3Attr,
    K4Attr,
    OperatorFeCompositeAttr,
    StyleAttr,
    FilterPrimitiveElement,
    Element,
):
    pass


@final
class FeConvolveMatrix(
    BiasAttr,
    ClassAttr,
    DivisorAttr,
    InAttr,
    KernelMatrixAttr,
    KernelUnitLengthAttr,
    OrderAttr,
    PreserveAlphaAttr,
    StyleAttr,
    TargetXAttr,
    TargetYAttr,
    FilterPrimitiveElement,
    Element,
):
    pass


@final
class FeDiffuseLighting(
    ClassAttr,
    DiffuseConstantAttr,
    InAttr,
    KernelUnitLengthAttr,
    StyleAttr,
    SurfaceScaleAttr,
    FilterPrimitiveElement,
    Element,
):
    pass


@final
class FeDisplacementMap(
    ClassAttr,
    InAttr,
    In2Attr,
    ScaleAttr,
    StyleAttr,
    XChannelSelectorAttr,
    YChannelSelectorAttr,
    FilterPrimitiveElement,
    Element,
):
    pass


@final
class FeDistantLight(
    AzimuthAttr, ElevationAttr, LightSourceElement, Element
):
    pass


@final
class FeFlood(ClassAttr, StyleAttr, FilterPrimitiveElement, Element):
    pass


@final
class FeFuncA(TransferFunctionAttrs, Element):
    pass


@final
class FeFuncB(TransferFunctionAttrs, Element):
    pass


@final
class FeFuncG(TransferFunctionAttrs, Element):
    pass


@final
class FeFuncR(TransferFunctionAttrs, Element):
    pass


@final
class FeGaussianBlur(
    ClassAttr,
    InAttr,
    StdDeviationAttr,
    StyleAttr,
    FilterPrimitiveElement,
    Element,
):
    pass


@final
class FeImage(
    XlinkAttrs,
    ClassAttr,
    ExternalResourcesRequiredAttr,
    PreserveAspectRatioAttr,
    StyleAttr,
    FilterPrimitiveElement,
    Element,
):
    pass


@final
class FeMerge(ClassAttr, StyleAttr, FilterPrimitiveElement, Element):
    pass


@final
class FeMergeNode(InAttr, Element):
    pass


@final
class FeMorphology(
    ClassAttr,
    InAttr,
    OperatorFeMorphologyAttr,
    RadiusAttr,
    StyleAttr,
    FilterPrimitiveElement,
    Element,
):
    pass


@final
class FeOffset(
    ClassAttr,
    DxNumberAttr,
    DyNumberAttr,
    InAttr,
    StyleAttr,
    FilterPrimitiveElement,
    Element,
):
    pass


@final
class FePointLight(
    XNumberAttr, YNumberAttr, ZAttr, LightSourceElement, Element
):
    pass


@final
class FeSpecularLighting(
    ClassAttr,
    InAttr,
    KernelUnitLengthAttr,
    SpecularConstantAttr,
    SpecularExponentAttr,
    StyleAttr,
    SurfaceScaleAttr,
    FilterPrimitiveElement,
    Element,
):
    pass


@final
class FeSpotLight(
    LimitingConeAngleAttr,
    PointsAtXAttr,
    PointsAtYAttr,
    PointsAtZAttr,
    SpecularExponentAttr,
    XNumberAttr,
    YNumberAttr,
    ZAttr,
    LightSourceElement,
    Element,
):
    pass


@final
class FeTile(
    ClassAttr, InAttr, StyleAttr, FilterPrimitiveElement, Element
):
    pass


@final
class FeTurbulence(
    BaseFrequencyAttr,
    ClassAttr,
    NumOctavesAttr,
    SeedAttr,
    StitchTilesAttr,
    StyleAttr,
    TypeFeTurbluenceAttr,
    FilterPrimitiveElement,
    Element,
):
    pass


@final
class Filter(
    RenderedIndirectly,
    XlinkAttrs,
    ClassAttr,
    ExternalResourcesRequiredAttr,
    FilterResAttr,
    FilterUnitsAttr,
    HeightAttr,
    PrimitiveUnitsAttr,
    StyleAttr,
    WidthAttr,
    XCoordinateAttr,
    YCoordinateAttr,
    Element,
):
    pass


@final
class Font(
    RenderedIndirectly,
    ClassAttr,
    ExternalResourcesRequiredAttr,
    HorizAdvXAttr,
    HorizOriginXAttr,
    HorizOriginYAttr,
    StyleAttr,
    VertAdvYAttr,
    VertOriginXAttr,
    VertOriginYAttr,
    Element,
):
    pass


@final
class FontFace(
    RenderedIndirectly,
    AccentHeightAttr,
    AlphabeticAttr,
    AscentAttr,
    BboxAttr,
    CapHeightAttr,
    DescentAttr,
    HangingAttr,
    IdeographicAttr,
    MathematicalAttr,
    OverlinePositionAttr,
    OverlineThicknessAttr,
    Panose1Attr,
    SlopeAttr,
    StemhAttr,
    StemvAttr,
    StrikethroughPositionAttr,
    StrikethroughThicknessAttr,
    UnderlinePositionAttr,
    UnderlineThicknessAttr,
    UnicodeRangeAttr,
    UnitsPerEmAttr,
    VAlphabeticAttr,
    VHangingAttr,
    VIdeographicAttr,
    VMathematicalAttr,
    WidthsAttr,
    XHeightAttr,
    Element,
):
    pass


@final
class FontFaceFormat(RenderedIndirectly, StringAttr, Element):
    pass


@final
class FontFaceName(RenderedIndirectly, StringAttr, Element):
    pass


@final
class FontFaceSrc(RenderedIndirectly, Element):
    pass


@final
class FontFaceUri(RenderedIndirectly, XlinkAttrs, Element):
    pass


@final
class ForeignObject(
    TranslatableGeometry,
    ViewportEstablishing,
    ConditionalProcessingAttrs,
    ClassAttr,
    ExternalResourcesRequiredAttr,
    HeightAttr,
    StyleAttr,
    WidthAttr,
    XCoordinateAttr,
    YCoordinateAttr,
    Element,
):
    pass


@final
class G(
    Grouping,
    TransformInheritedByChildren,
    ConditionalProcessingAttrs,
    ClassAttr,
    ExternalResourcesRequiredAttr,
    StyleAttr,
    StructuralElement,
    ContainerElement,
):
    pass


@final
class Glyph(
    RenderedIndirectly,
    ArabicFormAttr,
    ClassAttr,
    DAttr,
    GlyphNameAttr,
    HorizAdvXAttr,
    LangGlyphAttr,
    OrientationAttr,
    StyleAttr,
    UnicodeAttr,
    VertAdvYAttr,
    VertOriginXAttr,
    VertOriginYAttr,
    ContainerElement,
):
    pass


@final
class GlyphRef(
    RenderedIndirectly,
    XlinkAttrs,
    ClassAttr,
    DxNumberAttr,
    DyNumberAttr,
    FormatAttr,
    GlyphRefAttr,
    StyleAttr,
    XNumberAttr,
    YNumberAttr,
    Element,
):
    pass


@final
class Hkern(
    RenderedIndirectly, G1Attr, G2Attr, KAttr, U1Attr, U2Attr, Element
):
    pass


@final
class Image(
    UniformlyScalableGeometry,
    ViewportEstablishing,
    ConditionalProcessingAttrs,
    XlinkAttrs,
    ClassAttr,
    ExternalResourcesRequiredAttr,
    HeightAttr,
    PreserveAspectRatioAttr,
    StyleAttr,
    WidthAttr,
    XCoordinateAttr,
    YCoordinateAttr,
    GraphicsElement,
    GraphicsReferencingElement,
    Element,
):
    pass


@final
class Line(
    AffineGeometry,
    ConditionalProcessingAttrs,
    ClassAttr,
    ExternalResourcesRequiredAttr,
    StyleAttr,
    X1Attr,
    X2Attr,
    Y1Attr,
    Y2Attr,
    BasicShape,
    Element,
):
    @override
    def to_path_data(self) -> PathData:
        x1 = _length_or_zero(self.x1)
        y1 = _length_or_zero(self.y1)
        x2 = _length_or_zero(self.x2)
        y2 = _length_or_zero(self.y2)

        return PathData().move_to(Point(x1, y1)).line_to(Point(x2, y2))

    @override
    def to_path(self) -> Path:
        return _basic_shape_to_path(self)


@final
class LinearGradient(
    XlinkAttrs,
    ClassAttr,
    ExternalResourcesRequiredAttr,
    GradientTransformAttr,
    GradientUnitsAttr,
    SpreadMethodAttr,
    StyleAttr,
    X1Attr,
    X2Attr,
    Y1Attr,
    Y2Attr,
    GradientElement,
    Element,
):
    pass


@final
class Marker(
    RenderedIndirectly,
    ViewportEstablishing,
    ClassAttr,
    ExternalResourcesRequiredAttr,
    MarkerHeightAttr,
    MarkerUnitsAttr,
    MarkerWidthAttr,
    OrientAttr,
    PreserveAspectRatioAttr,
    RefXAttr,
    RefYAttr,
    StyleAttr,
    ViewBoxAttr,
    ContainerElement,
):
    pass


@final
class Mask(
    RenderedIndirectly,
    ClassAttr,
    ExternalResourcesRequiredAttr,
    HeightAttr,
    MaskContentUnitsAttr,
    MaskUnitsAttr,
    StyleAttr,
    WidthAttr,
    XCoordinateAttr,
    YCoordinateAttr,
    ContainerElement,
):
    pass


@final
class Metadata(DescriptiveElement, Element):
    pass


@final
class MissingGlyph(
    RenderedIndirectly,
    ClassAttr,
    DAttr,
    HorizAdvXAttr,
    StyleAttr,
    VertAdvYAttr,
    VertOriginXAttr,
    VertOriginYAttr,
    ContainerElement,
):
    pass


@final
class Mpath(
    RenderedIndirectly, XlinkAttrs, ExternalResourcesRequiredAttr, Element
):
    pass


@final
class Pattern(
    RenderedIndirectly,
    ViewportEstablishing,
    XlinkAttrs,
    ClassAttr,
    ExternalResourcesRequiredAttr,
    HeightAttr,
    PatternContentUnitsAttr,
    PatternTransformAttr,
    PatternUnitsAttr,
    PreserveAspectRatioAttr,
    StyleAttr,
    ViewBoxAttr,
    WidthAttr,
    XCoordinateAttr,
    YCoordinateAttr,
    ContainerElement,
):
    pass


@final
class Polygon(
    AffineGeometry,
    ConditionalProcessingAttrs,
    ClassAttr,
    ExternalResourcesRequiredAttr,
    PointsAttr,
    StyleAttr,
    BasicShape,
    Element,
):
    @override
    def to_path_data(self) -> PathData:
        d = _points_to_path_data(self)

        return d.close() if d else d

    @override
    def to_path(self) -> Path:
        return _basic_shape_to_path(self)


@final
class Polyline(
    AffineGeometry,
    ConditionalProcessingAttrs,
    ClassAttr,
    ExternalResourcesRequiredAttr,
    PointsAttr,
    StyleAttr,
    BasicShape,
    Element,
):
    @override
    def to_path_data(self) -> PathData:
        return _points_to_path_data(self)

    @override
    def to_path(self) -> Path:
        return _basic_shape_to_path(self)


@final
class RadialGradient(
    XlinkAttrs,
    ClassAttr,
    CxAttr,
    CyAttr,
    ExternalResourcesRequiredAttr,
    FrAttr,
    FxAttr,
    FyAttr,
    GradientTransformAttr,
    GradientUnitsAttr,
    RAttr,
    SpreadMethodAttr,
    StyleAttr,
    GradientElement,
    Element,
):
    pass


@final
class Rect(
    RectilinearGeometry,
    ImplicitlyOrientedShape,
    ConditionalProcessingAttrs,
    ClassAttr,
    ExternalResourcesRequiredAttr,
    HeightAttr,
    RxAttr,
    RyAttr,
    StyleAttr,
    WidthAttr,
    XCoordinateAttr,
    YCoordinateAttr,
    BasicShape,
    Element,
):
    @override
    def to_path_data(self) -> PathData:
        x = _length_or_zero(self.x)
        y = _length_or_zero(self.y)
        width = _length_or_zero(self.width)
        height = _length_or_zero(self.height)

        match self.rx, self.ry:
            case None, None:
                rx = ry = Length(0)
            case Length(), None:
                rx = ry = self.rx
            case None, Length():
                rx = ry = self.ry
            case Length(), Length():
                rx = self.rx
                ry = self.ry

        if not width or not height:
            # a rect without an extent is not rendered
            return PathData()

        # the specification requires clamping the radii to half the side
        rx = min(rx, width / 2, key=float)
        ry = min(ry, height / 2, key=float)

        if not rx or not ry:
            return (
                PathData()
                .move_to(Point(x, y))
                .horizontal_line_to(x + width)
                .vertical_line_to(y + height)
                .horizontal_line_to(x)
                .close()
            )

        return (
            PathData()
            .move_to(Point(x + rx, y))
            .horizontal_line_to(x + width - rx)
            .arc_to(
                Point(rx, ry),
                0,
                Point(x + width, y + ry),
                large=False,
                sweep=True,
            )
            .vertical_line_to(y + height - ry)
            .arc_to(
                Point(rx, ry),
                0,
                Point(x + width - rx, y + height),
                large=False,
                sweep=True,
            )
            .horizontal_line_to(x + rx)
            .arc_to(
                Point(rx, ry),
                0,
                Point(x, y + height - ry),
                large=False,
                sweep=True,
            )
            .vertical_line_to(y + ry)
            .arc_to(
                Point(rx, ry), 0, Point(x + rx, y), large=False, sweep=True
            )
            .close()
        )

    @override
    def to_path(self) -> Path:
        return _basic_shape_to_path(self)


@final
class Script(
    RenderedIndirectly,
    XlinkAttrs,
    ExternalResourcesRequiredAttr,
    TypeContentTypeAttr,
    Element,
):
    pass


@final
class Set(
    AnimationAttributeTargetAttrs,
    XlinkAttrs,
    ExternalResourcesRequiredAttr,
    ToAttr,
    AnimationElement,
    Element,
):
    pass


@final
class Stop(
    RenderedIndirectly,
    ClassAttr,
    OffsetNumberPercentageAttr,
    StyleAttr,
    Element,
):
    pass


@final
class Style(
    Stylesheet,
    RenderedIndirectly,
    MediaAttr,
    TitleAttr,
    TypeContentTypeAttr,
    Element,
):
    pass


_STYLED_TRANSFORM: Final = frozenset({"transform", "transform-origin"})
"""Style properties that override what prepending to `transform` would do."""


@final
class Svg(
    DocumentFragmentRoot,
    TranslatableGeometry,
    ViewportEstablishing,
    ConditionalProcessingAttrs,
    DocumentEventsAttrs,
    BaseProfileAttr,
    ClassAttr,
    ContentScriptTypeAttr,
    ContentStyleTypeAttr,
    ExternalResourcesRequiredAttr,
    HeightAttr,
    PreserveAspectRatioAttr,
    StyleAttr,
    VersionAttr,
    ViewBoxAttr,
    WidthAttr,
    XCoordinateAttr,
    XmlnsAttr,
    YCoordinateAttr,
    ZoomAndPanAttr,
    StructuralElement,
    ContainerElement,
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
        formatter: Formatter | None = None,
    ) -> None: ...

    @overload
    def save(
        self,
        file: SupportsWrite[str],
        /,
        *,
        pretty: bool = True,
        trailing_newline: bool = True,
        formatter: Formatter | None = None,
    ) -> None: ...

    def save(
        self,
        path_or_file: str | os.PathLike[str] | SupportsWrite[str],
        /,
        *,
        pretty: bool = True,
        trailing_newline: bool = True,
        formatter: Formatter | None = None,
    ) -> None:
        """Convert the SVG document fragment to XML and write it to a file.

        Args:
            path_or_file: The path to the file to save the XML to,
                or a file-like object.
            pretty: Whether to produce pretty-printed XML.
            trailing_newline: Whether to add a trailing newline to the file.
            formatter: The formatter to use for serialization.

        Examples:
            >>> import sys
            >>> from svglab import Rect, Svg
            >>> svg = Svg(id="foo").add_child(Rect())
            >>> formatter = Formatter(indent=4)
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
            file: SupportsWrite[str]

            match path_or_file:
                case str() | os.PathLike() as path:
                    file = stack.enter_context(
                        pathlib.Path(path).open("w")
                    )
                case SupportsWrite() as file:
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

        If the new `viewBox` is equal to the current one, the content is left
        untouched.

        Children that are not drawn where they sit, such as `clipPath` or
        `defs`, are left alone: they are drawn in the coordinate system of
        whatever uses them. A child whose own transformation is seen elsewhere
        -- one a `use` references, one an animation targets, or one whose
        `style` sets its transformation -- is wrapped in a new `g` that
        carries the scaling and translation instead.

        Any attributes of type `Length` in the SVG must be convertible to
        user units. If an attribute is not convertible, the method raises an
        exception.

        Args:
            viewbox: A tuple of four numbers representing the new viewBox.

        Raises:
            ValueError: If `viewBox` is not set and `width` and `height` are
                not set or if the aspect ratios of the old and new viewBox
                differ.
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

        if all(
            is_close(old, new)
            for old, new in zip(old_viewbox, viewbox, strict=True)
        ):
            self.viewBox = viewbox
            return

        old_min_x, old_min_y, old_width, old_height = old_viewbox
        min_x, min_y, width, height = viewbox

        sx = width / old_width
        sy = height / old_height

        if not is_close(sx, sy):
            raise ValueError("Aspect ratios of old and new viewBox differ")

        tx = min_x - sx * old_min_x
        ty = min_y - sy * old_min_y

        mapping: Transform = [Translate(tx, ty), Scale(sx, sy)]
        referenced = referenced_elements(self.get_root())

        # skip self; the mapping is handed to the children, each of which
        # folds as much of it as it can into its own geometry
        for child in list(self.find_all(recursive=False)):
            if isinstance(child, RenderedIndirectly):
                # drawn in the coordinate system of whatever uses it, which
                # the mapping reaches already
                continue

            styled = style_declarations(child).keys()

            if id(child) in referenced or _STYLED_TRANSFORM & styled:
                # the child's own transformation has to stay as it is, so the
                # mapping goes around it instead
                index = self.get_child_index(child)
                self.remove_child(child)
                wrapper = G(transform=list(mapping)).add_child(child)
                self.add_child(wrapper, index=index)
                continue

            # this is normally done in the reify method, but we need to do it
            # before we prepend the new transformations
            child.decompose_transform_origin()
            child.transform = [*mapping, *(child.transform or [])]

        self.reify()

        self.viewBox = viewbox

    def render(
        self,
        options: RenderOptions | None = None,
        *,
        background: Color | None = None,
        height: float | None = None,
        width: float | None = None,
        zoom: float = 1,
    ) -> PIL.Image.Image:
        """Render an SVG document fragment into a Pillow image.

        If the width and height are not specified, the dimensions of the SVG
        element are used. If only one dimension is specified, the other
        dimension is calculated in a way that preserves the aspect ratio set
        in the SVG element. If both dimensions are specified, the SVG is
        scaled so that the aspect ratio is preserved.

        If the SVG element does not have a `width` or a `height` attribute,
        the missing dimension defaults to `100%` and is resolved against the
        `viewBox`, if there is one. A `viewBox` only defines an aspect ratio,
        not a size, so when neither dimension is known, one user unit is
        rendered as one pixel.

        Args:
            options: The renderer options, such as the default font and the
                resolution.
            background: The background color of the rendered image. If `None`,
                the background is transparent.
            height: The height of the rendered image, in pixels. If `None`, the
                height attribute of the SVG element is used.
            width: The width of the rendered image, in pixels. If `None`, the
                width attribute of the SVG element is used.
            zoom: The zoom level to use when rendering the image. A zoom level
                of 1 means no zoom, 2 means 200%, and so on.

        Returns:
            The rendered image.

        Raises:
            ValueError: If the image dimensions cannot be determined, are not
                positive, or if an argument is not a valid value for its
                parameter.
            OSError: If a font file named by `options` cannot be read.
            MemoryError: If the image does not fit in memory.
            RuntimeError: If the renderer panics, which is a bug in it.
            SvgRenderError: If the document cannot be rasterized.

        Examples:
            >>> from svglab import Svg, Length, resvg
            >>> svg = Svg(width=Length(20), height=Length(10))
            >>> svg.render().size
            (20, 10)
            >>> svg.render(RenderOptions(dpi=300), width=40).size
            (40, 20)

        """
        return render(
            self,
            options,
            background=background,
            height=height,
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
        xml = self.to_xml(formatter=MINIMAL_FORMATTER)
        b64 = base64.b64encode(xml.encode()).decode()

        return f"data:image/svg+xml;base64,{b64}"


@final
class Switch(
    SelectsAChild,
    TransformInheritedByChildren,
    ConditionalProcessingAttrs,
    ClassAttr,
    ExternalResourcesRequiredAttr,
    StyleAttr,
    ContainerElement,
):
    pass


@final
class Symbol(
    RenderedIndirectly,
    ViewportEstablishing,
    ClassAttr,
    ExternalResourcesRequiredAttr,
    PreserveAspectRatioAttr,
    RefXAttr,
    RefYAttr,
    StyleAttr,
    ViewBoxAttr,
    StructuralElement,
    ContainerElement,
):
    pass


@final
class Text(
    PositionDefaultsToOrigin,
    ConditionalProcessingAttrs,
    ClassAttr,
    DxListOfLengthsAttr,
    DyListOfLengthsAttr,
    ExternalResourcesRequiredAttr,
    LengthAdjustAttr,
    RotateListOfNumbersAttr,
    StyleAttr,
    TextLengthAttr,
    XListOfCoordinatesAttr,
    YListOfCoordinatesAttr,
    TextContentElement,
    Element,
):
    pass


@final
class TextPath(
    PositionedByReference,
    ConditionalProcessingAttrs,
    XlinkAttrs,
    ClassAttr,
    ExternalResourcesRequiredAttr,
    LengthAdjustAttr,
    MethodAttr,
    SpacingAttr,
    StartOffsetAttr,
    StyleAttr,
    TextLengthAttr,
    TextContentChildElement,
    TextContentElement,
    Element,
):
    pass


@final
class Title(ClassAttr, StyleAttr, DescriptiveElement, Element):
    pass


@final
class Tref(
    ConditionalProcessingAttrs,
    XlinkAttrs,
    ClassAttr,
    DxListOfLengthsAttr,
    DyListOfLengthsAttr,
    ExternalResourcesRequiredAttr,
    LengthAdjustAttr,
    RotateListOfNumbersAttr,
    StyleAttr,
    TextLengthAttr,
    XListOfCoordinatesAttr,
    YListOfCoordinatesAttr,
    TextContentChildElement,
    TextContentElement,
    Element,
):
    pass


@final
class Tspan(
    ConditionalProcessingAttrs,
    ClassAttr,
    DxListOfLengthsAttr,
    DyListOfLengthsAttr,
    ExternalResourcesRequiredAttr,
    LengthAdjustAttr,
    RotateListOfNumbersAttr,
    StyleAttr,
    TextLengthAttr,
    XListOfCoordinatesAttr,
    YListOfCoordinatesAttr,
    TextContentBlockElement,
    TextContentChildElement,
    TextContentElement,
    Element,
):
    pass


@final
class Use(
    TranslatableGeometry,
    ConditionalProcessingAttrs,
    XlinkAttrs,
    ClassAttr,
    ExternalResourcesRequiredAttr,
    HeightAttr,
    StyleAttr,
    WidthAttr,
    XCoordinateAttr,
    YCoordinateAttr,
    GraphicsElement,
    GraphicsReferencingElement,
    StructuralElement,
    Element,
):
    pass


@final
class View(
    RenderedIndirectly,
    ExternalResourcesRequiredAttr,
    PreserveAspectRatioAttr,
    ViewBoxAttr,
    ViewTargetAttr,
    ZoomAndPanAttr,
    Element,
):
    pass


@final
class Vkern(
    RenderedIndirectly, G1Attr, G2Attr, KAttr, U1Attr, U2Attr, Element
):
    pass
