"""Definitions of regular attributes."""
# ruff: noqa: N815, D101

from typing_extensions import Literal

from svglab import models, utiltypes
from svglab.attrs import common, typedefs


class AccentHeightAttr(common.Attr):
    accent_height: models.Attr[typedefs.Number] = None


class AccumulateAttr(common.Attr):
    accumulate: models.Attr[typedefs.None_ | Literal["sum"]] = None


class AdditiveAttr(common.Attr):
    additive: models.Attr[Literal["replace", "sum"]] = None


class AlphabeticAttr(common.Attr):
    alphabetic: models.Attr[typedefs.Number] = None


class AmplitudeAttr(common.Attr):
    amplitude: models.Attr[typedefs.Number] = None


class ArabicFormAttr(common.Attr):
    arabic_form: models.Attr[
        Literal["initial", "medial", "terminal", "isolated"]
    ] = None


class AscentAttr(common.Attr):
    ascent: models.Attr[typedefs.Number] = None


class AttributeNameAttr(common.Attr):
    attributeName: models.Attr[typedefs.Unparsed] = None


class AttributeTypeAttr(common.Attr):
    attributeType: models.Attr[Literal["CSS", "XML"] | typedefs.Auto] = (
        None
    )


class AzimuthAttr(common.Attr):
    azimuth: models.Attr[typedefs.Number] = None


class BaseFrequencyAttr(common.Attr):
    baseFrequency: models.Attr[typedefs.NumberOptionalNumber] = None


class BaseProfileAttr(common.Attr):
    baseProfile: models.Attr[typedefs.ProfileName] = None


class BboxAttr(common.Attr):
    bbox: models.Attr[
        models.Tuple4[
            typedefs.Number,
            typedefs.Number,
            typedefs.Number,
            typedefs.Number,
        ]
    ] = None


class BeginAttr(common.Attr):
    begin: models.Attr[typedefs.BeginValueList] = None


class BiasAttr(common.Attr):
    bias: models.Attr[typedefs.Number] = None


class ByAttr(common.Attr):
    by: models.Attr[typedefs.Unparsed] = None


class CalcModeAttr(common.Attr):
    calcMode: models.Attr[
        Literal["discrete", "linear", "paced", "spline"]
    ] = None


class CapHeightAttr(common.Attr):
    cap_height: models.Attr[typedefs.Number] = None


class ClassAttr(common.Attr):
    class_: models.Attr[typedefs.ListOfStrings] = None


class ClipPathUnitsAttr(common.Attr):
    clipPathUnits: models.Attr[
        Literal["userSpaceOnUse", "objectBoundingBox"]
    ] = None


class ContentScriptTypeAttr(common.Attr):
    contentScriptType: models.Attr[typedefs.ContentType] = None


class ContentStyleTypeAttr(common.Attr):
    contentStyleType: models.Attr[typedefs.ContentType] = None


class CxAttr(common.Attr):
    cx: models.Attr[typedefs.Coordinate] = None


class CyAttr(common.Attr):
    cy: models.Attr[typedefs.Coordinate] = None


class DAttr(common.Attr):
    d: models.Attr[typedefs.PathData] = None


class DescentAttr(common.Attr):
    descent: models.Attr[typedefs.Number] = None


class DiffuseConstantAttr(common.Attr):
    diffuseConstant: models.Attr[typedefs.Number] = None


class DivisorAttr(common.Attr):
    divisor: models.Attr[typedefs.Number] = None


class DurAttr(common.Attr):
    dur: models.Attr[
        typedefs.ClockValue | Literal["media", "indefinite"]
    ] = None


class DxListOfLengthsAttr(common.Attr):
    dx: models.Attr[typedefs.ListOfLengths] = None


class DxNumberAttr(common.Attr):
    dx: models.Attr[typedefs.Number] = None


class DyListOfLengthsAttr(common.Attr):
    dy: models.Attr[typedefs.ListOfLengths] = None


class DyNumberAttr(common.Attr):
    dy: models.Attr[typedefs.Number] = None


class EdgeModeAttr(common.Attr):
    edgeMode: models.Attr[Literal["duplicate", "wrap", "none"]] = None


class ElevationAttr(common.Attr):
    elevation: models.Attr[typedefs.Number] = None


class EndAttr(common.Attr):
    end: models.Attr[typedefs.EndValueList] = None


class ExponentAttr(common.Attr):
    exponent: models.Attr[typedefs.Number] = None


class ExternalResourcesRequiredAttr(common.Attr):
    externalResourcesRequired: models.Attr[typedefs.Boolean] = None


class FilterResAttr(common.Attr):
    filterRes: models.Attr[typedefs.NumberOptionalNumber] = None


class FilterUnitsAttr(common.Attr):
    filterUnits: models.Attr[
        Literal["userSpaceOnUse", "objectBoundingBox"]
    ] = None


class FormatAttr(common.Attr):
    format: models.Attr[typedefs.Unparsed] = None


class FrAttr(common.Attr):
    fr: models.Attr[typedefs.Length] = None


class FromAttr(common.Attr):
    from_: models.Attr[typedefs.Unparsed] = None


class FxAttr(common.Attr):
    fx: models.Attr[typedefs.Coordinate] = None


class FyAttr(common.Attr):
    fy: models.Attr[typedefs.Coordinate] = None


class G1Attr(common.Attr):
    g1: models.Attr[typedefs.ListOfNames] = None


class G2Attr(common.Attr):
    g2: models.Attr[typedefs.ListOfNames] = None


class GlyphNameAttr(common.Attr):
    glyph_name: models.Attr[typedefs.ListOfNames] = None


class GlyphRefAttr(common.Attr):
    glyphRef: models.Attr[typedefs.Unparsed] = None


class GradientTransformAttr(common.Attr):
    gradientTransform: models.Attr[typedefs.TransformList] = None


class GradientUnitsAttr(common.Attr):
    gradientUnits: models.Attr[
        Literal["userSpaceOnUse", "objectBoundingBox"]
    ] = None


class HangingAttr(common.Attr):
    hanging: models.Attr[typedefs.Number] = None


class HeightAttr(common.Attr):
    height: models.Attr[typedefs.Length] = None


class HorizAdvXAttr(common.Attr):
    horiz_adv_x: models.Attr[typedefs.Number] = None


class HorizOriginXAttr(common.Attr):
    horiz_origin_x: models.Attr[typedefs.Number] = None


class HorizOriginYAttr(common.Attr):
    horiz_origin_y: models.Attr[typedefs.Number] = None


class HrefAttr(common.Attr):
    href: models.Attr[typedefs.Iri] = None


class IdAttr(common.Attr):
    id: models.Attr[typedefs.Name] = None


class IdeographicAttr(common.Attr):
    ideographic: models.Attr[typedefs.Number] = None


class InAttr(common.Attr):
    in_: models.Attr[
        typedefs.Paint
        | typedefs.FilterPrimitiveReference
        | typedefs.Unparsed
    ] = None


class In2Attr(common.Attr):
    in2: models.Attr[
        typedefs.Paint
        | typedefs.FilterPrimitiveReference
        | typedefs.Unparsed
    ] = None


class InterceptAttr(common.Attr):
    intercept: models.Attr[typedefs.Number] = None


class KAttr(common.Attr):
    k: models.Attr[typedefs.Number] = None


class K1Attr(common.Attr):
    k1: models.Attr[typedefs.Number] = None


class K2Attr(common.Attr):
    k2: models.Attr[typedefs.Number] = None


class K3Attr(common.Attr):
    k3: models.Attr[typedefs.Number] = None


class K4Attr(common.Attr):
    k4: models.Attr[typedefs.Number] = None


class KernelMatrixAttr(common.Attr):
    kernelMatrix: models.Attr[typedefs.ListOfNumbers] = None


class KernelUnitLengthAttr(common.Attr):
    kernelUnitLength: models.Attr[typedefs.NumberOptionalNumber] = None


class KeyPointsAttr(common.Attr):
    keyPoints: models.Attr[typedefs.ListOfNumbers] = None


class KeySplinesAttr(common.Attr):
    keySplines: models.Attr[typedefs.Unparsed] = None


class KeyTimesAttr(common.Attr):
    keyTimes: models.Attr[typedefs.Unparsed] = None


class LangAttr(common.Attr):
    lang: models.Attr[typedefs.LanguageTag] = None


class LangGlyphAttr(common.Attr):
    lang: models.Attr[typedefs.LanguageCodes] = None


class LengthAdjustAttr(common.Attr):
    lengthAdjust: models.Attr[Literal["spacing", "spacingAndGlyphs"]] = (
        None
    )


class LimitingConeAngleAttr(common.Attr):
    limitingConeAngle: models.Attr[typedefs.Number] = None


class LocalAttr(common.Attr):
    local: models.Attr[typedefs.Unparsed] = None


class MarkerHeightAttr(common.Attr):
    markerHeight: models.Attr[typedefs.Length] = None


class MarkerUnitsAttr(common.Attr):
    markerUnits: models.Attr[Literal["strokeWidth", "userSpaceOnUse"]] = (
        None
    )


class MarkerWidthAttr(common.Attr):
    markerWidth: models.Attr[typedefs.Length] = None


class MaskContentUnitsAttr(common.Attr):
    maskContentUnits: models.Attr[
        Literal["userSpaceOnUse", "objectBoundingBox"]
    ] = None


class MaskUnitsAttr(common.Attr):
    maskUnits: models.Attr[
        Literal["userSpaceOnUse", "objectBoundingBox"]
    ] = None


class MathematicalAttr(common.Attr):
    mathematical: models.Attr[typedefs.Number] = None


class MaxAttr(common.Attr):
    max: models.Attr[Literal["media"] | typedefs.ClockValue] = None


class MediaAttr(common.Attr):
    media: models.Attr[typedefs.MediaDescriptors] = None


class MethodAttr(common.Attr):
    method: models.Attr[Literal["align", "stretch"]] = None


class MinAttr(common.Attr):
    min: models.Attr[Literal["media"] | typedefs.ClockValue] = None


class ModeAttr(common.Attr):
    mode: models.Attr[
        Literal["normal", "multiply", "screen", "darken", "lighten"]
    ] = None


class NameNameAttr(common.Attr):
    name: models.Attr[typedefs.Name] = None


class NameAnythingAttr(common.Attr):
    name: models.Attr[typedefs.Anything] = None


class NumOctavesAttr(common.Attr):
    numOctaves: models.Attr[typedefs.Integer] = None


class OffsetNumberPercentageAttr(common.Attr):
    offset: models.Attr[typedefs.Number | typedefs.Percentage] = None


class OffsetNumberAttr(common.Attr):
    offset: models.Attr[typedefs.Number] = None


class OnAbortAttr(common.Attr):
    onabort: models.Attr[typedefs.Anything] = None


class OnActivateAttr(common.Attr):
    onactivate: models.Attr[typedefs.Anything] = None


class OnBeginAttr(common.Attr):
    onbegin: models.Attr[typedefs.Anything] = None


class OnClickAttr(common.Attr):
    onclick: models.Attr[typedefs.Anything] = None


class OnEndAttr(common.Attr):
    onend: models.Attr[typedefs.Anything] = None


class OnErrorAttr(common.Attr):
    onerror: models.Attr[typedefs.Anything] = None


class OnFocusInAttr(common.Attr):
    onfocusin: models.Attr[typedefs.Anything] = None


class OnFocusOutAttr(common.Attr):
    onfocusout: models.Attr[typedefs.Anything] = None


class OnLoadAttr(common.Attr):
    onload: models.Attr[typedefs.Anything] = None


class OnMouseDownAttr(common.Attr):
    onmousedown: models.Attr[typedefs.Anything] = None


class OnMouseMoveAttr(common.Attr):
    onmousemove: models.Attr[typedefs.Anything] = None


class OnMouseOutAttr(common.Attr):
    onmouseout: models.Attr[typedefs.Anything] = None


class OnMouseOverAttr(common.Attr):
    onmouseover: models.Attr[typedefs.Anything] = None


class OnMouseUpAttr(common.Attr):
    onmouseup: models.Attr[typedefs.Anything] = None


class OnRepeatAttr(common.Attr):
    onrepeat: models.Attr[typedefs.Anything] = None


class OnResizeAttr(common.Attr):
    onresize: models.Attr[typedefs.Anything] = None


class OnScrollAttr(common.Attr):
    onscroll: models.Attr[typedefs.Anything] = None


class OnUnloadAttr(common.Attr):
    onunload: models.Attr[typedefs.Anything] = None


class OnZoomAttr(common.Attr):
    onzoom: models.Attr[typedefs.Anything] = None


class OperatorFeCompositeAttr(common.Attr):
    operator: models.Attr[
        Literal["over", "in", "out", "atop", "xor", "arithmetic"]
    ] = None


class OperatorFeMorphologyAttr(common.Attr):
    operator: models.Attr[Literal["erode", "dilate"]] = None


class OrderAttr(common.Attr):
    order: models.Attr[typedefs.NumberOptionalNumber] = None


class OrientAttr(common.Attr):
    orient: models.Attr[
        typedefs.Auto | Literal["auto-start-reverse"] | typedefs.Angle
    ] = None


class OrientationAttr(common.Attr):
    orientation: models.Attr[Literal["h", "v"]] = None


class OriginAttr(common.Attr):
    origin: models.Attr[Literal["default"]] = None


class OverlinePositionAttr(common.Attr):
    overline_position: models.Attr[typedefs.Number] = None


class OverlineThicknessAttr(common.Attr):
    overline_thickness: models.Attr[typedefs.Number] = None


class Panose1Attr(common.Attr):
    panose1: models.Attr[
        models.Tuple[
            tuple[
                typedefs.Integer,
                typedefs.Integer,
                typedefs.Integer,
                typedefs.Integer,
                typedefs.Integer,
                typedefs.Integer,
                typedefs.Integer,
                typedefs.Integer,
                typedefs.Integer,
                typedefs.Integer,
            ]
        ]
    ] = None


class PathAttr(common.Attr):
    path: models.Attr[typedefs.PathData] = None


class PathLengthAttr(common.Attr):
    pathLength: models.Attr[typedefs.Number] = None


class PatternContentUnitsAttr(common.Attr):
    patternContentUnits: models.Attr[
        Literal["userSpaceOnUse", "objectBoundingBox"]
    ] = None


class PatternTransformAttr(common.Attr):
    patternTransform: models.Attr[typedefs.TransformList] = None


class PatternUnitsAttr(common.Attr):
    patternUnits: models.Attr[
        Literal["userSpaceOnUse", "objectBoundingBox"]
    ] = None


class PointsAttr(common.Attr):
    points: models.Attr[typedefs.ListOfPoints] = None


class PointsAtXAttr(common.Attr):
    pointsAtX: models.Attr[typedefs.Number] = None


class PointsAtYAttr(common.Attr):
    pointsAtY: models.Attr[typedefs.Number] = None


class PointsAtZAttr(common.Attr):
    pointsAtZ: models.Attr[typedefs.Number] = None


class PreserveAlphaAttr(common.Attr):
    preserveAlpha: models.Attr[typedefs.Boolean] = None


class PreserveAspectRatioAttr(common.Attr):
    preserveAspectRatio: models.Attr[
        None
        | Literal[
            "xMinYMin",
            "xMidYMin",
            "xMaxYMin",
            "xMinYMid",
            "xMidYMid",
            "xMaxYMid",
            "xMinYMax",
            "xMidYMax",
            "xMaxYMax",
        ]
        | typedefs.Unparsed
    ] = None


class PrimitiveUnitsAttr(common.Attr):
    primitiveUnits: models.Attr[
        Literal["userSpaceOnUse", "objectBoundingBox"]
    ] = None


class RAttr(common.Attr):
    r: models.Attr[typedefs.Length] = None


class RadiusAttr(common.Attr):
    radius: models.Attr[typedefs.NumberOptionalNumber] = None


class RefXAttr(common.Attr):
    ref_x: models.Attr[
        Literal["left", "center", "right"] | typedefs.Coordinate
    ] = None


class RefYAttr(common.Attr):
    ref_y: models.Attr[
        Literal["top", "center", "bottom"] | typedefs.Coordinate
    ] = None


class RenderingIntentAttr(common.Attr):
    rendering_intent: models.Attr[
        Literal[
            "auto",
            "perceptual",
            "relative-colorimetric",
            "saturation",
            "absolute-colorimetric",
        ]
    ] = None


class RepeatCountAttr(common.Attr):
    repeatCount: models.Attr[
        Literal["indefinite"] | typedefs.NumericValue
    ] = None


class RepeatDurAttr(common.Attr):
    repeatDur: models.Attr[Literal["indefinite"] | typedefs.ClockValue] = (
        None
    )


class RequiredExtensionsAttr(common.Attr):
    requiredExtensions: models.Attr[typedefs.ListOfExtensions] = None


class RequiredFeaturesAttr(common.Attr):
    requiredFeatures: models.Attr[typedefs.ListOfFeatures] = None


class RestartAttr(common.Attr):
    restart: models.Attr[Literal["always", "whenNotActive", "never"]] = (
        None
    )


class ResultAttr(common.Attr):
    result: models.Attr[typedefs.FilterPrimitiveReference] = None


class RotateListOfNumbersAttr(common.Attr):
    rotate: models.Attr[typedefs.ListOfNumbers] = None


class RotateNumberAutoAutoReverseAttr(common.Attr):
    rotate: (
        models.Attr[typedefs.Number]
        | typedefs.Auto
        | Literal["auto-reverse"]
    ) = None


class RxAttr(common.Attr):
    rx: models.Attr[typedefs.Length] = None


class RyAttr(common.Attr):
    ry: models.Attr[typedefs.Length] = None


class ScaleAttr(common.Attr):
    scale: models.Attr[typedefs.Number] = None


class SeedAttr(common.Attr):
    seed: models.Attr[typedefs.Number] = None


class SlopeAttr(common.Attr):
    slope: models.Attr[typedefs.Number] = None


class SpacingAttr(common.Attr):
    spacing: models.Attr[Literal["auto", "exact"]] = None


class SpecularConstantAttr(common.Attr):
    specularConstant: models.Attr[typedefs.Number] = None


class SpecularExponentAttr(common.Attr):
    specularExponent: models.Attr[typedefs.Number] = None


class SpreadMethodAttr(common.Attr):
    spreadMethod: models.Attr[Literal["pad", "reflect", "repeat"]] = None


class StartOffsetAttr(common.Attr):
    startOffset: models.Attr[typedefs.Length] = None


class StdDeviationAttr(common.Attr):
    stdDeviation: models.Attr[typedefs.NumberOptionalNumber] = None


class StemhAttr(common.Attr):
    stemh: models.Attr[typedefs.Number] = None


class StemvAttr(common.Attr):
    stemv: models.Attr[typedefs.Number] = None


class StitchTilesAttr(common.Attr):
    stitchTiles: models.Attr[Literal["stitch", "noStitch"]] = None


class StrikethroughPositionAttr(common.Attr):
    strikethrough_position: models.Attr[typedefs.Number] = None


class StrikethroughThicknessAttr(common.Attr):
    strikethrough_thickness: models.Attr[typedefs.Number] = None


class StringAttr(common.Attr):
    string: models.Attr[typedefs.Anything] = None


class StyleAttr(common.Attr):
    style: models.Attr[typedefs.Unparsed] = None


class SurfaceScaleAttr(common.Attr):
    surfaceScale: models.Attr[typedefs.Number] = None


class SystemLanguageAttr(common.Attr):
    systemLanguage: models.Attr[typedefs.LanguageCodes] = None


class TableValuesAttr(common.Attr):
    tableValues: models.Attr[typedefs.ListOfNumbers] = None


class TargetAttr(common.Attr):
    target: models.Attr[
        Literal["_replace", "_self", "_parent", "_top", "_blank"]
        | typedefs.XmlName
    ] = None


class TargetXAttr(common.Attr):
    targetX: models.Attr[typedefs.Integer] = None


class TargetYAttr(common.Attr):
    targetY: models.Attr[typedefs.Integer] = None


class TextLengthAttr(common.Attr):
    textLength: models.Attr[typedefs.Length] = None


class TitleAttr(common.Attr):
    title: models.Attr[typedefs.AdvisoryTitle] = None


class ToAttr(common.Attr):
    to: models.Attr[typedefs.Unparsed] = None


class TypeAnimateTransformAttr(common.Attr):
    type: models.Attr[
        Literal["translate", "scale", "rotate", "skewX", "skewY"]
    ] = None


class TypeFeColorMatrixAttr(common.Attr):
    type: models.Attr[
        Literal["matrix", "saturate", "hueRotate", "luminanceToAlpha"]
    ] = None


class TypeFeTurbluenceAttr(common.Attr):
    type: models.Attr[Literal["fractalNoise", "turbulence"]] = None


class TypeContentTypeAttr(common.Attr):
    type: models.Attr[typedefs.ContentType] = None


class TypeFeFuncAttr(common.Attr):
    type: models.Attr[
        Literal["identity", "table", "discrete", "linear", "gamma"]
    ] = None


class U1Attr(common.Attr):
    u1: models.Attr[models.List[typedefs.Character | typedefs.Urange]] = (
        None
    )


class U2Attr(common.Attr):
    u2: models.Attr[models.List[typedefs.Character | typedefs.Urange]] = (
        None
    )


class UnderlinePositionAttr(common.Attr):
    underline_position: models.Attr[typedefs.Number] = None


class UnderlineThicknessAttr(common.Attr):
    underline_thickness: models.Attr[typedefs.Number] = None


class UnicodeAttr(common.Attr):
    unicode: models.Attr[typedefs.Anything] = None


class UnicodeRangeAttr(common.Attr):
    unicode_range: models.Attr[models.List[typedefs.Urange]] = None


class UnitsPerEmAttr(common.Attr):
    units_per_em: models.Attr[typedefs.Number] = None


class VAlphabeticAttr(common.Attr):
    v_alphabetic: models.Attr[typedefs.Number] = None


class VHangingAttr(common.Attr):
    v_hanging: models.Attr[typedefs.Number] = None


class VIdeographicAttr(common.Attr):
    v_ideographic: models.Attr[typedefs.Number] = None


class VMathematicalAttr(common.Attr):
    v_mathematical: models.Attr[typedefs.Number] = None


class ValuesListOfNumbersAttr(common.Attr):
    values: models.Attr[typedefs.ListOfNumbers] = None


class ValuesListAttr(common.Attr):
    values: models.Attr[typedefs.Unparsed] = None


class VersionAttr(common.Attr):
    version: models.Attr[Literal["1.0", "1.1", "1.2"]] = None


class VertAdvYAttr(common.Attr):
    vert_adv_y: models.Attr[typedefs.Number] = None


class VertOriginXAttr(common.Attr):
    vert_origin_x: models.Attr[typedefs.Number] = None


class VertOriginYAttr(common.Attr):
    vert_origin_y: models.Attr[typedefs.Number] = None


class ViewBoxAttr(common.Attr):
    viewBox: models.Attr[
        models.Tuple4[
            typedefs.Number,
            typedefs.Number,
            typedefs.Number,
            typedefs.Number,
        ]
    ] = None


class ViewTargetAttr(common.Attr):
    viewTarget: models.Attr[models.List[typedefs.XmlName]] = None


class WidthAttr(common.Attr):
    width: models.Attr[typedefs.Length] = None


class WidthsAttr(common.Attr):
    widths: models.Attr[
        models.List[
            typedefs.Urange
            | models.Tuple2[typedefs.Urange, typedefs.Number]
        ]
    ] = None


class XListOfCoordinatesAttr(common.Attr):
    x: models.Attr[typedefs.ListOfCoordinates] = None


class XCoordinateAttr(common.Attr):
    x: models.Attr[typedefs.Coordinate] = None


class XNumberAttr(common.Attr):
    x: models.Attr[typedefs.Number] = None


class XHeightAttr(common.Attr):
    x_height: models.Attr[typedefs.Number] = None


class X1Attr(common.Attr):
    x1: models.Attr[typedefs.Coordinate] = None


class X2Attr(common.Attr):
    x2: models.Attr[typedefs.Coordinate] = None


class XChannelSelectorAttr(common.Attr):
    xChannelSelector: models.Attr[Literal["R", "G", "B", "A"]] = None


class XlinkActuateOnRequestAttr(common.Attr):
    xlink_actuate: models.Attr[Literal["onRequest"]] = None


class XlinkActuateOnLoadAttr(common.Attr):
    xlink_actuate: models.Attr[Literal["onLoad"]] = None


class XlinkArcroleAttr(common.Attr):
    xlink_arcrole: models.Attr[typedefs.Iri] = None


class XlinkHrefAttr(common.Attr):
    xlink_href: models.Attr[typedefs.Iri] = None


class XlinkRoleAttr(common.Attr):
    xlink_role: models.Attr[typedefs.Iri] = None


class XlinkShowAttr(common.Attr):
    xlink_show: models.Attr[
        Literal["new", "replace", "embed", "other", "none"]
    ] = None


class XlinkTitleAttr(common.Attr):
    xlink_title: models.Attr[typedefs.Anything] = None


class XlinkTypeAttr(common.Attr):
    xlink_type: models.Attr[Literal["simple"]] = None


class XmlBaseAttr(common.Attr):
    xml_base: models.Attr[typedefs.Iri] = None


class XmlLangAttr(common.Attr):
    xml_lang: models.Attr[typedefs.LanguageId] = None


class XmlnsAttr(common.Attr):
    xmlns: models.Attr[utiltypes.Xmlns] = None


class XmlSpaceAttr(common.Attr):
    xml_space: models.Attr[Literal["default", "preserve"]] = None


class YListOfCoordinatesAttr(common.Attr):
    y: models.Attr[typedefs.ListOfCoordinates] = None


class YCoordinateAttr(common.Attr):
    y: models.Attr[typedefs.Coordinate] = None


class YNumberAttr(common.Attr):
    y: models.Attr[typedefs.Number] = None


class Y1Attr(common.Attr):
    y1: models.Attr[typedefs.Coordinate] = None


class Y2Attr(common.Attr):
    y2: models.Attr[typedefs.Coordinate] = None


class YChannelSelectorAttr(common.Attr):
    yChannelSelector: models.Attr[Literal["R", "G", "B", "A"]] = None


class ZAttr(common.Attr):
    z: models.Attr[typedefs.Number] = None


class ZoomAndPanAttr(common.Attr):
    zoomAndPan: models.Attr[Literal["disable", "magnify"]] = None
