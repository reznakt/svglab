"""Definitions of all SVG attributes."""

# ruff: noqa: N815, D101

import pydantic
from typing_extensions import Annotated, Literal, TypeAlias

from svglab import models, utiltypes
from svglab.attrs import typedefs


class Attr(models.BaseModel):
    pass


class AccentHeightAttr(Attr):
    accent_height: models.Attr[typedefs.Number] = None


class AccumulateAttr(Attr):
    accumulate: models.Attr[typedefs.None_ | Literal["sum"]] = None


class AdditiveAttr(Attr):
    additive: models.Attr[Literal["replace", "sum"]] = None


class AlignmentBaselineAttr(Attr):
    alignment_baseline: models.Attr[
        typedefs.Auto
        | typedefs.Inherit
        | Literal[
            "baseline",
            "before-edge",
            "text-before-edge",
            "middle",
            "central",
            "after-edge",
            "text-after-edge",
            "ideographic",
            "alphabetic",
            "hanging",
            "mathematical",
        ]
    ] = None


class AlphabeticAttr(Attr):
    alphabetic: models.Attr[typedefs.Number] = None


class AmplitudeAttr(Attr):
    amplitude: models.Attr[typedefs.Number] = None


class ArabicFormAttr(Attr):
    arabic_form: models.Attr[
        Literal["initial", "medial", "terminal", "isolated"]
    ] = None


class AscentAttr(Attr):
    ascent: models.Attr[typedefs.Number] = None


class AttributeNameAttr(Attr):
    attributeName: models.Attr[typedefs.Unparsed] = None


class AttributeTypeAttr(Attr):
    attributeType: models.Attr[Literal["CSS", "XML"] | typedefs.Auto] = (
        None
    )


class AzimuthAttr(Attr):
    azimuth: models.Attr[typedefs.Number] = None


class BaseFrequencyAttr(Attr):
    baseFrequency: models.Attr[typedefs.NumberOptionalNumber] = None


class BaselineShiftAttr(Attr):
    baseline_shift: models.Attr[
        Literal["baseline", "sub", "super"]
        | typedefs.Percentage
        | typedefs.Length
        | typedefs.Inherit
    ] = None


class BaseProfileAttr(Attr):
    baseProfile: models.Attr[typedefs.ProfileName] = None


class BboxAttr(Attr):
    bbox: models.Attr[
        models.Tuple4[
            typedefs.Number,
            typedefs.Number,
            typedefs.Number,
            typedefs.Number,
        ]
    ] = None


class BeginAttr(Attr):
    begin: models.Attr[typedefs.BeginValueList] = None


class BiasAttr(Attr):
    bias: models.Attr[typedefs.Number] = None


class ByAttr(Attr):
    by: models.Attr[typedefs.Unparsed] = None


class CalcModeAttr(Attr):
    calcMode: models.Attr[
        Literal["discrete", "linear", "paced", "spline"]
    ] = None


class CapHeightAttr(Attr):
    cap_height: models.Attr[typedefs.Number] = None


class ClassAttr(Attr):
    class_: models.Attr[typedefs.ListOfStrings] = None


class ClipAttr(Attr):
    clip: models.Attr[
        typedefs.Shape | typedefs.Auto | typedefs.Inherit
    ] = None


class ClipPathAttr(Attr):
    clip_path: models.Attr[
        typedefs.FuncIri | typedefs.None_ | typedefs.Inherit
    ] = None


class ClipPathUnitsAttr(Attr):
    clipPathUnits: models.Attr[
        Literal["userSpaceOnUse", "objectBoundingBox"]
    ] = None


class ClipRuleAttr(Attr):
    clip_rule: models.Attr[
        Literal["nonzero", "evenodd"] | typedefs.Inherit
    ] = None


class ColorAttr(Attr):
    color: models.Attr[typedefs.Color | typedefs.Inherit] = None


class ColorInterpolationAttr(Attr):
    color_interpolation: models.Attr[
        typedefs.Auto | Literal["sRGB", "linearRGB"] | typedefs.Inherit
    ] = None


class ColorInterpolationFiltersAttr(Attr):
    color_interpolation_filters: models.Attr[
        typedefs.Auto | Literal["sRGB", "linearRGB"] | typedefs.Inherit
    ] = None


class ColorProfileAttr(Attr):
    color_profile: models.Attr[
        typedefs.Auto
        | Literal["sRGB"]
        | typedefs.Name
        | typedefs.Iri
        | typedefs.Inherit
    ] = None


class ColorRenderingAttr(Attr):
    color_rendering: models.Attr[
        typedefs.Auto
        | Literal["optimizeSpeed", "optimizeQuality"]
        | typedefs.Inherit
    ] = None


class ContentScriptTypeAttr(Attr):
    contentScriptType: models.Attr[typedefs.ContentType] = None


class ContentStyleTypeAttr(Attr):
    contentStyleType: models.Attr[typedefs.ContentType] = None


class CursorAttr(Attr):
    cursor: models.Attr[
        typedefs.CursorValue
        | typedefs.Inherit
        | models.List[typedefs.CursorValue]
    ] = None


class CxAttr(Attr):
    cx: models.Attr[typedefs.Coordinate] = None


class CyAttr(Attr):
    cy: models.Attr[typedefs.Coordinate] = None


class DAttr(Attr):
    d: models.Attr[typedefs.PathData] = None


class DescentAttr(Attr):
    descent: models.Attr[typedefs.Number] = None


class DiffuseConstantAttr(Attr):
    diffuseConstant: models.Attr[typedefs.Number] = None


class DirectionAttr(Attr):
    direction: models.Attr[Literal["ltr", "rtl"] | typedefs.Inherit] = None


class DisplayAttr(Attr):
    display: models.Attr[
        Literal[
            "block",
            "compact",
            "inline-table",
            "inline",
            "list-item",
            "marker",
            "run-in",
            "table-caption",
            "table-cell",
            "table-column-group",
            "table-column",
            "table-footer-group",
            "table-header-group",
            "table-row-group",
            "table-row",
            "table",
        ]
        | typedefs.None_
        | typedefs.Inherit
    ] = None


class DivisorAttr(Attr):
    divisor: models.Attr[typedefs.Number] = None


class DominantBaselineAttr(Attr):
    dominant_baseline: models.Attr[
        typedefs.Auto
        | Literal[
            "use-script",
            "no-change",
            "reset-size",
            "ideographic",
            "alphabetic",
            "hanging",
            "mathematical",
            "central",
            "middle",
            "text-after-edge",
            "text-before-edge",
        ]
        | typedefs.Inherit
    ] = None


class DurAttr(Attr):
    dur: models.Attr[
        typedefs.ClockValue | Literal["media", "indefinite"]
    ] = None


class DxListOfLengthsAttr(Attr):
    dx: models.Attr[typedefs.ListOfLengths] = None


class DxNumberAttr(Attr):
    dx: models.Attr[typedefs.Number] = None


class DyListOfLengthsAttr(Attr):
    dy: models.Attr[typedefs.ListOfLengths] = None


class DyNumberAttr(Attr):
    dy: models.Attr[typedefs.Number] = None


class EdgeModeAttr(Attr):
    edgeMode: models.Attr[Literal["duplicate", "wrap", "none"]] = None


class ElevationAttr(Attr):
    elevation: models.Attr[typedefs.Number] = None


class EnableBackgroundAttr(Attr):
    enable_background: models.Attr[
        Literal["accumulate"]
        | typedefs.Inherit
        | typedefs.Unparsed  # new [ <x> <y> <width> <height> ]
    ] = None


class EndAttr(Attr):
    end: models.Attr[typedefs.EndValueList] = None


class ExponentAttr(Attr):
    exponent: models.Attr[typedefs.Number] = None


class ExternalResourcesRequiredAttr(Attr):
    externalResourcesRequired: models.Attr[typedefs.Boolean] = None


class FillAttr(Attr):
    fill: models.Attr[typedefs.Paint | Literal["freeze", "remove"]] = None


class FillOpacityAttr(Attr):
    fill_opacity: models.Attr[typedefs.OpacityValue | typedefs.Inherit] = (
        None
    )


class FillRuleAttr(Attr):
    fill_rule: models.Attr[
        Literal["nonzero", "evenodd"] | typedefs.Inherit
    ] = None


class FilterAttr(Attr):
    filter: models.Attr[
        typedefs.FuncIri | typedefs.None_ | typedefs.Inherit
    ] = None


class FilterResAttr(Attr):
    filterRes: models.Attr[typedefs.NumberOptionalNumber] = None


class FilterUnitsAttr(Attr):
    filterUnits: models.Attr[
        Literal["userSpaceOnUse", "objectBoundingBox"]
    ] = None


class FloodColorAttr(Attr):
    flood_color: models.Attr[
        Literal["currentColor"]
        | typedefs.Inherit
        | typedefs.IccColor
        | typedefs.Color
    ] = None


class FloodOpacityAttr(Attr):
    flood_opacity: models.Attr[
        typedefs.OpacityValue | typedefs.Inherit
    ] = None


class FontFamilyAttr(Attr):
    font_family: models.Attr[
        models.List[typedefs.FamilyName | typedefs.GenericFamily]
        | typedefs.Inherit
    ] = None


class FontSizeAttr(Attr):
    font_size: models.Attr[
        typedefs.AbsoluteSize
        | typedefs.RelativeSize
        | typedefs.Length
        | typedefs.Percentage
        | typedefs.Inherit
        | typedefs.All
        | typedefs.ListOfLengths
    ] = None


class FontSizeAdjustAttr(Attr):
    font_size_adjust: models.Attr[
        typedefs.Number | typedefs.None_ | typedefs.Inherit
    ] = None


class FontStretchAttr(Attr):
    font_stretch: models.Attr[
        typedefs.All
        | Literal[
            "condensed ",
            "condensed",
            "expanded",
            "extra-condensed",
            "extra-expanded",
            "narrower",
            "normal",
            "semi-condensed",
            "semi-expanded",
            "ultra-condensed",
            "ultra-expanded",
            "wider",
        ]
        | typedefs.Inherit
    ] = None


class FontStyleAttr(Attr):
    font_style: models.Attr[
        typedefs.All
        | models.List[Literal["normal", "italic", "oblique"]]
        | typedefs.Inherit
    ] = None


class FontVariantAttr(Attr):
    font_variant: models.Attr[
        Literal["normal", "small-caps"] | typedefs.Inherit
    ] = None


# a BeforeValidator must be used on non-string literals; pydantic will not
# coerce literal values
_FontWeightInt: TypeAlias = Annotated[
    Literal[100, 200, 300, 400, 500, 600, 700, 800, 900],
    pydantic.BeforeValidator(int),
]


class FontWeightAttr(Attr):
    font_weight: models.Attr[
        typedefs.All
        | typedefs.Inherit
        | models.List[
            Literal["normal", "bold", "bolder", "lighter"] | _FontWeightInt
        ]
    ] = None


class FormatAttr(Attr):
    format: models.Attr[typedefs.Unparsed] = None


class FrAttr(Attr):
    fr: models.Attr[typedefs.Length] = None


class FromAttr(Attr):
    from_: models.Attr[typedefs.Unparsed] = None


class FxAttr(Attr):
    fx: models.Attr[typedefs.Coordinate] = None


class FyAttr(Attr):
    fy: models.Attr[typedefs.Coordinate] = None


class G1Attr(Attr):
    g1: models.Attr[typedefs.ListOfNames] = None


class G2Attr(Attr):
    g2: models.Attr[typedefs.ListOfNames] = None


class GlyphNameAttr(Attr):
    glyph_name: models.Attr[typedefs.ListOfNames] = None


class GlyphOrientationHorizontalAttr(Attr):
    glyph_orientation_horizontal: models.Attr[
        typedefs.Angle | typedefs.Inherit
    ] = None


class GlyphOrientationVerticalAttr(Attr):
    glyph_orientation_vertical: models.Attr[
        typedefs.Auto | typedefs.Angle | typedefs.Inherit
    ] = None


class GlyphRefAttr(Attr):
    glyphRef: models.Attr[typedefs.Unparsed] = None


class GradientTransformAttr(Attr):
    gradientTransform: models.Attr[typedefs.TransformList] = None


class GradientUnitsAttr(Attr):
    gradientUnits: models.Attr[
        Literal["userSpaceOnUse", "objectBoundingBox"]
    ] = None


class HangingAttr(Attr):
    hanging: models.Attr[typedefs.Number] = None


class HeightAttr(Attr):
    height: models.Attr[typedefs.Length] = None


class HorizAdvXAttr(Attr):
    horiz_adv_x: models.Attr[typedefs.Number] = None


class HorizOriginXAttr(Attr):
    horiz_origin_x: models.Attr[typedefs.Number] = None


class HorizOriginYAttr(Attr):
    horiz_origin_y: models.Attr[typedefs.Number] = None


class HrefAttr(Attr):
    href: models.Attr[typedefs.Iri] = None


class IdAttr(Attr):
    id: models.Attr[typedefs.Name] = None


class IdeographicAttr(Attr):
    ideographic: models.Attr[typedefs.Number] = None


class ImageRenderingAttr(Attr):
    image_rendering: models.Attr[
        typedefs.Auto
        | Literal["optimizeSpeed", "optimizeQuality"]
        | typedefs.Inherit
    ] = None


class In2Attr(Attr):
    in2: models.Attr[
        typedefs.Paint
        | typedefs.FilterPrimitiveReference
        | typedefs.Unparsed
    ] = None


class InAttr(Attr):
    in_: models.Attr[
        typedefs.Paint
        | typedefs.FilterPrimitiveReference
        | typedefs.Unparsed
    ] = None


class InterceptAttr(Attr):
    intercept: models.Attr[typedefs.Number] = None


class K1Attr(Attr):
    k1: models.Attr[typedefs.Number] = None


class K2Attr(Attr):
    k2: models.Attr[typedefs.Number] = None


class K3Attr(Attr):
    k3: models.Attr[typedefs.Number] = None


class K4Attr(Attr):
    k4: models.Attr[typedefs.Number] = None


class KAttr(Attr):
    k: models.Attr[typedefs.Number] = None


class KernelMatrixAttr(Attr):
    kernelMatrix: models.Attr[typedefs.ListOfNumbers] = None


class KernelUnitLengthAttr(Attr):
    kernelUnitLength: models.Attr[typedefs.NumberOptionalNumber] = None


class KerningAttr(Attr):
    kerning: models.Attr[
        typedefs.Auto | typedefs.Length | typedefs.Inherit
    ] = None


class KeyPointsAttr(Attr):
    keyPoints: models.Attr[typedefs.ListOfNumbers] = None


class KeySplinesAttr(Attr):
    keySplines: models.Attr[typedefs.Unparsed] = None


class KeyTimesAttr(Attr):
    keyTimes: models.Attr[typedefs.Unparsed] = None


class LangAttr(Attr):
    lang: models.Attr[typedefs.LanguageTag] = None


class LangGlyphAttr(Attr):
    lang: models.Attr[typedefs.LanguageCodes] = None


class LengthAdjustAttr(Attr):
    lengthAdjust: models.Attr[Literal["spacing", "spacingAndGlyphs"]] = (
        None
    )


class LetterSpacingAttr(Attr):
    letter_spacing: models.Attr[
        Literal["normal"] | typedefs.Length | typedefs.Inherit
    ] = None


class LightingColorAttr(Attr):
    lighting_color: models.Attr[
        Literal["currentColor"]
        | typedefs.Color
        | typedefs.Inherit
        | typedefs.Unparsed
    ] = None


class LimitingConeAngleAttr(Attr):
    limitingConeAngle: models.Attr[typedefs.Number] = None


class LocalAttr(Attr):
    local: models.Attr[typedefs.Unparsed] = None


class MarkerEndAttr(Attr):
    marker_end: models.Attr[
        typedefs.FuncIri | typedefs.None_ | typedefs.Inherit
    ] = None


class MarkerHeightAttr(Attr):
    markerHeight: models.Attr[typedefs.Length] = None


class MarkerMidAttr(Attr):
    marker_mid: models.Attr[
        typedefs.FuncIri | typedefs.None_ | typedefs.Inherit
    ] = None


class MarkerStartAttr(Attr):
    marker_start: models.Attr[
        typedefs.FuncIri | typedefs.None_ | typedefs.Inherit
    ] = None


class MarkerUnitsAttr(Attr):
    markerUnits: models.Attr[Literal["strokeWidth", "userSpaceOnUse"]] = (
        None
    )


class MarkerWidthAttr(Attr):
    markerWidth: models.Attr[typedefs.Length] = None


class MaskAttr(Attr):
    mask: models.Attr[
        typedefs.FuncIri | typedefs.None_ | typedefs.Inherit
    ] = None


class MaskContentUnitsAttr(Attr):
    maskContentUnits: models.Attr[
        Literal["userSpaceOnUse", "objectBoundingBox"]
    ] = None


class MaskUnitsAttr(Attr):
    maskUnits: models.Attr[
        Literal["userSpaceOnUse", "objectBoundingBox"]
    ] = None


class MathematicalAttr(Attr):
    mathematical: models.Attr[typedefs.Number] = None


class MaxAttr(Attr):
    max: models.Attr[Literal["media"] | typedefs.ClockValue] = None


class MediaAttr(Attr):
    media: models.Attr[typedefs.MediaDescriptors] = None


class MethodAttr(Attr):
    method: models.Attr[Literal["align", "stretch"]] = None


class MinAttr(Attr):
    min: models.Attr[Literal["media"] | typedefs.ClockValue] = None


class ModeAttr(Attr):
    mode: models.Attr[
        Literal["normal", "multiply", "screen", "darken", "lighten"]
    ] = None


class NameAnythingAttr(Attr):
    name: models.Attr[typedefs.Anything] = None


class NameNameAttr(Attr):
    name: models.Attr[typedefs.Name] = None


class NumOctavesAttr(Attr):
    numOctaves: models.Attr[typedefs.Integer] = None


class OffsetNumberAttr(Attr):
    offset: models.Attr[typedefs.Number] = None


class OffsetNumberPercentageAttr(Attr):
    offset: models.Attr[typedefs.Number | typedefs.Percentage] = None


class OnAbortAttr(Attr):
    onabort: models.Attr[typedefs.Anything] = None


class OnActivateAttr(Attr):
    onactivate: models.Attr[typedefs.Anything] = None


class OnBeginAttr(Attr):
    onbegin: models.Attr[typedefs.Anything] = None


class OnClickAttr(Attr):
    onclick: models.Attr[typedefs.Anything] = None


class OnEndAttr(Attr):
    onend: models.Attr[typedefs.Anything] = None


class OnErrorAttr(Attr):
    onerror: models.Attr[typedefs.Anything] = None


class OnFocusInAttr(Attr):
    onfocusin: models.Attr[typedefs.Anything] = None


class OnFocusOutAttr(Attr):
    onfocusout: models.Attr[typedefs.Anything] = None


class OnLoadAttr(Attr):
    onload: models.Attr[typedefs.Anything] = None


class OnMouseDownAttr(Attr):
    onmousedown: models.Attr[typedefs.Anything] = None


class OnMouseMoveAttr(Attr):
    onmousemove: models.Attr[typedefs.Anything] = None


class OnMouseOutAttr(Attr):
    onmouseout: models.Attr[typedefs.Anything] = None


class OnMouseOverAttr(Attr):
    onmouseover: models.Attr[typedefs.Anything] = None


class OnMouseUpAttr(Attr):
    onmouseup: models.Attr[typedefs.Anything] = None


class OnRepeatAttr(Attr):
    onrepeat: models.Attr[typedefs.Anything] = None


class OnResizeAttr(Attr):
    onresize: models.Attr[typedefs.Anything] = None


class OnScrollAttr(Attr):
    onscroll: models.Attr[typedefs.Anything] = None


class OnUnloadAttr(Attr):
    onunload: models.Attr[typedefs.Anything] = None


class OnZoomAttr(Attr):
    onzoom: models.Attr[typedefs.Anything] = None


class OpacityAttr(Attr):
    opacity: models.Attr[typedefs.OpacityValue | typedefs.Inherit] = None


class OperatorFeCompositeAttr(Attr):
    operator: models.Attr[
        Literal["over", "in", "out", "atop", "xor", "arithmetic"]
    ] = None


class OperatorFeMorphologyAttr(Attr):
    operator: models.Attr[Literal["erode", "dilate"]] = None


class OrderAttr(Attr):
    order: models.Attr[typedefs.NumberOptionalNumber] = None


class OrientAttr(Attr):
    orient: models.Attr[
        typedefs.Auto | Literal["auto-start-reverse"] | typedefs.Angle
    ] = None


class OrientationAttr(Attr):
    orientation: models.Attr[Literal["h", "v"]] = None


class OriginAttr(Attr):
    origin: models.Attr[Literal["default"]] = None


class OverflowAttr(Attr):
    overflow: models.Attr[
        Literal["visible", "hidden", "scroll"]
        | typedefs.Auto
        | typedefs.Inherit
    ] = None


class OverlinePositionAttr(Attr):
    overline_position: models.Attr[typedefs.Number] = None


class OverlineThicknessAttr(Attr):
    overline_thickness: models.Attr[typedefs.Number] = None


class PaintOrderAttr(Attr):
    paint_order: (
        models.Attr[Literal["normal", "fill", "stroke", "markers"]]
        | typedefs.Inherit
    ) = None


class Panose1Attr(Attr):
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


class PathAttr(Attr):
    path: models.Attr[typedefs.PathData] = None


class PathLengthAttr(Attr):
    pathLength: models.Attr[typedefs.Number] = None


class PatternContentUnitsAttr(Attr):
    patternContentUnits: models.Attr[
        Literal["userSpaceOnUse", "objectBoundingBox"]
    ] = None


class PatternTransformAttr(Attr):
    patternTransform: models.Attr[typedefs.TransformList] = None


class PatternUnitsAttr(Attr):
    patternUnits: models.Attr[
        Literal["userSpaceOnUse", "objectBoundingBox"]
    ] = None


class PointerEventsAttr(Attr):
    pointer_events: models.Attr[
        Literal[
            "visiblePainted",
            "visibleFill",
            "visibleStroke",
            "visible",
            "painted",
            "fill",
            "stroke",
        ]
        | typedefs.All
        | typedefs.None_
        | typedefs.Inherit
    ] = None


class PointsAttr(Attr):
    points: models.Attr[typedefs.ListOfPoints] = None


class PointsAtXAttr(Attr):
    pointsAtX: models.Attr[typedefs.Number] = None


class PointsAtYAttr(Attr):
    pointsAtY: models.Attr[typedefs.Number] = None


class PointsAtZAttr(Attr):
    pointsAtZ: models.Attr[typedefs.Number] = None


class PreserveAlphaAttr(Attr):
    preserveAlpha: models.Attr[typedefs.Boolean] = None


class PreserveAspectRatioAttr(Attr):
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


class PrimitiveUnitsAttr(Attr):
    primitiveUnits: models.Attr[
        Literal["userSpaceOnUse", "objectBoundingBox"]
    ] = None


class RAttr(Attr):
    r: models.Attr[typedefs.Length] = None


class RadiusAttr(Attr):
    radius: models.Attr[typedefs.NumberOptionalNumber] = None


class RefXAttr(Attr):
    ref_x: models.Attr[
        Literal["left", "center", "right"] | typedefs.Coordinate
    ] = None


class RefYAttr(Attr):
    ref_y: models.Attr[
        Literal["top", "center", "bottom"] | typedefs.Coordinate
    ] = None


class RenderingIntentAttr(Attr):
    rendering_intent: models.Attr[
        Literal[
            "auto",
            "perceptual",
            "relative-colorimetric",
            "saturation",
            "absolute-colorimetric",
        ]
    ] = None


class RepeatCountAttr(Attr):
    repeatCount: models.Attr[
        Literal["indefinite"] | typedefs.NumericValue
    ] = None


class RepeatDurAttr(Attr):
    repeatDur: models.Attr[Literal["indefinite"] | typedefs.ClockValue] = (
        None
    )


class RequiredExtensionsAttr(Attr):
    requiredExtensions: models.Attr[typedefs.ListOfExtensions] = None


class RequiredFeaturesAttr(Attr):
    requiredFeatures: models.Attr[typedefs.ListOfFeatures] = None


class RestartAttr(Attr):
    restart: models.Attr[Literal["always", "whenNotActive", "never"]] = (
        None
    )


class ResultAttr(Attr):
    result: models.Attr[typedefs.FilterPrimitiveReference] = None


class RotateListOfNumbersAttr(Attr):
    rotate: models.Attr[typedefs.ListOfNumbers] = None


class RotateNumberAutoAutoReverseAttr(Attr):
    rotate: (
        models.Attr[typedefs.Number]
        | typedefs.Auto
        | Literal["auto-reverse"]
    ) = None


class RxAttr(Attr):
    rx: models.Attr[typedefs.Length] = None


class RyAttr(Attr):
    ry: models.Attr[typedefs.Length] = None


class ScaleAttr(Attr):
    scale: models.Attr[typedefs.Number] = None


class SeedAttr(Attr):
    seed: models.Attr[typedefs.Number] = None


class ShapeRenderingAttr(Attr):
    shape_rendering: models.Attr[
        typedefs.Auto
        | Literal["optimizeSpeed", "crispEdges", "geometricPrecision"]
        | typedefs.Inherit
    ] = None


class SlopeAttr(Attr):
    slope: models.Attr[typedefs.Number] = None


class SpacingAttr(Attr):
    spacing: models.Attr[Literal["auto", "exact"]] = None


class SpecularConstantAttr(Attr):
    specularConstant: models.Attr[typedefs.Number] = None


class SpecularExponentAttr(Attr):
    specularExponent: models.Attr[typedefs.Number] = None


class SpreadMethodAttr(Attr):
    spreadMethod: models.Attr[Literal["pad", "reflect", "repeat"]] = None


class StartOffsetAttr(Attr):
    startOffset: models.Attr[typedefs.Length] = None


class StdDeviationAttr(Attr):
    stdDeviation: models.Attr[typedefs.NumberOptionalNumber] = None


class StemhAttr(Attr):
    stemh: models.Attr[typedefs.Number] = None


class StemvAttr(Attr):
    stemv: models.Attr[typedefs.Number] = None


class StitchTilesAttr(Attr):
    stitchTiles: models.Attr[Literal["stitch", "noStitch"]] = None


class StopColorAttr(Attr):
    stop_color: models.Attr[
        Literal["currentColor"]
        | typedefs.Inherit
        | typedefs.IccColor
        | typedefs.Color
    ] = None


class StopOpacityAttr(Attr):
    stop_opacity: models.Attr[typedefs.OpacityValue | typedefs.Inherit] = (
        None
    )


class StrikethroughPositionAttr(Attr):
    strikethrough_position: models.Attr[typedefs.Number] = None


class StrikethroughThicknessAttr(Attr):
    strikethrough_thickness: models.Attr[typedefs.Number] = None


class StringAttr(Attr):
    string: models.Attr[typedefs.Anything] = None


class StrokeAttr(Attr):
    stroke: models.Attr[typedefs.Paint] = None


class StrokeDasharrayAttr(Attr):
    stroke_dasharray: models.Attr[
        typedefs.None_ | typedefs.Dasharray | typedefs.Inherit
    ] = None


class StrokeDashoffsetAttr(Attr):
    stroke_dashoffset: models.Attr[
        typedefs.Percentage | typedefs.Length | typedefs.Inherit
    ] = None


class StrokeLinecapAttr(Attr):
    stroke_linecap: models.Attr[
        Literal["butt", "round", "square"] | typedefs.Inherit
    ] = None


class StrokeLinejoinAttr(Attr):
    stroke_linejoin: models.Attr[
        Literal["miter", "round", "bevel", "miter-clip", "arcs"]
        | typedefs.Inherit
    ] = None


class StrokeMiterlimitAttr(Attr):
    stroke_miterlimit: models.Attr[
        typedefs.Miterlimit | typedefs.Inherit
    ] = None


class StrokeOpacityAttr(Attr):
    stroke_opacity: models.Attr[
        typedefs.OpacityValue | typedefs.Inherit
    ] = None


class StrokeWidthAttr(Attr):
    stroke_width: models.Attr[
        typedefs.Percentage | typedefs.Length | typedefs.Inherit
    ] = None


class StyleAttr(Attr):
    style: models.Attr[typedefs.Unparsed] = None


class SurfaceScaleAttr(Attr):
    surfaceScale: models.Attr[typedefs.Number] = None


class SystemLanguageAttr(Attr):
    systemLanguage: models.Attr[typedefs.LanguageCodes] = None


class TableValuesAttr(Attr):
    tableValues: models.Attr[typedefs.ListOfNumbers] = None


class TargetAttr(Attr):
    target: models.Attr[
        Literal["_replace", "_self", "_parent", "_top", "_blank"]
        | typedefs.XmlName
    ] = None


class TargetXAttr(Attr):
    targetX: models.Attr[typedefs.Integer] = None


class TargetYAttr(Attr):
    targetY: models.Attr[typedefs.Integer] = None


class TextAlignAllAttr(Attr):
    text_align_all: models.Attr[
        Literal[
            "start",
            "end",
            "left",
            "right",
            "center",
            "justify",
            "match-parent",
        ]
        | typedefs.Inherit
    ] = None


class TextAlignAttr(Attr):
    text_align: models.Attr[
        Literal[
            "start",
            "end",
            "left",
            "right",
            "center",
            "justify",
            "match-parent",
            "justify-all",
        ]
        | typedefs.Inherit
    ] = None


class TextAlignLastAttr(Attr):
    text_align_last: models.Attr[
        typedefs.Auto
        | Literal[
            "start",
            "end",
            "left",
            "right",
            "center",
            "justify",
            "match-parent",
        ]
        | typedefs.Inherit
    ] = None


class TextAnchorAttr(Attr):
    text_anchor: models.Attr[
        Literal["start", "middle", "end"] | typedefs.Inherit
    ] = None


class TextDecorationAttr(Attr):
    text_decoration: models.Attr[
        typedefs.None_
        | Literal["underline", "overline", "line-through", "blink"]
        | typedefs.Inherit
    ] = None


class TextIndentAttr(Attr):
    text_indent: models.Attr[
        typedefs.Length
        | typedefs.Percentage
        | Literal["each-line", "hanging"]
        | typedefs.Inherit
    ] = None


class TextLengthAttr(Attr):
    textLength: models.Attr[typedefs.Length] = None


class TextRenderingAttr(Attr):
    text_rendering: models.Attr[
        typedefs.Auto
        | Literal[
            "optimizeSpeed", "optimizeLegibility", "geometricPrecision"
        ]
        | typedefs.Inherit
    ] = None


class TitleAttr(Attr):
    title: models.Attr[typedefs.AdvisoryTitle] = None


class ToAttr(Attr):
    to: models.Attr[typedefs.Unparsed] = None


class TransformAttr(Attr):
    transform: models.Attr[typedefs.TransformList] = None


class TransformOriginAttr(Attr):
    transform_origin: models.Attr[typedefs.TransformOrigin] = None


class TypeAnimateTransformAttr(Attr):
    type: models.Attr[
        Literal["translate", "scale", "rotate", "skewX", "skewY"]
    ] = None


class TypeContentTypeAttr(Attr):
    type: models.Attr[typedefs.ContentType] = None


class TypeFeColorMatrixAttr(Attr):
    type: models.Attr[
        Literal["matrix", "saturate", "hueRotate", "luminanceToAlpha"]
    ] = None


class TypeFeFuncAttr(Attr):
    type: models.Attr[
        Literal["identity", "table", "discrete", "linear", "gamma"]
    ] = None


class TypeFeTurbluenceAttr(Attr):
    type: models.Attr[Literal["fractalNoise", "turbulence"]] = None


class U1Attr(Attr):
    u1: models.Attr[models.List[typedefs.Character | typedefs.Urange]] = (
        None
    )


class U2Attr(Attr):
    u2: models.Attr[models.List[typedefs.Character | typedefs.Urange]] = (
        None
    )


class UnderlinePositionAttr(Attr):
    underline_position: models.Attr[typedefs.Number] = None


class UnderlineThicknessAttr(Attr):
    underline_thickness: models.Attr[typedefs.Number] = None


class UnicodeAttr(Attr):
    unicode: models.Attr[typedefs.Anything] = None


class UnicodeBidiAttr(Attr):
    unicode_bidi: models.Attr[
        Literal["normal", "embed", "bidi-override"] | typedefs.Inherit
    ] = None


class UnicodeRangeAttr(Attr):
    unicode_range: models.Attr[models.List[typedefs.Urange]] = None


class UnitsPerEmAttr(Attr):
    units_per_em: models.Attr[typedefs.Number] = None


class VAlphabeticAttr(Attr):
    v_alphabetic: models.Attr[typedefs.Number] = None


class VHangingAttr(Attr):
    v_hanging: models.Attr[typedefs.Number] = None


class VIdeographicAttr(Attr):
    v_ideographic: models.Attr[typedefs.Number] = None


class VMathematicalAttr(Attr):
    v_mathematical: models.Attr[typedefs.Number] = None


class ValuesListAttr(Attr):
    values: models.Attr[typedefs.Unparsed] = None


class ValuesListOfNumbersAttr(Attr):
    values: models.Attr[typedefs.ListOfNumbers] = None


class VectorEffectAttr(Attr):
    vector_effect: models.Attr[
        Literal[
            "non-scaling-stroke",
            "non-scaling-size",
            "non-rotation",
            "fixed-position",
        ]
        | typedefs.None_
    ] = None


class VersionAttr(Attr):
    version: models.Attr[Literal["1.0", "1.1", "1.2"]] = None


class VertAdvYAttr(Attr):
    vert_adv_y: models.Attr[typedefs.Number] = None


class VertOriginXAttr(Attr):
    vert_origin_x: models.Attr[typedefs.Number] = None


class VertOriginYAttr(Attr):
    vert_origin_y: models.Attr[typedefs.Number] = None


class ViewBoxAttr(Attr):
    viewBox: models.Attr[
        models.Tuple4[
            typedefs.Number,
            typedefs.Number,
            typedefs.Number,
            typedefs.Number,
        ]
    ] = None


class ViewTargetAttr(Attr):
    viewTarget: models.Attr[models.List[typedefs.XmlName]] = None


class VisibilityAttr(Attr):
    visibility: models.Attr[
        Literal["visible", "hidden", "collapse"] | typedefs.Inherit
    ] = None


class WhiteSpaceAttr(Attr):
    white_space: models.Attr[
        Literal[
            "normal",
            "pre",
            "nowrap",
            "pre-wrap",
            "break-spaces",
            "pre-line",
        ]
        | typedefs.Inherit
    ] = None


class WidthAttr(Attr):
    width: models.Attr[typedefs.Length] = None


class WidthsAttr(Attr):
    widths: models.Attr[
        models.List[
            typedefs.Urange
            | models.Tuple2[typedefs.Urange, typedefs.Number]
        ]
    ] = None


class WordSpacingAttr(Attr):
    word_spacing: models.Attr[
        Literal["normal"] | typedefs.Length | typedefs.Inherit
    ] = None


class WritingModeAttr(Attr):
    writing_mode: models.Attr[
        Literal["lr-tb", "rl-tb", "tb-rl", "lr", "rl", "tb"]
        | typedefs.Inherit
    ] = None


class X1Attr(Attr):
    x1: models.Attr[typedefs.Coordinate] = None


class X2Attr(Attr):
    x2: models.Attr[typedefs.Coordinate] = None


class XChannelSelectorAttr(Attr):
    xChannelSelector: models.Attr[Literal["R", "G", "B", "A"]] = None


class XCoordinateAttr(Attr):
    x: models.Attr[typedefs.Coordinate] = None


class XHeightAttr(Attr):
    x_height: models.Attr[typedefs.Number] = None


class XListOfCoordinatesAttr(Attr):
    x: models.Attr[typedefs.ListOfCoordinates] = None


class XNumberAttr(Attr):
    x: models.Attr[typedefs.Number] = None


class XlinkActuateOnLoadAttr(Attr):
    xlink_actuate: models.Attr[Literal["onLoad"]] = None


class XlinkActuateOnRequestAttr(Attr):
    xlink_actuate: models.Attr[Literal["onRequest"]] = None


class XlinkArcroleAttr(Attr):
    xlink_arcrole: models.Attr[typedefs.Iri] = None


class XlinkHrefAttr(Attr):
    xlink_href: models.Attr[typedefs.Iri] = None


class XlinkRoleAttr(Attr):
    xlink_role: models.Attr[typedefs.Iri] = None


class XlinkShowAttr(Attr):
    xlink_show: models.Attr[
        Literal["new", "replace", "embed", "other", "none"]
    ] = None


class XlinkTitleAttr(Attr):
    xlink_title: models.Attr[typedefs.Anything] = None


class XlinkTypeAttr(Attr):
    xlink_type: models.Attr[Literal["simple"]] = None


class XmlBaseAttr(Attr):
    xml_base: models.Attr[typedefs.Iri] = None


class XmlLangAttr(Attr):
    xml_lang: models.Attr[typedefs.LanguageId] = None


class XmlSpaceAttr(Attr):
    xml_space: models.Attr[Literal["default", "preserve"]] = None


class XmlnsAttr(Attr):
    xmlns: models.Attr[utiltypes.Xmlns] = None


class Y1Attr(Attr):
    y1: models.Attr[typedefs.Coordinate] = None


class Y2Attr(Attr):
    y2: models.Attr[typedefs.Coordinate] = None


class YChannelSelectorAttr(Attr):
    yChannelSelector: models.Attr[Literal["R", "G", "B", "A"]] = None


class YCoordinateAttr(Attr):
    y: models.Attr[typedefs.Coordinate] = None


class YListOfCoordinatesAttr(Attr):
    y: models.Attr[typedefs.ListOfCoordinates] = None


class YNumberAttr(Attr):
    y: models.Attr[typedefs.Number] = None


class ZAttr(Attr):
    z: models.Attr[typedefs.Number] = None


class ZoomAndPanAttr(Attr):
    zoomAndPan: models.Attr[Literal["disable", "magnify"]] = None
