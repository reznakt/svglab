"""Definitions of all SVG attributes."""

# ruff: noqa: N815, D101

import pydantic
from typing_extensions import Annotated, Literal, TypeAlias

from svglab.attrs.typedefs import (
    AbsoluteSize,
    AdvisoryTitle,
    All,
    Angle,
    Anything,
    Auto,
    BeginValueList,
    Boolean,
    Character,
    ClockValue,
    Color,
    ContentType,
    Coordinate,
    CursorValue,
    Dasharray,
    EndValueList,
    FamilyName,
    FilterPrimitiveReference,
    FuncIri,
    GenericFamily,
    IccColor,
    ImageRendering,
    Inherit,
    Integer,
    Iri,
    KeySplines,
    LanguageCodes,
    LanguageId,
    LanguageTag,
    Length,
    ListOfCoordinates,
    ListOfExtensions,
    ListOfFeatures,
    ListOfLengths,
    ListOfNames,
    ListOfNumbers,
    ListOfPoints,
    ListOfStrings,
    ListOfValues,
    MediaDescriptors,
    Miterlimit,
    Name,
    None_,
    Number,
    NumberOptionalNumber,
    NumericValue,
    OpacityValue,
    Paint,
    PathData,
    Percentage,
    ProfileName,
    RelativeSize,
    SemicolonListOfNumbers,
    Shape,
    ShapeRendering,
    TextRendering,
    TransformList,
    TransformOrigin,
    Unparsed,
    Urange,
    XmlName,
)
from svglab.models import Attr, BaseModel, List, Tuple
from svglab.utiltypes import Xmlns


class _Attr(BaseModel):
    pass


class AccentHeightAttr(_Attr):
    accent_height: Attr[Number] = None


class AccumulateAttr(_Attr):
    accumulate: Attr[None_ | Literal["sum"]] = None


class AdditiveAttr(_Attr):
    additive: Attr[Literal["replace", "sum"]] = None


class AlignmentBaselineAttr(_Attr):
    alignment_baseline: Attr[
        Auto
        | Inherit
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


class AlphabeticAttr(_Attr):
    alphabetic: Attr[Number] = None


class AmplitudeAttr(_Attr):
    amplitude: Attr[Number] = None


class ArabicFormAttr(_Attr):
    arabic_form: Attr[
        Literal["initial", "medial", "terminal", "isolated"]
    ] = None


class AscentAttr(_Attr):
    ascent: Attr[Number] = None


class AttributeNameAttr(_Attr):
    attributeName: Attr[Unparsed] = None


class AttributeTypeAttr(_Attr):
    attributeType: Attr[Literal["CSS", "XML"] | Auto] = None


class AzimuthAttr(_Attr):
    azimuth: Attr[Number] = None


class BaseFrequencyAttr(_Attr):
    baseFrequency: Attr[NumberOptionalNumber] = None


class BaselineShiftAttr(_Attr):
    baseline_shift: Attr[
        Literal["baseline", "sub", "super"] | Percentage | Length | Inherit
    ] = None


class BaseProfileAttr(_Attr):
    baseProfile: Attr[ProfileName] = None


class BboxAttr(_Attr):
    bbox: Attr[Tuple[Number, Number, Number, Number]] = None


class BeginAttr(_Attr):
    begin: Attr[BeginValueList] = None


class BiasAttr(_Attr):
    bias: Attr[Number] = None


class ByAttr(_Attr):
    by: Attr[Unparsed] = None


class CalcModeAttr(_Attr):
    calcMode: Attr[Literal["discrete", "linear", "paced", "spline"]] = None


class CapHeightAttr(_Attr):
    cap_height: Attr[Number] = None


class ClassAttr(_Attr):
    class_: Attr[ListOfStrings] = None


class ClipAttr(_Attr):
    clip: Attr[Shape | Auto | Inherit] = None


class ClipPathAttr(_Attr):
    clip_path: Attr[FuncIri | None_ | Inherit] = None


class ClipPathUnitsAttr(_Attr):
    clipPathUnits: Attr[Literal["userSpaceOnUse", "objectBoundingBox"]] = (
        None
    )


class ClipRuleAttr(_Attr):
    clip_rule: Attr[Literal["nonzero", "evenodd"] | Inherit] = None


class ColorAttr(_Attr):
    color: Attr[Literal["currentColor"] | Inherit | Color] = None


class ColorInterpolationAttr(_Attr):
    color_interpolation: Attr[
        Auto | Literal["sRGB", "linearRGB"] | Inherit
    ] = None


class ColorInterpolationFiltersAttr(_Attr):
    color_interpolation_filters: Attr[
        Auto | Literal["sRGB", "linearRGB"] | Inherit
    ] = None


class ColorProfileAttr(_Attr):
    color_profile: Attr[Auto | Literal["sRGB"] | Name | Iri | Inherit] = (
        None
    )


class ColorRenderingAttr(_Attr):
    color_rendering: Attr[
        Auto | Literal["optimizeSpeed", "optimizeQuality"] | Inherit
    ] = None


class ContentScriptTypeAttr(_Attr):
    contentScriptType: Attr[ContentType] = None


class ContentStyleTypeAttr(_Attr):
    contentStyleType: Attr[ContentType] = None


class CursorAttr(_Attr):
    cursor: Attr[CursorValue | Inherit | List[CursorValue]] = None


class CxAttr(_Attr):
    cx: Attr[Coordinate] = None


class CyAttr(_Attr):
    cy: Attr[Coordinate] = None


class DAttr(_Attr):
    d: Attr[PathData] = None


class DescentAttr(_Attr):
    descent: Attr[Number] = None


class DiffuseConstantAttr(_Attr):
    diffuseConstant: Attr[Number] = None


class DirectionAttr(_Attr):
    direction: Attr[Literal["ltr", "rtl"] | Inherit] = None


class DisplayAttr(_Attr):
    display: Attr[
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
        | None_
        | Inherit
    ] = None


class DivisorAttr(_Attr):
    divisor: Attr[Number] = None


class DominantBaselineAttr(_Attr):
    dominant_baseline: Attr[
        Auto
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
        | Inherit
    ] = None


class DurAttr(_Attr):
    dur: Attr[ClockValue | Literal["media", "indefinite"]] = None


class DxListOfLengthsAttr(_Attr):
    dx: Attr[ListOfLengths] = None


class DxNumberAttr(_Attr):
    dx: Attr[Number] = None


class DyListOfLengthsAttr(_Attr):
    dy: Attr[ListOfLengths] = None


class DyNumberAttr(_Attr):
    dy: Attr[Number] = None


class EdgeModeAttr(_Attr):
    edgeMode: Attr[Literal["duplicate", "wrap", "none"]] = None


class ElevationAttr(_Attr):
    elevation: Attr[Number] = None


class EnableBackgroundAttr(_Attr):
    enable_background: Attr[
        Literal["accumulate"]
        | Inherit
        | Unparsed  # new [ <x> <y> <width> <height> ]
    ] = None


class EndAttr(_Attr):
    end: Attr[EndValueList] = None


class ExponentAttr(_Attr):
    exponent: Attr[Number] = None


class ExternalResourcesRequiredAttr(_Attr):
    externalResourcesRequired: Attr[Boolean] = None


class FillAttr(_Attr):
    fill: Attr[Paint | Literal["freeze", "remove"]] = None


class FillOpacityAttr(_Attr):
    fill_opacity: Attr[OpacityValue | Inherit] = None


class FillRuleAttr(_Attr):
    fill_rule: Attr[Literal["nonzero", "evenodd"] | Inherit] = None


class FilterAttr(_Attr):
    filter: Attr[FuncIri | None_ | Inherit] = None


class FilterResAttr(_Attr):
    filterRes: Attr[NumberOptionalNumber] = None


class FilterUnitsAttr(_Attr):
    filterUnits: Attr[Literal["userSpaceOnUse", "objectBoundingBox"]] = (
        None
    )


class FloodColorAttr(_Attr):
    flood_color: Attr[
        Literal["currentColor"] | Inherit | Color | IccColor
    ] = None


class FloodOpacityAttr(_Attr):
    flood_opacity: Attr[OpacityValue | Inherit] = None


class FontFamilyAttr(_Attr):
    font_family: Attr[List[FamilyName | GenericFamily] | Inherit] = None


class FontSizeAttr(_Attr):
    font_size: Attr[
        AbsoluteSize
        | RelativeSize
        | Length
        | Percentage
        | Inherit
        | All
        | ListOfLengths
    ] = None


class FontSizeAdjustAttr(_Attr):
    font_size_adjust: Attr[Number | None_ | Inherit] = None


class FontStretchAttr(_Attr):
    font_stretch: Attr[
        All
        | Literal[
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
        | Inherit
    ] = None


class FontStyleAttr(_Attr):
    font_style: Attr[
        All | List[Literal["normal", "italic", "oblique"]] | Inherit
    ] = None


class FontVariantAttr(_Attr):
    font_variant: Attr[Literal["normal", "small-caps"] | Inherit] = None


# a BeforeValidator must be used on non-string literals; pydantic will not
# coerce literal values
_FontWeightInt: TypeAlias = Annotated[
    Literal[100, 200, 300, 400, 500, 600, 700, 800, 900],
    pydantic.BeforeValidator(int),
]


class FontWeightAttr(_Attr):
    font_weight: Attr[
        All
        | Inherit
        | List[
            Literal["normal", "bold", "bolder", "lighter"] | _FontWeightInt
        ]
    ] = None


class FormatAttr(_Attr):
    format: Attr[Unparsed] = None


class FrAttr(_Attr):
    fr: Attr[Length] = None


class FromAttr(_Attr):
    from_: Attr[Unparsed] = None


class FxAttr(_Attr):
    fx: Attr[Coordinate] = None


class FyAttr(_Attr):
    fy: Attr[Coordinate] = None


class G1Attr(_Attr):
    g1: Attr[ListOfNames] = None


class G2Attr(_Attr):
    g2: Attr[ListOfNames] = None


class GlyphNameAttr(_Attr):
    glyph_name: Attr[ListOfNames] = None


class GlyphOrientationHorizontalAttr(_Attr):
    glyph_orientation_horizontal: Attr[Angle | Inherit] = None


class GlyphOrientationVerticalAttr(_Attr):
    glyph_orientation_vertical: Attr[Auto | Angle | Inherit] = None


class GlyphRefAttr(_Attr):
    glyphRef: Attr[Unparsed] = None


class GradientTransformAttr(_Attr):
    gradientTransform: Attr[TransformList] = None


class GradientUnitsAttr(_Attr):
    gradientUnits: Attr[Literal["userSpaceOnUse", "objectBoundingBox"]] = (
        None
    )


class HangingAttr(_Attr):
    hanging: Attr[Number] = None


class HeightAttr(_Attr):
    height: Attr[Length] = None


class HorizAdvXAttr(_Attr):
    horiz_adv_x: Attr[Number] = None


class HorizOriginXAttr(_Attr):
    horiz_origin_x: Attr[Number] = None


class HorizOriginYAttr(_Attr):
    horiz_origin_y: Attr[Number] = None


class HrefAttr(_Attr):
    href: Attr[Iri] = None


class IdAttr(_Attr):
    id: Attr[Name] = None


class IdeographicAttr(_Attr):
    ideographic: Attr[Number] = None


class ImageRenderingAttr(_Attr):
    image_rendering: Attr[Auto | ImageRendering | Inherit] = None


class In2Attr(_Attr):
    in2: Attr[FilterPrimitiveReference] = None


class InAttr(_Attr):
    in_: Attr[FilterPrimitiveReference] = None


class InterceptAttr(_Attr):
    intercept: Attr[Number] = None


class K1Attr(_Attr):
    k1: Attr[Number] = None


class K2Attr(_Attr):
    k2: Attr[Number] = None


class K3Attr(_Attr):
    k3: Attr[Number] = None


class K4Attr(_Attr):
    k4: Attr[Number] = None


class KAttr(_Attr):
    k: Attr[Number] = None


class KernelMatrixAttr(_Attr):
    kernelMatrix: Attr[ListOfNumbers] = None


class KernelUnitLengthAttr(_Attr):
    kernelUnitLength: Attr[NumberOptionalNumber] = None


class KerningAttr(_Attr):
    kerning: Attr[Auto | Length | Inherit] = None


class KeyPointsAttr(_Attr):
    keyPoints: Attr[SemicolonListOfNumbers] = None


class KeySplinesAttr(_Attr):
    keySplines: Attr[KeySplines] = None


class KeyTimesAttr(_Attr):
    keyTimes: Attr[SemicolonListOfNumbers] = None


class LangAttr(_Attr):
    lang: Attr[LanguageTag] = None


class LangGlyphAttr(_Attr):
    lang: Attr[LanguageCodes] = None


class LengthAdjustAttr(_Attr):
    lengthAdjust: Attr[Literal["spacing", "spacingAndGlyphs"]] = None


class LetterSpacingAttr(_Attr):
    letter_spacing: Attr[Literal["normal"] | Length | Inherit] = None


class LightingColorAttr(_Attr):
    lighting_color: Attr[
        Literal["currentColor"] | Color | Inherit | Unparsed
    ] = None


class LimitingConeAngleAttr(_Attr):
    limitingConeAngle: Attr[Number] = None


class LocalAttr(_Attr):
    local: Attr[Unparsed] = None


class MarkerEndAttr(_Attr):
    marker_end: Attr[FuncIri | None_ | Inherit] = None


class MarkerHeightAttr(_Attr):
    markerHeight: Attr[Length] = None


class MarkerMidAttr(_Attr):
    marker_mid: Attr[FuncIri | None_ | Inherit] = None


class MarkerStartAttr(_Attr):
    marker_start: Attr[FuncIri | None_ | Inherit] = None


class MarkerUnitsAttr(_Attr):
    markerUnits: Attr[Literal["strokeWidth", "userSpaceOnUse"]] = None


class MarkerWidthAttr(_Attr):
    markerWidth: Attr[Length] = None


class MaskAttr(_Attr):
    mask: Attr[FuncIri | None_ | Inherit] = None


class MaskContentUnitsAttr(_Attr):
    maskContentUnits: Attr[
        Literal["userSpaceOnUse", "objectBoundingBox"]
    ] = None


class MaskUnitsAttr(_Attr):
    maskUnits: Attr[Literal["userSpaceOnUse", "objectBoundingBox"]] = None


class MathematicalAttr(_Attr):
    mathematical: Attr[Number] = None


class MaxAttr(_Attr):
    max: Attr[Literal["media"] | ClockValue] = None


class MediaAttr(_Attr):
    media: Attr[MediaDescriptors] = None


class MethodAttr(_Attr):
    method: Attr[Literal["align", "stretch"]] = None


class MinAttr(_Attr):
    min: Attr[Literal["media"] | ClockValue] = None


class ModeAttr(_Attr):
    mode: Attr[
        Literal["normal", "multiply", "screen", "darken", "lighten"]
    ] = None


class NameAnythingAttr(_Attr):
    name: Attr[Anything] = None


class NameNameAttr(_Attr):
    name: Attr[Name] = None


class NumOctavesAttr(_Attr):
    numOctaves: Attr[Integer] = None


class OffsetNumberAttr(_Attr):
    offset: Attr[Number] = None


class OffsetNumberPercentageAttr(_Attr):
    offset: Attr[Number | Percentage] = None


class OnAbortAttr(_Attr):
    onabort: Attr[Anything] = None


class OnActivateAttr(_Attr):
    onactivate: Attr[Anything] = None


class OnBeginAttr(_Attr):
    onbegin: Attr[Anything] = None


class OnClickAttr(_Attr):
    onclick: Attr[Anything] = None


class OnEndAttr(_Attr):
    onend: Attr[Anything] = None


class OnErrorAttr(_Attr):
    onerror: Attr[Anything] = None


class OnFocusInAttr(_Attr):
    onfocusin: Attr[Anything] = None


class OnFocusOutAttr(_Attr):
    onfocusout: Attr[Anything] = None


class OnLoadAttr(_Attr):
    onload: Attr[Anything] = None


class OnMouseDownAttr(_Attr):
    onmousedown: Attr[Anything] = None


class OnMouseMoveAttr(_Attr):
    onmousemove: Attr[Anything] = None


class OnMouseOutAttr(_Attr):
    onmouseout: Attr[Anything] = None


class OnMouseOverAttr(_Attr):
    onmouseover: Attr[Anything] = None


class OnMouseUpAttr(_Attr):
    onmouseup: Attr[Anything] = None


class OnRepeatAttr(_Attr):
    onrepeat: Attr[Anything] = None


class OnResizeAttr(_Attr):
    onresize: Attr[Anything] = None


class OnScrollAttr(_Attr):
    onscroll: Attr[Anything] = None


class OnUnloadAttr(_Attr):
    onunload: Attr[Anything] = None


class OnZoomAttr(_Attr):
    onzoom: Attr[Anything] = None


class OpacityAttr(_Attr):
    opacity: Attr[OpacityValue | Inherit] = None


class OperatorFeCompositeAttr(_Attr):
    operator: Attr[
        Literal["over", "in", "out", "atop", "xor", "arithmetic"]
    ] = None


class OperatorFeMorphologyAttr(_Attr):
    operator: Attr[Literal["erode", "dilate"]] = None


class OrderAttr(_Attr):
    order: Attr[NumberOptionalNumber] = None


class OrientAttr(_Attr):
    orient: Attr[Auto | Literal["auto-start-reverse"] | Angle] = None


class OrientationAttr(_Attr):
    orientation: Attr[Literal["h", "v"]] = None


class OriginAttr(_Attr):
    origin: Attr[Literal["default"]] = None


class OverflowAttr(_Attr):
    overflow: Attr[
        Literal["visible", "hidden", "scroll"] | Auto | Inherit
    ] = None


class OverlinePositionAttr(_Attr):
    overline_position: Attr[Number] = None


class OverlineThicknessAttr(_Attr):
    overline_thickness: Attr[Number] = None


class PaintOrderAttr(_Attr):
    paint_order: (
        Attr[Literal["normal", "fill", "stroke", "markers"]] | Inherit
    ) = None


class Panose1Attr(_Attr):
    panose1: Attr[
        Tuple[
            Integer,
            Integer,
            Integer,
            Integer,
            Integer,
            Integer,
            Integer,
            Integer,
            Integer,
            Integer,
        ]
    ] = None


class PathAttr(_Attr):
    path: Attr[PathData] = None


class PathLengthAttr(_Attr):
    pathLength: Attr[Number] = None


class PatternContentUnitsAttr(_Attr):
    patternContentUnits: Attr[
        Literal["userSpaceOnUse", "objectBoundingBox"]
    ] = None


class PatternTransformAttr(_Attr):
    patternTransform: Attr[TransformList] = None


class PatternUnitsAttr(_Attr):
    patternUnits: Attr[Literal["userSpaceOnUse", "objectBoundingBox"]] = (
        None
    )


class PointerEventsAttr(_Attr):
    pointer_events: Attr[
        Literal[
            "visiblePainted",
            "visibleFill",
            "visibleStroke",
            "visible",
            "painted",
            "fill",
            "stroke",
        ]
        | All
        | None_
        | Inherit
    ] = None


class PointsAttr(_Attr):
    points: Attr[ListOfPoints] = None


class PointsAtXAttr(_Attr):
    pointsAtX: Attr[Number] = None


class PointsAtYAttr(_Attr):
    pointsAtY: Attr[Number] = None


class PointsAtZAttr(_Attr):
    pointsAtZ: Attr[Number] = None


class PreserveAlphaAttr(_Attr):
    preserveAlpha: Attr[Boolean] = None


class PreserveAspectRatioAttr(_Attr):
    preserveAspectRatio: Attr[
        Literal[
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
        | Unparsed
    ] = None


class PrimitiveUnitsAttr(_Attr):
    primitiveUnits: Attr[
        Literal["userSpaceOnUse", "objectBoundingBox"]
    ] = None


class RAttr(_Attr):
    r: Attr[Length] = None


class RadiusAttr(_Attr):
    radius: Attr[NumberOptionalNumber] = None


class RefXAttr(_Attr):
    refX: Attr[Literal["left", "center", "right"] | Coordinate] = None


class RefYAttr(_Attr):
    refY: Attr[Literal["top", "center", "bottom"] | Coordinate] = None


class RenderingIntentAttr(_Attr):
    rendering_intent: Attr[
        Literal[
            "auto",
            "perceptual",
            "relative-colorimetric",
            "saturation",
            "absolute-colorimetric",
        ]
    ] = None


class RepeatCountAttr(_Attr):
    repeatCount: Attr[Literal["indefinite"] | NumericValue] = None


class RepeatDurAttr(_Attr):
    repeatDur: Attr[Literal["indefinite"] | ClockValue] = None


class RequiredExtensionsAttr(_Attr):
    requiredExtensions: Attr[ListOfExtensions] = None


class RequiredFeaturesAttr(_Attr):
    requiredFeatures: Attr[ListOfFeatures] = None


class RestartAttr(_Attr):
    restart: Attr[Literal["always", "whenNotActive", "never"]] = None


class ResultAttr(_Attr):
    result: Attr[FilterPrimitiveReference] = None


class RotateListOfNumbersAttr(_Attr):
    rotate: Attr[ListOfNumbers] = None


class RotateNumberAutoAutoReverseAttr(_Attr):
    rotate: Attr[Number] | Auto | Literal["auto-reverse"] = None


class RxAttr(_Attr):
    rx: Attr[Length] = None


class RyAttr(_Attr):
    ry: Attr[Length] = None


class ScaleAttr(_Attr):
    scale: Attr[Number] = None


class SeedAttr(_Attr):
    seed: Attr[Number] = None


class ShapeRenderingAttr(_Attr):
    shape_rendering: Attr[Auto | ShapeRendering | Inherit] = None


class SlopeAttr(_Attr):
    slope: Attr[Number] = None


class SpacingAttr(_Attr):
    spacing: Attr[Literal["auto", "exact"]] = None


class SpecularConstantAttr(_Attr):
    specularConstant: Attr[Number] = None


class SpecularExponentAttr(_Attr):
    specularExponent: Attr[Number] = None


class SpreadMethodAttr(_Attr):
    spreadMethod: Attr[Literal["pad", "reflect", "repeat"]] = None


class StartOffsetAttr(_Attr):
    startOffset: Attr[Length] = None


class StdDeviationAttr(_Attr):
    stdDeviation: Attr[NumberOptionalNumber] = None


class StemhAttr(_Attr):
    stemh: Attr[Number] = None


class StemvAttr(_Attr):
    stemv: Attr[Number] = None


class StitchTilesAttr(_Attr):
    stitchTiles: Attr[Literal["stitch", "noStitch"]] = None


class StopColorAttr(_Attr):
    stop_color: Attr[
        Literal["currentColor"] | Inherit | Color | IccColor
    ] = None


class StopOpacityAttr(_Attr):
    stop_opacity: Attr[OpacityValue | Inherit] = None


class StrikethroughPositionAttr(_Attr):
    strikethrough_position: Attr[Number] = None


class StrikethroughThicknessAttr(_Attr):
    strikethrough_thickness: Attr[Number] = None


class StringAttr(_Attr):
    string: Attr[Anything] = None


class StrokeAttr(_Attr):
    stroke: Attr[Paint] = None


class StrokeDasharrayAttr(_Attr):
    stroke_dasharray: Attr[None_ | Dasharray | Inherit] = None


class StrokeDashoffsetAttr(_Attr):
    stroke_dashoffset: Attr[Percentage | Length | Inherit] = None


class StrokeLinecapAttr(_Attr):
    stroke_linecap: Attr[Literal["butt", "round", "square"] | Inherit] = (
        None
    )


class StrokeLinejoinAttr(_Attr):
    stroke_linejoin: Attr[
        Literal["miter", "round", "bevel", "miter-clip", "arcs"] | Inherit
    ] = None


class StrokeMiterlimitAttr(_Attr):
    stroke_miterlimit: Attr[Miterlimit | Inherit] = None


class StrokeOpacityAttr(_Attr):
    stroke_opacity: Attr[OpacityValue | Inherit] = None


class StrokeWidthAttr(_Attr):
    stroke_width: Attr[Percentage | Length | Inherit] = None


class StyleAttr(_Attr):
    style: Attr[Unparsed] = None


class SurfaceScaleAttr(_Attr):
    surfaceScale: Attr[Number] = None


class SystemLanguageAttr(_Attr):
    systemLanguage: Attr[LanguageCodes] = None


class TableValuesAttr(_Attr):
    tableValues: Attr[ListOfNumbers] = None


class TargetAttr(_Attr):
    target: Attr[
        Literal["_replace", "_self", "_parent", "_top", "_blank"] | XmlName
    ] = None


class TargetXAttr(_Attr):
    targetX: Attr[Integer] = None


class TargetYAttr(_Attr):
    targetY: Attr[Integer] = None


class TextAlignAllAttr(_Attr):
    text_align_all: Attr[
        Literal[
            "start",
            "end",
            "left",
            "right",
            "center",
            "justify",
            "match-parent",
        ]
        | Inherit
    ] = None


class TextAlignAttr(_Attr):
    text_align: Attr[
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
        | Inherit
    ] = None


class TextAlignLastAttr(_Attr):
    text_align_last: Attr[
        Auto
        | Literal[
            "start",
            "end",
            "left",
            "right",
            "center",
            "justify",
            "match-parent",
        ]
        | Inherit
    ] = None


class TextAnchorAttr(_Attr):
    text_anchor: Attr[Literal["start", "middle", "end"] | Inherit] = None


class TextDecorationAttr(_Attr):
    text_decoration: Attr[
        None_
        | List[Literal["underline", "overline", "line-through", "blink"]]
        | Inherit
    ] = None


class TextIndentAttr(_Attr):
    text_indent: Attr[
        Length | Percentage | Literal["each-line", "hanging"] | Inherit
    ] = None


class TextLengthAttr(_Attr):
    textLength: Attr[Length] = None


class TextRenderingAttr(_Attr):
    text_rendering: Attr[Auto | TextRendering | Inherit] = None


class TitleAttr(_Attr):
    title: Attr[AdvisoryTitle] = None


class ToAttr(_Attr):
    to: Attr[Unparsed] = None


class TransformAttr(_Attr):
    transform: Attr[TransformList] = None


class TransformOriginAttr(_Attr):
    transform_origin: Attr[TransformOrigin] = None


class TypeAnimateTransformAttr(_Attr):
    type: Attr[
        Literal["translate", "scale", "rotate", "skewX", "skewY"]
    ] = None


class TypeContentTypeAttr(_Attr):
    type: Attr[ContentType] = None


class TypeFeColorMatrixAttr(_Attr):
    type: Attr[
        Literal["matrix", "saturate", "hueRotate", "luminanceToAlpha"]
    ] = None


class TypeFeFuncAttr(_Attr):
    type: Attr[
        Literal["identity", "table", "discrete", "linear", "gamma"]
    ] = None


class TypeFeTurbluenceAttr(_Attr):
    type: Attr[Literal["fractalNoise", "turbulence"]] = None


class U1Attr(_Attr):
    u1: Attr[List[Character | Urange]] = None


class U2Attr(_Attr):
    u2: Attr[List[Character | Urange]] = None


class UnderlinePositionAttr(_Attr):
    underline_position: Attr[Number] = None


class UnderlineThicknessAttr(_Attr):
    underline_thickness: Attr[Number] = None


class UnicodeAttr(_Attr):
    unicode: Attr[Anything] = None


class UnicodeBidiAttr(_Attr):
    unicode_bidi: Attr[
        Literal["normal", "embed", "bidi-override"] | Inherit
    ] = None


class UnicodeRangeAttr(_Attr):
    unicode_range: Attr[List[Urange]] = None


class UnitsPerEmAttr(_Attr):
    units_per_em: Attr[Number] = None


class VAlphabeticAttr(_Attr):
    v_alphabetic: Attr[Number] = None


class VHangingAttr(_Attr):
    v_hanging: Attr[Number] = None


class VIdeographicAttr(_Attr):
    v_ideographic: Attr[Number] = None


class VMathematicalAttr(_Attr):
    v_mathematical: Attr[Number] = None


class ValuesListAttr(_Attr):
    values: Attr[ListOfValues] = None


class ValuesListOfNumbersAttr(_Attr):
    values: Attr[ListOfNumbers] = None


class VectorEffectAttr(_Attr):
    vector_effect: Attr[
        Literal[
            "non-scaling-stroke",
            "non-scaling-size",
            "non-rotation",
            "fixed-position",
        ]
        | None_
    ] = None


class VersionAttr(_Attr):
    version: Attr[Literal["1.0", "1.1", "1.2"]] = None


class VertAdvYAttr(_Attr):
    vert_adv_y: Attr[Number] = None


class VertOriginXAttr(_Attr):
    vert_origin_x: Attr[Number] = None


class VertOriginYAttr(_Attr):
    vert_origin_y: Attr[Number] = None


class ViewBoxAttr(_Attr):
    viewBox: Attr[Tuple[Number, Number, Number, Number]] = None


class ViewTargetAttr(_Attr):
    viewTarget: Attr[List[XmlName]] = None


class VisibilityAttr(_Attr):
    visibility: Attr[
        Literal["visible", "hidden", "collapse"] | Inherit
    ] = None


class WhiteSpaceAttr(_Attr):
    white_space: Attr[
        Literal[
            "normal",
            "pre",
            "nowrap",
            "pre-wrap",
            "break-spaces",
            "pre-line",
        ]
        | Inherit
    ] = None


class WidthAttr(_Attr):
    width: Attr[Length] = None


class WidthsAttr(_Attr):
    widths: Attr[List[Urange | Tuple[Urange, Number]]] = None


class WordSpacingAttr(_Attr):
    word_spacing: Attr[Literal["normal"] | Length | Inherit] = None


class WritingModeAttr(_Attr):
    writing_mode: Attr[
        Literal["lr-tb", "rl-tb", "tb-rl", "lr", "rl", "tb"] | Inherit
    ] = None


class X1Attr(_Attr):
    x1: Attr[Coordinate] = None


class X2Attr(_Attr):
    x2: Attr[Coordinate] = None


class XChannelSelectorAttr(_Attr):
    xChannelSelector: Attr[Literal["R", "G", "B", "A"]] = None


class XCoordinateAttr(_Attr):
    x: Attr[Coordinate] = None


class XHeightAttr(_Attr):
    x_height: Attr[Number] = None


class XListOfCoordinatesAttr(_Attr):
    x: Attr[ListOfCoordinates] = None


class XNumberAttr(_Attr):
    x: Attr[Number] = None


class XlinkActuateOnLoadAttr(_Attr):
    xlink_actuate: Attr[Literal["onLoad"]] = None


class XlinkActuateOnRequestAttr(_Attr):
    xlink_actuate: Attr[Literal["onRequest"]] = None


class XlinkArcroleAttr(_Attr):
    xlink_arcrole: Attr[Iri] = None


class XlinkHrefAttr(_Attr):
    xlink_href: Attr[Iri] = None


class XlinkRoleAttr(_Attr):
    xlink_role: Attr[Iri] = None


class XlinkShowAttr(_Attr):
    xlink_show: Attr[
        Literal["new", "replace", "embed", "other", "none"]
    ] = None


class XlinkTitleAttr(_Attr):
    xlink_title: Attr[Anything] = None


class XlinkTypeAttr(_Attr):
    xlink_type: Attr[Literal["simple"]] = None


class XmlBaseAttr(_Attr):
    xml_base: Attr[Iri] = None


class XmlLangAttr(_Attr):
    xml_lang: Attr[LanguageId] = None


class XmlSpaceAttr(_Attr):
    xml_space: Attr[Literal["default", "preserve"]] = None


class XmlnsAttr(_Attr):
    xmlns: Attr[Xmlns] = None


class Y1Attr(_Attr):
    y1: Attr[Coordinate] = None


class Y2Attr(_Attr):
    y2: Attr[Coordinate] = None


class YChannelSelectorAttr(_Attr):
    yChannelSelector: Attr[Literal["R", "G", "B", "A"]] = None


class YCoordinateAttr(_Attr):
    y: Attr[Coordinate] = None


class YListOfCoordinatesAttr(_Attr):
    y: Attr[ListOfCoordinates] = None


class YNumberAttr(_Attr):
    y: Attr[Number] = None


class ZAttr(_Attr):
    z: Attr[Number] = None


class ZoomAndPanAttr(_Attr):
    zoomAndPan: Attr[Literal["disable", "magnify"]] = None
