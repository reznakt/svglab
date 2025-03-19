# ruff: noqa: N815

from typing_extensions import Literal

from svglab import models, utiltypes
from svglab.attrs import common, typedefs


class AccentHeight(common.Attr):
    accent_height: models.Attr[typedefs.Number] = None


class Accumulate(common.Attr):
    accumulate: models.Attr[typedefs.None_ | Literal["sum"]] = None


class Additive(common.Attr):
    additive: models.Attr[Literal["replace", "sum"]] = None


class Alphabetic(common.Attr):
    alphabetic: models.Attr[typedefs.Number] = None


class Amplitude(common.Attr):
    amplitude: models.Attr[typedefs.Number] = None


class ArabicForm(common.Attr):
    arabic_form: models.Attr[
        Literal["initial", "medial", "terminal", "isolated"]
    ] = None


class Ascent(common.Attr):
    ascent: models.Attr[typedefs.Number] = None


class AttributeName(common.Attr):
    attributeName: models.Attr[typedefs.Unparsed] = None


class AttributeType(common.Attr):
    attributeType: models.Attr[Literal["CSS", "XML"] | typedefs.Auto] = (
        None
    )


class Azimuth(common.Attr):
    azimuth: models.Attr[typedefs.Number] = None


class BaseFrequency(common.Attr):
    baseFrequency: models.Attr[typedefs.NumberOptionalNumber] = None


class BaseProfile(common.Attr):
    baseProfile: models.Attr[typedefs.ProfileName] = None


class Bbox(common.Attr):
    bbox: models.Attr[
        models.Tuple4[
            typedefs.Number,
            typedefs.Number,
            typedefs.Number,
            typedefs.Number,
        ]
    ] = None


class Begin(common.Attr):
    begin: models.Attr[typedefs.BeginValueList] = None


class Bias(common.Attr):
    bias: models.Attr[typedefs.Number] = None


class By(common.Attr):
    by: models.Attr[typedefs.Unparsed] = None


class CalcMode(common.Attr):
    calcMode: models.Attr[
        Literal["discrete", "linear", "paced", "spline"]
    ] = None


class CapHeight(common.Attr):
    cap_height: models.Attr[typedefs.Number] = None


class Class(common.Attr):
    class_: models.Attr[typedefs.ListOfStrings] = None


class ClipPathUnits(common.Attr):
    clipPathUnits: models.Attr[
        Literal["userSpaceOnUse", "objectBoundingBox"]
    ] = None


class ContentScriptType(common.Attr):
    contentScriptType: models.Attr[typedefs.ContentType] = None


class ContentStyleType(common.Attr):
    contentStyleType: models.Attr[typedefs.ContentType] = None


class Cx(common.Attr):
    cx: models.Attr[typedefs.Coordinate] = None


class Cy(common.Attr):
    cy: models.Attr[typedefs.Coordinate] = None


class D(common.Attr):
    d: models.Attr[typedefs.PathData] = None


class Descent(common.Attr):
    descent: models.Attr[typedefs.Number] = None


class DiffuseConstant(common.Attr):
    diffuseConstant: models.Attr[typedefs.Number] = None


class Divisor(common.Attr):
    divisor: models.Attr[typedefs.Number] = None


class Dur(common.Attr):
    dur: models.Attr[
        typedefs.ClockValue | Literal["media", "indefinite"]
    ] = None


class DxListOfLengths(common.Attr):
    dx: models.Attr[typedefs.ListOfLengths] = None


class DxNumber(common.Attr):
    dx: models.Attr[typedefs.Number] = None


class DyListOfLengths(common.Attr):
    dy: models.Attr[typedefs.ListOfLengths] = None


class DyNumber(common.Attr):
    dy: models.Attr[typedefs.Number] = None


class EdgeMode(common.Attr):
    edgeMode: models.Attr[Literal["duplicate", "wrap", "none"]] = None


class Elevation(common.Attr):
    elevation: models.Attr[typedefs.Number] = None


class End(common.Attr):
    end: models.Attr[typedefs.EndValueList] = None


class Exponent(common.Attr):
    exponent: models.Attr[typedefs.Number] = None


class ExternalResourcesRequired(common.Attr):
    externalResourcesRequired: models.Attr[typedefs.Boolean] = None


class FilterRes(common.Attr):
    filterRes: models.Attr[typedefs.NumberOptionalNumber] = None


class FilterUnits(common.Attr):
    filterUnits: models.Attr[
        Literal["userSpaceOnUse", "objectBoundingBox"]
    ] = None


class FontFamily(common.Attr):
    font_family: models.Attr[
        models.List[typedefs.FamilyName | typedefs.GenericFamily]
    ] = None


class Format(common.Attr):
    format: models.Attr[typedefs.Unparsed] = None


class Fr(common.Attr):
    fr: models.Attr[typedefs.Length] = None


class From(common.Attr):
    from_: models.Attr[typedefs.Unparsed] = None


class Fx(common.Attr):
    fx: models.Attr[typedefs.Coordinate] = None


class Fy(common.Attr):
    fy: models.Attr[typedefs.Coordinate] = None


class G1(common.Attr):
    g1: models.Attr[typedefs.ListOfNames] = None


class G2(common.Attr):
    g2: models.Attr[typedefs.ListOfNames] = None


class GlyphName(common.Attr):
    glyph_name: models.Attr[typedefs.ListOfNames] = None


class GlyphRef(common.Attr):
    glyphRef: models.Attr[typedefs.Unparsed] = None


class GradientTransform(common.Attr):
    gradientTransform: models.Attr[typedefs.TransformList] = None


class GradientUnits(common.Attr):
    gradientUnits: models.Attr[
        Literal["userSpaceOnUse", "objectBoundingBox"]
    ] = None


class Hanging(common.Attr):
    hanging: models.Attr[typedefs.Number] = None


class Height(common.Attr):
    height: models.Attr[typedefs.Length] = None


class HorizAdvX(common.Attr):
    horiz_adv_x: models.Attr[typedefs.Number] = None


class HorizOriginX(common.Attr):
    horiz_origin_x: models.Attr[typedefs.Number] = None


class HorizOriginY(common.Attr):
    horiz_origin_y: models.Attr[typedefs.Number] = None


class Href(common.Attr):
    href: models.Attr[typedefs.Url] = None


class Id(common.Attr):
    id: models.Attr[typedefs.Name] = None


class Ideographic(common.Attr):
    ideographic: models.Attr[typedefs.Number] = None


class In(common.Attr):
    in_: models.Attr[
        typedefs.Paint
        | typedefs.FilterPrimitiveReference
        | typedefs.Unparsed
    ] = None


class In2(common.Attr):
    in2: models.Attr[
        typedefs.Paint
        | typedefs.FilterPrimitiveReference
        | typedefs.Unparsed
    ] = None


class Intercept(common.Attr):
    intercept: models.Attr[typedefs.Number] = None


class K(common.Attr):
    k: models.Attr[typedefs.Number] = None


class K1(common.Attr):
    k1: models.Attr[typedefs.Number] = None


class K2(common.Attr):
    k2: models.Attr[typedefs.Number] = None


class K3(common.Attr):
    k3: models.Attr[typedefs.Number] = None


class K4(common.Attr):
    k4: models.Attr[typedefs.Number] = None


class KernelMatrix(common.Attr):
    kernelMatrix: models.Attr[typedefs.ListOfNumbers] = None


class KernelUnitLength(common.Attr):
    kernelUnitLength: models.Attr[typedefs.NumberOptionalNumber] = None


class KeyPoints(common.Attr):
    keyPoints: models.Attr[typedefs.ListOfNumbers] = None


class KeySplines(common.Attr):
    keySplines: models.Attr[typedefs.Unparsed] = None


class KeyTimes(common.Attr):
    keyTimes: models.Attr[typedefs.Unparsed] = None


class Lang(common.Attr):
    lang: models.Attr[typedefs.LanguageTag] = None


class LangGlyph(common.Attr):
    lang: models.Attr[typedefs.LanguageCodes] = None


class LengthAdjust(common.Attr):
    lengthAdjust: models.Attr[Literal["spacing", "spacingAndGlyphs"]] = (
        None
    )


class LimitingConeAngle(common.Attr):
    limitingConeAngle: models.Attr[typedefs.Number] = None


class Local(common.Attr):
    local: models.Attr[typedefs.Unparsed] = None


class MarkerHeight(common.Attr):
    markerHeight: models.Attr[typedefs.Length] = None


class MarkerUnits(common.Attr):
    markerUnits: models.Attr[Literal["strokeWidth", "userSpaceOnUse"]] = (
        None
    )


class MarkerWidth(common.Attr):
    markerWidth: models.Attr[typedefs.Length] = None


class MaskContentUnits(common.Attr):
    maskContentUnits: models.Attr[
        Literal["userSpaceOnUse", "objectBoundingBox"]
    ] = None


class MaskUnits(common.Attr):
    maskUnits: models.Attr[
        Literal["userSpaceOnUse", "objectBoundingBox"]
    ] = None


class Mathematical(common.Attr):
    mathematical: models.Attr[typedefs.Number] = None


class Max(common.Attr):
    max: models.Attr[Literal["media"] | typedefs.ClockValue] = None


class Media(common.Attr):
    media: models.Attr[typedefs.MediaDescriptors] = None


class Method(common.Attr):
    method: models.Attr[Literal["align", "stretch"]] = None


class Min(common.Attr):
    min: models.Attr[Literal["media"] | typedefs.ClockValue] = None


class Mode(common.Attr):
    mode: models.Attr[
        Literal["normal", "multiply", "screen", "darken", "lighten"]
    ] = None


class NameName(common.Attr):
    name: models.Attr[typedefs.Name] = None


class NameAnything(common.Attr):
    name: models.Attr[typedefs.Anything] = None


class NumOctaves(common.Attr):
    numOctaves: models.Attr[typedefs.Integer] = None


class OffsetNumberPercentage(common.Attr):
    offset: models.Attr[typedefs.Number | typedefs.Percentage] = None


class OffsetNumber(common.Attr):
    offset: models.Attr[typedefs.Number] = None


class OnAbort(common.Attr):
    onabort: models.Attr[typedefs.Anything] = None


class OnActivate(common.Attr):
    onactivate: models.Attr[typedefs.Anything] = None


class OnBegin(common.Attr):
    onbegin: models.Attr[typedefs.Anything] = None


class OnClick(common.Attr):
    onclick: models.Attr[typedefs.Anything] = None


class OnEnd(common.Attr):
    onend: models.Attr[typedefs.Anything] = None


class OnError(common.Attr):
    onerror: models.Attr[typedefs.Anything] = None


class OnFocusIn(common.Attr):
    onfocusin: models.Attr[typedefs.Anything] = None


class OnFocusOut(common.Attr):
    onfocusout: models.Attr[typedefs.Anything] = None


class OnLoad(common.Attr):
    onload: models.Attr[typedefs.Anything] = None


class OnMouseDown(common.Attr):
    onmousedown: models.Attr[typedefs.Anything] = None


class OnMouseMove(common.Attr):
    onmousemove: models.Attr[typedefs.Anything] = None


class OnMouseOut(common.Attr):
    onmouseout: models.Attr[typedefs.Anything] = None


class OnMouseOver(common.Attr):
    onmouseover: models.Attr[typedefs.Anything] = None


class OnMouseUp(common.Attr):
    onmouseup: models.Attr[typedefs.Anything] = None


class OnRepeat(common.Attr):
    onrepeat: models.Attr[typedefs.Anything] = None


class OnResize(common.Attr):
    onresize: models.Attr[typedefs.Anything] = None


class OnScroll(common.Attr):
    onscroll: models.Attr[typedefs.Anything] = None


class OnUnload(common.Attr):
    onunload: models.Attr[typedefs.Anything] = None


class OnZoom(common.Attr):
    onzoom: models.Attr[typedefs.Anything] = None


class OperatorFeComposite(common.Attr):
    operator: models.Attr[
        Literal["over", "in", "out", "atop", "xor", "arithmetic"]
    ] = None


class OperatorFeMorphology(common.Attr):
    operator: models.Attr[Literal["erode", "dilate"]] = None


class Order(common.Attr):
    order: models.Attr[typedefs.NumberOptionalNumber] = None


class Orient(common.Attr):
    orient: models.Attr[
        typedefs.Auto | Literal["auto-start-reverse"] | typedefs.Angle
    ] = None


class Orientation(common.Attr):
    orientation: models.Attr[Literal["h", "v"]] = None


class Origin(common.Attr):
    origin: models.Attr[Literal["default"]] = None


class OverlinePosition(common.Attr):
    overline_position: models.Attr[typedefs.Number] = None


class OverlineThickness(common.Attr):
    overline_thickness: models.Attr[typedefs.Number] = None


class Panose1(common.Attr):
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


class Path(common.Attr):
    path: models.Attr[typedefs.PathData] = None


class PathLength(common.Attr):
    pathLength: models.Attr[typedefs.Number] = None


class PatternContentUnits(common.Attr):
    patternContentUnits: models.Attr[
        Literal["userSpaceOnUse", "objectBoundingBox"]
    ] = None


class PatternTransform(common.Attr):
    patternTransform: models.Attr[typedefs.TransformList] = None


class PatternUnits(common.Attr):
    patternUnits: models.Attr[
        Literal["userSpaceOnUse", "objectBoundingBox"]
    ] = None


class Points(common.Attr):
    points: models.Attr[typedefs.ListOfPoints] = None


class PointsAtX(common.Attr):
    pointsAtX: models.Attr[typedefs.Number] = None


class PointsAtY(common.Attr):
    pointsAtY: models.Attr[typedefs.Number] = None


class PointsAtZ(common.Attr):
    pointsAtZ: models.Attr[typedefs.Number] = None


class PreserveAlpha(common.Attr):
    preserveAlpha: models.Attr[typedefs.Boolean] = None


class PreserveAspectRatio(common.Attr):
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


class PrimitiveUnits(common.Attr):
    primitiveUnits: models.Attr[
        Literal["userSpaceOnUse", "objectBoundingBox"]
    ] = None


class R(common.Attr):
    r: models.Attr[typedefs.Length] = None


class Radius(common.Attr):
    radius: models.Attr[typedefs.NumberOptionalNumber] = None


class RefX(common.Attr):
    ref_x: models.Attr[
        Literal["left", "center", "right"] | typedefs.Coordinate
    ] = None


class RefY(common.Attr):
    ref_y: models.Attr[
        Literal["top", "center", "bottom"] | typedefs.Coordinate
    ] = None


class RenderingIntent(common.Attr):
    rendering_intent: models.Attr[
        Literal[
            "auto",
            "perceptual",
            "relative-colorimetric",
            "saturation",
            "absolute-colorimetric",
        ]
    ] = None


class RepeatCount(common.Attr):
    repeatCount: models.Attr[
        Literal["indefinite"] | typedefs.NumericValue
    ] = None


class RepeatDur(common.Attr):
    repeatDur: models.Attr[Literal["indefinite"] | typedefs.ClockValue] = (
        None
    )


class RequiredExtensions(common.Attr):
    requiredExtensions: models.Attr[typedefs.ListOfExtensions] = None


class RequiredFeatures(common.Attr):
    requiredFeatures: models.Attr[typedefs.ListOfFeatures] = None


class Restart(common.Attr):
    restart: models.Attr[Literal["always", "whenNotActive", "never"]] = (
        None
    )


class Result(common.Attr):
    result: models.Attr[typedefs.FilterPrimitiveReference] = None


class RotateListOfNumbers(common.Attr):
    rotate: models.Attr[typedefs.ListOfNumbers] = None


class RotateNumberAutoAutoReverse(common.Attr):
    rotate: (
        models.Attr[typedefs.Number]
        | typedefs.Auto
        | Literal["auto-reverse"]
    ) = None


class Rx(common.Attr):
    rx: models.Attr[typedefs.Length] = None


class Ry(common.Attr):
    ry: models.Attr[typedefs.Length] = None


class Scale(common.Attr):
    scale: models.Attr[typedefs.Number] = None


class Seed(common.Attr):
    seed: models.Attr[typedefs.Number] = None


class Slope(common.Attr):
    slope: models.Attr[typedefs.Number] = None


class Spacing(common.Attr):
    spacing: models.Attr[Literal["auto", "exact"]] = None


class SpecularConstant(common.Attr):
    specularConstant: models.Attr[typedefs.Number] = None


class SpecularExponent(common.Attr):
    specularExponent: models.Attr[typedefs.Number] = None


class SpreadMethod(common.Attr):
    spreadMethod: models.Attr[Literal["pad", "reflect", "repeat"]] = None


class StartOffset(common.Attr):
    startOffset: models.Attr[typedefs.Length] = None


class StdDeviation(common.Attr):
    stdDeviation: models.Attr[typedefs.NumberOptionalNumber] = None


class Stemh(common.Attr):
    stemh: models.Attr[typedefs.Number] = None


class Stemv(common.Attr):
    stemv: models.Attr[typedefs.Number] = None


class StitchTiles(common.Attr):
    stitchTiles: models.Attr[Literal["stitch", "noStitch"]] = None


class StrikethroughPosition(common.Attr):
    strikethrough_position: models.Attr[typedefs.Number] = None


class StrikethroughThickness(common.Attr):
    strikethrough_thickness: models.Attr[typedefs.Number] = None


class String(common.Attr):
    string: models.Attr[typedefs.Anything] = None


class Style(common.Attr):
    style: models.Attr[typedefs.Unparsed] = None


class SurfaceScale(common.Attr):
    surfaceScale: models.Attr[typedefs.Number] = None


class SystemLanguage(common.Attr):
    systemLanguage: models.Attr[typedefs.LanguageCodes] = None


class TableValues(common.Attr):
    tableValues: models.Attr[typedefs.ListOfNumbers] = None


class Target(common.Attr):
    target: models.Attr[
        Literal["_replace", "_self", "_parent", "_top", "_blank"]
        | typedefs.XmlName
    ] = None


class TargetX(common.Attr):
    targetX: models.Attr[typedefs.Integer] = None


class TargetY(common.Attr):
    targetY: models.Attr[typedefs.Integer] = None


class TextLength(common.Attr):
    textLength: models.Attr[typedefs.Length] = None


class Title(common.Attr):
    title: models.Attr[typedefs.AdvisoryTitle] = None


class To(common.Attr):
    to: models.Attr[typedefs.Unparsed] = None


class TypeAnimateTransform(common.Attr):
    type: models.Attr[
        Literal["translate", "scale", "rotate", "skewX", "skewY"]
    ] = None


class TypeFeColorMatrix(common.Attr):
    type: models.Attr[
        Literal["matrix", "saturate", "hueRotate", "luminanceToAlpha"]
    ] = None


class TypeFeTurbluence(common.Attr):
    type: models.Attr[Literal["fractalNoise", "turbulence"]] = None


class TypeContentType(common.Attr):
    type: models.Attr[typedefs.ContentType] = None


class TypeFeFunc(common.Attr):
    type: models.Attr[
        Literal["identity", "table", "discrete", "linear", "gamma"]
    ] = None


class U1(common.Attr):
    u1: models.Attr[models.List[typedefs.Character | typedefs.Urange]] = (
        None
    )


class U2(common.Attr):
    u2: models.Attr[models.List[typedefs.Character | typedefs.Urange]] = (
        None
    )


class UnderlinePosition(common.Attr):
    underline_position: models.Attr[typedefs.Number] = None


class UnderlineThickness(common.Attr):
    underline_thickness: models.Attr[typedefs.Number] = None


class Unicode(common.Attr):
    unicode: models.Attr[typedefs.Anything] = None


class UnicodeRange(common.Attr):
    unicode_range: models.Attr[models.List[typedefs.Urange]] = None


class UnitsPerEm(common.Attr):
    units_per_em: models.Attr[typedefs.Number] = None


class VAlphabetic(common.Attr):
    v_alphabetic: models.Attr[typedefs.Number] = None


class VHanging(common.Attr):
    v_hanging: models.Attr[typedefs.Number] = None


class VIdeographic(common.Attr):
    v_ideographic: models.Attr[typedefs.Number] = None


class VMathematical(common.Attr):
    v_mathematical: models.Attr[typedefs.Number] = None


class ValuesListOfNumbers(common.Attr):
    values: models.Attr[typedefs.ListOfNumbers] = None


class ValuesList(common.Attr):
    values: models.Attr[typedefs.Unparsed] = None


class Version(common.Attr):
    version: models.Attr[Literal["1.0", "1.1", "1.2"]] = None


class VertAdvY(common.Attr):
    vert_adv_y: models.Attr[typedefs.Number] = None


class VertOriginX(common.Attr):
    vert_origin_x: models.Attr[typedefs.Number] = None


class VertOriginY(common.Attr):
    vert_origin_y: models.Attr[typedefs.Number] = None


class ViewBox(common.Attr):
    viewBox: models.Attr[
        models.Tuple4[
            typedefs.Number,
            typedefs.Number,
            typedefs.Number,
            typedefs.Number,
        ]
    ] = None


class ViewTarget(common.Attr):
    viewTarget: models.Attr[models.List[typedefs.XmlName]] = None


class Width(common.Attr):
    width: models.Attr[typedefs.Length] = None


class Widths(common.Attr):
    widths: models.Attr[
        models.List[
            typedefs.Urange
            | models.Tuple2[typedefs.Urange, typedefs.Number]
        ]
    ] = None


class XListOfCoordinates(common.Attr):
    x: models.Attr[typedefs.ListOfCoordinates] = None


class XCoordinate(common.Attr):
    x: models.Attr[typedefs.Coordinate] = None


class XNumber(common.Attr):
    x: models.Attr[typedefs.Number] = None


class XHeight(common.Attr):
    x_height: models.Attr[typedefs.Number] = None


class X1(common.Attr):
    x1: models.Attr[typedefs.Coordinate] = None


class X2(common.Attr):
    x2: models.Attr[typedefs.Coordinate] = None


class XChannelSelector(common.Attr):
    xChannelSelector: models.Attr[Literal["R", "G", "B", "A"]] = None


class XlinkActuateOnRequest(common.Attr):
    xlink_actuate: models.Attr[Literal["onRequest"]] = None


class XlinkActuateOnLoad(common.Attr):
    xlink_actuate: models.Attr[Literal["onLoad"]] = None


class XlinkArcrole(common.Attr):
    xlink_arcrole: models.Attr[typedefs.Iri] = None


class XlinkHref(common.Attr):
    xlink_href: models.Attr[typedefs.Iri] = None


class XlinkRole(common.Attr):
    xlink_role: models.Attr[typedefs.Iri] = None


class XlinkShow(common.Attr):
    xlink_show: models.Attr[
        Literal["new", "replace", "embed", "other", "none"]
    ] = None


class XlinkTitle(common.Attr):
    xlink_title: models.Attr[typedefs.Anything] = None


class XlinkType(common.Attr):
    xlink_type: models.Attr[Literal["simple"]] = None


class XmlBase(common.Attr):
    xml_base: models.Attr[typedefs.Iri] = None


class XmlLang(common.Attr):
    xml_lang: models.Attr[typedefs.LanguageId] = None


class Xmlns(common.Attr):
    xmlns: models.Attr[utiltypes.Xmlns] = None


class XmlSpace(common.Attr):
    xml_space: models.Attr[Literal["default", "preserve"]] = None


class YListOfCoordinates(common.Attr):
    y: models.Attr[typedefs.ListOfCoordinates] = None


class YCoordinate(common.Attr):
    y: models.Attr[typedefs.Coordinate] = None


class YNumber(common.Attr):
    y: models.Attr[typedefs.Number] = None


class Y1(common.Attr):
    y1: models.Attr[typedefs.Coordinate] = None


class Y2(common.Attr):
    y2: models.Attr[typedefs.Coordinate] = None


class YChannelSelector(common.Attr):
    yChannelSelector: models.Attr[Literal["R", "G", "B", "A"]] = None


class Z(common.Attr):
    z: models.Attr[typedefs.Number] = None


class ZoomAndPan(common.Attr):
    zoomAndPan: models.Attr[Literal["disable", "magnify"]] = None
