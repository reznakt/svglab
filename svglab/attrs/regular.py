# ruff: noqa: N815

from typing import Literal

import pydantic

from svglab import constants, models
from svglab.attrs import common, types


class AccentHeight(common.Attr):
    accent_height: models.Attr[types.Number] = None


class Accumulate(common.Attr):
    accumulate: models.Attr[types.None_ | Literal["sum"]] = None


class Additive(common.Attr):
    additive: models.Attr[Literal["replace", "sum"]] = None


class Alphabetic(common.Attr):
    alphabetic: models.Attr[types.Number] = None


class Amplitude(common.Attr):
    amplitude: models.Attr[types.Number] = None


class ArabicForm(common.Attr):
    arabic_form: models.Attr[
        Literal["initial", "medial", "terminal", "isolated"]
    ] = None


class Ascent(common.Attr):
    ascent: models.Attr[types.Number] = None


class AttributeName(common.Attr):
    attributeName: models.Attr[types.Unparsed] = None


class AttributeType(common.Attr):
    attributeType: models.Attr[Literal["CSS", "XML"] | types.Auto] = None


class Azimuth(common.Attr):
    azimuth: models.Attr[types.Number] = None


class BaseFrequency(common.Attr):
    baseFrequency: models.Attr[types.NumberOptionalNumber] = None


class BaseProfile(common.Attr):
    baseProfile: models.Attr[types.ProfileName] = None


class Bbox(common.Attr):
    bbox: models.Attr[
        models.Tuple4[
            types.Number, types.Number, types.Number, types.Number
        ]
    ] = None


class Begin(common.Attr):
    begin: models.Attr[types.BeginValueList] = None


class Bias(common.Attr):
    bias: models.Attr[types.Number] = None


class By(common.Attr):
    by: models.Attr[types.Unparsed] = None


class CalcMode(common.Attr):
    calcMode: models.Attr[
        Literal["discrete", "linear", "paced", "spline"]
    ] = None


class CapHeight(common.Attr):
    cap_height: models.Attr[types.Number] = None


class Class(common.Attr):
    class_: models.Attr[types.ListOfStrings] = None


class ClipPathUnits(common.Attr):
    clipPathUnits: models.Attr[
        Literal["userSpaceOnUse", "objectBoundingBox"]
    ] = None


class ContentScriptType(common.Attr):
    contentScriptType: models.Attr[types.ContentType] = None


class ContentStyleType(common.Attr):
    contentStyleType: models.Attr[types.ContentType] = None


class Cx(common.Attr):
    cx: models.Attr[types.Coordinate] = None


class Cy(common.Attr):
    cy: models.Attr[types.Coordinate] = None


class D(common.Attr):
    d: models.Attr[types.PathData] = None


class Descent(common.Attr):
    descent: models.Attr[types.Number] = None


class DiffuseConstant(common.Attr):
    diffuseConstant: models.Attr[types.Number] = None


class Divisor(common.Attr):
    divisor: models.Attr[types.Number] = None


class Dur(common.Attr):
    dur: models.Attr[types.ClockValue | Literal["media", "indefinite"]] = (
        None
    )


class DxListOfLengths(common.Attr):
    dx: models.Attr[types.ListOfLengths] = None


class DxNumber(common.Attr):
    dx: models.Attr[types.Number] = None


class DyListOfLengths(common.Attr):
    dy: models.Attr[types.ListOfLengths] = None


class DyNumber(common.Attr):
    dy: models.Attr[types.Number] = None


class EdgeMode(common.Attr):
    edgeMode: models.Attr[Literal["duplicate", "wrap", "none"]] = None


class Elevation(common.Attr):
    elevation: models.Attr[types.Number] = None


class End(common.Attr):
    end: models.Attr[types.EndValueList] = None


class Exponent(common.Attr):
    exponent: models.Attr[types.Number] = None


class ExternalResourcesRequired(common.Attr):
    externalResourcesRequired: models.Attr[types.Boolean] = None


class FilterRes(common.Attr):
    filterRes: models.Attr[types.NumberOptionalNumber] = None


class FilterUnits(common.Attr):
    filterUnits: models.Attr[
        Literal["userSpaceOnUse", "objectBoundingBox"]
    ] = None


class FontFamily(common.Attr):
    font_family: models.Attr[
        models.List[types.FamilyName | types.GenericFamily]
    ] = None


class FontSize(common.Attr):
    font_size: models.Attr[types.All | types.ListOfLengths] = None


class Format(common.Attr):
    format: models.Attr[types.Unparsed] = None


class From(common.Attr):
    from_: models.Attr[types.Unparsed] = None


class Fx(common.Attr):
    fx: models.Attr[types.Coordinate] = None


class Fy(common.Attr):
    fy: models.Attr[types.Coordinate] = None


class G1(common.Attr):
    g1: models.Attr[types.ListOfNames] = None


class G2(common.Attr):
    g2: models.Attr[types.ListOfNames] = None


class GlyphName(common.Attr):
    glyph_name: models.Attr[types.ListOfNames] = None


class GlyphRef(common.Attr):
    glyphRef: models.Attr[types.Unparsed] = None


class GradientTransform(common.Attr):
    gradientTransform: models.Attr[types.TransformList] = None


class GradientUnits(common.Attr):
    gradientUnits: models.Attr[
        Literal["userSpaceOnUse", "objectBoundingBox"]
    ] = None


class Hanging(common.Attr):
    hanging: models.Attr[types.Number] = None


class Height(common.Attr):
    height: models.Attr[types.Length] = None


class HorizAdvX(common.Attr):
    horiz_adv_x: models.Attr[types.Number] = None


class HorizOriginX(common.Attr):
    horiz_origin_x: models.Attr[types.Number] = None


class HorizOriginY(common.Attr):
    horiz_origin_y: models.Attr[types.Number] = None


class Id(common.Attr):
    id: models.Attr[types.Name] = None


class Ideographic(common.Attr):
    ideographic: models.Attr[types.Number] = None


class In(common.Attr):
    in_: models.Attr[
        types.Paint | types.FilterPrimitiveReference | types.Unparsed
    ] = None


class In2(common.Attr):
    in2: models.Attr[
        types.Paint | types.FilterPrimitiveReference | types.Unparsed
    ] = None


class Intercept(common.Attr):
    intercept: models.Attr[types.Number] = None


class K(common.Attr):
    k: models.Attr[types.Number] = None


class K1(common.Attr):
    k1: models.Attr[types.Number] = None


class K2(common.Attr):
    k2: models.Attr[types.Number] = None


class K3(common.Attr):
    k3: models.Attr[types.Number] = None


class K4(common.Attr):
    k4: models.Attr[types.Number] = None


class KernelMatrix(common.Attr):
    kernelMatrix: models.Attr[types.ListOfNumbers] = None


class KernelUnitLength(common.Attr):
    kernelUnitLength: models.Attr[types.NumberOptionalNumber] = None


class KeyPoints(common.Attr):
    keyPoints: models.Attr[types.ListOfNumbers] = None


class KeySplines(common.Attr):
    keySplines: models.Attr[types.Unparsed] = None


class KeyTimes(common.Attr):
    keyTimes: models.Attr[types.Unparsed] = None


class Lang(common.Attr):
    lang: models.Attr[types.LanguageCodes] = None


class LengthAdjust(common.Attr):
    lengthAdjust: models.Attr[Literal["spacing", "spacingAndGlyphs"]] = (
        None
    )


class LimitingConeAngle(common.Attr):
    limitingConeAngle: models.Attr[types.Number] = None


class Local(common.Attr):
    local: models.Attr[types.Unparsed] = None


class MarkerHeight(common.Attr):
    markerHeight: models.Attr[types.Length] = None


class MarkerUnits(common.Attr):
    markerUnits: models.Attr[Literal["strokeWidth", "userSpaceOnUse"]] = (
        None
    )


class MarkerWidth(common.Attr):
    markerWidth: models.Attr[types.Length] = None


class MaskContentUnits(common.Attr):
    maskContentUnits: models.Attr[
        Literal["userSpaceOnUse", "objectBoundingBox"]
    ] = None


class MaskUnits(common.Attr):
    maskUnits: models.Attr[
        Literal["userSpaceOnUse", "objectBoundingBox"]
    ] = None


class Mathematical(common.Attr):
    mathematical: models.Attr[types.Number] = None


class Max(common.Attr):
    max: models.Attr[Literal["media"] | types.ClockValue] = None


class Media(common.Attr):
    media: models.Attr[types.MediaDescriptors] = None


class Method(common.Attr):
    method: models.Attr[Literal["align", "stretch"]] = None


class Min(common.Attr):
    min: models.Attr[Literal["media"] | types.ClockValue] = None


class Mode(common.Attr):
    mode: models.Attr[
        Literal["normal", "multiply", "screen", "darken", "lighten"]
    ] = None


class NameName(common.Attr):
    name: models.Attr[types.Name] = None


class NameAnything(common.Attr):
    name: models.Attr[types.Anything] = None


class NumOctaves(common.Attr):
    numOctaves: models.Attr[types.Integer] = None


class OffsetNumberPercentage(common.Attr):
    offset: models.Attr[types.Number | types.Percentage] = None


class OffsetNumber(common.Attr):
    offset: models.Attr[types.Number] = None


class OnAbort(common.Attr):
    onabort: models.Attr[types.Anything] = None


class OnActivate(common.Attr):
    onactivate: models.Attr[types.Anything] = None


class OnBegin(common.Attr):
    onbegin: models.Attr[types.Anything] = None


class OnClick(common.Attr):
    onclick: models.Attr[types.Anything] = None


class OnEnd(common.Attr):
    onend: models.Attr[types.Anything] = None


class OnError(common.Attr):
    onerror: models.Attr[types.Anything] = None


class OnFocusIn(common.Attr):
    onfocusin: models.Attr[types.Anything] = None


class OnFocusOut(common.Attr):
    onfocusout: models.Attr[types.Anything] = None


class OnLoad(common.Attr):
    onload: models.Attr[types.Anything] = None


class OnMouseDown(common.Attr):
    onmousedown: models.Attr[types.Anything] = None


class OnMouseMove(common.Attr):
    onmousemove: models.Attr[types.Anything] = None


class OnMouseOut(common.Attr):
    onmouseout: models.Attr[types.Anything] = None


class OnMouseOver(common.Attr):
    onmouseover: models.Attr[types.Anything] = None


class OnMouseUp(common.Attr):
    onmouseup: models.Attr[types.Anything] = None


class OnRepeat(common.Attr):
    onrepeat: models.Attr[types.Anything] = None


class OnResize(common.Attr):
    onresize: models.Attr[types.Anything] = None


class OnScroll(common.Attr):
    onscroll: models.Attr[types.Anything] = None


class OnUnload(common.Attr):
    onunload: models.Attr[types.Anything] = None


class OnZoom(common.Attr):
    onzoom: models.Attr[types.Anything] = None


class OperatorFeComposite(common.Attr):
    operator: models.Attr[
        Literal["over", "in", "out", "atop", "xor", "arithmetic"]
    ] = None


class OperatorFeMorphology(common.Attr):
    operator: models.Attr[Literal["erode", "dilate"]] = None


class Order(common.Attr):
    order: models.Attr[types.NumberOptionalNumber] = None


class Orient(common.Attr):
    orient: models.Attr[types.Auto | types.Angle] = None


class Orientation(common.Attr):
    orientation: models.Attr[Literal["h", "v"]] = None


class Origin(common.Attr):
    origin: models.Attr[Literal["default"]] = None


class OverlinePosition(common.Attr):
    overline_position: models.Attr[types.Number] = None


class OverlineThickness(common.Attr):
    overline_thickness: models.Attr[types.Number] = None


class Panose1(common.Attr):
    panose1: models.Attr[
        models.Tuple[
            tuple[
                types.Integer,
                types.Integer,
                types.Integer,
                types.Integer,
                types.Integer,
                types.Integer,
                types.Integer,
                types.Integer,
                types.Integer,
                types.Integer,
            ]
        ]
    ] = None


class Path(common.Attr):
    path: models.Attr[types.PathData] = None


class PathLength(common.Attr):
    pathLength: models.Attr[types.Number] = None


class PatternContentUnits(common.Attr):
    patternContentUnits: models.Attr[
        Literal["userSpaceOnUse", "objectBoundingBox"]
    ] = None


class PatternTransform(common.Attr):
    patternTransform: models.Attr[types.TransformList] = None


class PatternUnits(common.Attr):
    patternUnits: models.Attr[
        Literal["userSpaceOnUse", "objectBoundingBox"]
    ] = None


class Points(common.Attr):
    points: models.Attr[types.ListOfPoints] = None


class PointsAtX(common.Attr):
    pointsAtX: models.Attr[types.Number] = None


class PointsAtY(common.Attr):
    pointsAtY: models.Attr[types.Number] = None


class PointsAtZ(common.Attr):
    pointsAtZ: models.Attr[types.Number] = None


class PreserveAlpha(common.Attr):
    preserveAlpha: models.Attr[types.Boolean] = None


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
        | types.Unparsed
    ] = None


class PrimitiveUnits(common.Attr):
    primitiveUnits: models.Attr[
        Literal["userSpaceOnUse", "objectBoundingBox"]
    ] = None


class R(common.Attr):
    r: models.Attr[types.Length] = None


class Radius(common.Attr):
    radius: models.Attr[types.NumberOptionalNumber] = None


class RefX(common.Attr):
    ref_x: models.Attr[types.Coordinate] = None


class RefY(common.Attr):
    ref_y: models.Attr[types.Coordinate] = None


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
        Literal["indefinite"] | types.NumericValue
    ] = None


class RepeatDur(common.Attr):
    repeatDur: models.Attr[Literal["indefinite"] | types.ClockValue] = None


class RequiredExtensions(common.Attr):
    requiredExtensions: models.Attr[types.ListOfExtensions] = None


class RequiredFeatures(common.Attr):
    requiredFeatures: models.Attr[types.ListOfFeatures] = None


class Restart(common.Attr):
    restart: models.Attr[Literal["always", "whenNotActive", "never"]] = (
        None
    )


class Result(common.Attr):
    result: models.Attr[types.FilterPrimitiveReference] = None


class RotateListOfNumbers(common.Attr):
    rotate: models.Attr[types.ListOfNumbers] = None


class RotateNumberAutoAutoReverse(common.Attr):
    rotate: (
        models.Attr[types.Number] | types.Auto | Literal["auto-reverse"]
    ) = None


class Rx(common.Attr):
    rx: models.Attr[types.Length] = None


class Ry(common.Attr):
    ry: models.Attr[types.Length] = None


class Scale(common.Attr):
    scale: models.Attr[types.Number] = None


class Seed(common.Attr):
    seed: models.Attr[types.Number] = None


class Slope(common.Attr):
    slope: models.Attr[types.Number] = None


class Spacing(common.Attr):
    spacing: models.Attr[Literal["auto", "exact"]] = None


class SpecularConstant(common.Attr):
    specularConstant: models.Attr[types.Number] = None


class SpecularExponent(common.Attr):
    specularExponent: models.Attr[types.Number] = None


class SpreadMethod(common.Attr):
    spreadMethod: models.Attr[Literal["pad", "reflect", "repeat"]] = None


class StartOffset(common.Attr):
    startOffset: models.Attr[types.Length] = None


class StdDeviation(common.Attr):
    stdDeviation: models.Attr[types.NumberOptionalNumber] = None


class Stemh(common.Attr):
    stemh: models.Attr[types.Number] = None


class Stemv(common.Attr):
    stemv: models.Attr[types.Number] = None


class StitchTiles(common.Attr):
    stitchTiles: models.Attr[Literal["stitch", "noStitch"]] = None


class StrikethroughPosition(common.Attr):
    strikethrough_position: models.Attr[types.Number] = None


class StrikethroughThickness(common.Attr):
    strikethrough_thickness: models.Attr[types.Number] = None


class String(common.Attr):
    string: models.Attr[types.Anything] = None


class Style(common.Attr):
    style: models.Attr[types.Unparsed] = None


class SurfaceScale(common.Attr):
    surfaceScale: models.Attr[types.Number] = None


class SystemLanguage(common.Attr):
    systemLanguage: models.Attr[types.LanguageCodes] = None


class TableValues(common.Attr):
    tableValues: models.Attr[types.ListOfNumbers] = None


class Target(common.Attr):
    target: models.Attr[
        Literal["_replace", "_self", "_parent", "_top", "_blank"]
        | types.XmlName
    ] = None


class TargetX(common.Attr):
    targetX: models.Attr[types.Integer] = None


class TargetY(common.Attr):
    targetY: models.Attr[types.Integer] = None


class TextLength(common.Attr):
    textLength: models.Attr[types.Length] = None


class Title(common.Attr):
    title: models.Attr[types.AdvisoryTitle] = None


class To(common.Attr):
    to: models.Attr[types.Unparsed] = None


class Transform(common.Attr):
    transform: models.Attr[types.TransformList] = None


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
    type: models.Attr[types.ContentType] = None


class TypeFeFunc(common.Attr):
    type: models.Attr[
        Literal["identity", "table", "discrete", "linear", "gamma"]
    ] = None


class U1(common.Attr):
    u1: models.Attr[models.List[types.Character | types.Urange]] = None


class U2(common.Attr):
    u2: models.Attr[models.List[types.Character | types.Urange]] = None


class UnderlinePosition(common.Attr):
    underline_position: models.Attr[types.Number] = None


class UnderlineThickness(common.Attr):
    underline_thickness: models.Attr[types.Number] = None


class Unicode(common.Attr):
    unicode: models.Attr[types.Anything] = None


class UnicodeRange(common.Attr):
    unicode_range: models.Attr[models.List[types.Urange]] = None


class UnitsPerEm(common.Attr):
    units_per_em: models.Attr[types.Number] = None


class VAlphabetic(common.Attr):
    v_alphabetic: models.Attr[types.Number] = None


class VHanging(common.Attr):
    v_hanging: models.Attr[types.Number] = None


class VIdeographic(common.Attr):
    v_ideographic: models.Attr[types.Number] = None


class VMathematical(common.Attr):
    v_mathematical: models.Attr[types.Number] = None


class ValuesListOfNumbers(common.Attr):
    values: models.Attr[types.ListOfNumbers] = None


class ValuesList(common.Attr):
    values: models.Attr[types.Unparsed] = None


class Version(common.Attr):
    version: models.Attr[Literal["1.1"]] = None


class VertAdvY(common.Attr):
    vert_adv_y: models.Attr[types.Number] = None


class VertOriginX(common.Attr):
    vert_origin_x: models.Attr[types.Number] = None


class VertOriginY(common.Attr):
    vert_origin_y: models.Attr[types.Number] = None


class ViewBox(common.Attr):
    viewBox: models.Attr[
        models.Tuple4[
            types.Number, types.Number, types.Number, types.Number
        ]
    ] = None


class ViewTarget(common.Attr):
    viewTarget: models.Attr[models.List[types.XmlName]] = None


class Width(common.Attr):
    width: models.Attr[types.Length] = None


class Widths(common.Attr):
    widths: models.Attr[
        models.List[
            types.Urange | models.Tuple2[types.Urange, types.Number]
        ]
    ] = None


class XListOfCoordinates(common.Attr):
    x: models.Attr[types.ListOfCoordinates] = None


class XCoordinate(common.Attr):
    x: models.Attr[types.Coordinate] = None


class XNumber(common.Attr):
    x: models.Attr[types.Number] = None


class XHeight(common.Attr):
    x_height: models.Attr[types.Number] = None


class X1(common.Attr):
    x1: models.Attr[types.Coordinate] = None


class X2(common.Attr):
    x2: models.Attr[types.Coordinate] = None


class XChannelSelector(common.Attr):
    xChannelSelector: models.Attr[Literal["R", "G", "B", "A"]] = None


class XlinkActuateOnRequest(common.Attr):
    xlink_actuate: models.Attr[Literal["onRequest"]] = None


class XlinkActuateOnLoad(common.Attr):
    xlink_actuate: models.Attr[Literal["onLoad"]] = None


class XlinkArcrole(common.Attr):
    xlink_arcrole: models.Attr[types.Iri] = None


class XlinkHref(common.Attr):
    xlink_href: models.Attr[types.Iri] = None


class XlinkRole(common.Attr):
    xlink_role: models.Attr[types.Iri] = None


class XlinkShow(common.Attr):
    xlink_show: models.Attr[
        Literal["new", "replace", "embed", "other", "none"]
    ] = None


class XlinkTitle(common.Attr):
    xlink_title: models.Attr[types.Anything] = None


class XlinkType(common.Attr):
    xlink_type: models.Attr[Literal["simple"]] = None


class XmlBase(common.Attr):
    xml_base: models.Attr[types.Iri] = None


class XmlLang(common.Attr):
    xml_lang: models.Attr[types.LanguageId] = None


class Xmlns(common.Attr):
    # cannot use Final here because pydantic will consider the field a ClassVar
    # see https://github.com/pydantic/pydantic/issues/6253
    xmlns: constants.Xmlns = pydantic.Field(
        default=constants.DEFAULT_XMLNS, frozen=True
    )


class XmlSpace(common.Attr):
    xml_space: models.Attr[Literal["default", "preserve"]] = None


class YListOfCoordinates(common.Attr):
    y: models.Attr[types.ListOfCoordinates] = None


class YCoordinate(common.Attr):
    y: models.Attr[types.Coordinate] = None


class YNumber(common.Attr):
    y: models.Attr[types.Number] = None


class Y1(common.Attr):
    y1: models.Attr[types.Coordinate] = None


class Y2(common.Attr):
    y2: models.Attr[types.Coordinate] = None


class YChannelSelector(common.Attr):
    yChannelSelector: models.Attr[Literal["R", "G", "B", "A"]] = None


class Z(common.Attr):
    z: models.Attr[types.Number] = None


class ZoomAndPan(common.Attr):
    zoomAndPan: models.Attr[Literal["disable", "magnify"]] = None
