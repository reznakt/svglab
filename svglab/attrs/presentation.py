from typing import Literal

from svglab import models
from svglab.attrs import common, types


class AlignmentBaseline(common.Attr):
    alignment_baseline: models.Attr[
        types.Auto
        | types.Inherit
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


class BaselineShift(common.Attr):
    baseline_shift: models.Attr[
        Literal["baseline", "sub", "super"]
        | types.Percentage
        | types.Length
        | types.Inherit
    ] = None


class ClipPath(common.Attr):
    clip_path: models.Attr[types.FuncIri | types.None_ | types.Inherit] = (
        None
    )


class ClipRule(common.Attr):
    clip_rule: models.Attr[
        Literal["nonzero", "evenodd"] | types.Inherit
    ] = None


class Clip(common.Attr):
    clip: models.Attr[types.Shape | types.Auto | types.Inherit] = None


class ColorInterpolationFilters(common.Attr):
    color_interpolation_filters: models.Attr[
        types.Auto | Literal["sRGB", "linearRGB"] | types.Inherit
    ] = None


class ColorInterpolation(common.Attr):
    color_interpolation: models.Attr[
        types.Auto | Literal["sRGB", "linearRGB"] | types.Inherit
    ] = None


class ColorProfile(common.Attr):
    color_profile: models.Attr[
        types.Auto
        | Literal["sRGB"]
        | types.Name
        | types.Iri
        | types.Inherit
    ] = None


class ColorRendering(common.Attr):
    color_rendering: models.Attr[
        types.Auto
        | Literal["optimizeSpeed", "optimizeQuality"]
        | types.Inherit
    ] = None


class Color(common.Attr):
    color: models.Attr[types.Color | types.Inherit] = None


class Cursor(common.Attr):
    cursor: models.Attr[
        types.CursorValue | types.Inherit | models.List[types.CursorValue]
    ] = None


class Direction(common.Attr):
    direction: models.Attr[Literal["ltr", "rtl"] | types.Inherit] = None


class Display(common.Attr):
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
        | types.None_
        | types.Inherit
    ] = None


class DominantBaseline(common.Attr):
    dominant_baseline: models.Attr[
        types.Auto
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
        | types.Inherit
    ] = None


class EnableBackground(common.Attr):
    enable_background: models.Attr[
        Literal["accumulate"]
        | types.Inherit
        | types.Unparsed  # new [ <x> <y> <width> <height> ]
    ] = None


class FillOpacity(common.Attr):
    fill_opacity: models.Attr[types.OpacityValue | types.Inherit] = None


class FillRule(common.Attr):
    fill_rule: models.Attr[
        Literal["nonzero", "evenodd"] | types.Inherit
    ] = None


class Fill(common.Attr):
    fill: models.Attr[types.Paint] = None


class Filter(common.Attr):
    filter: models.Attr[types.FuncIri | types.None_ | types.Inherit] = None


class FloodColor(common.Attr):
    flood_color: models.Attr[
        Literal["currentColor"]
        | types.Color
        | types.Inherit
        | types.Unparsed  # <color> [<icccolor>]
    ] = None


class FloodOpacity(common.Attr):
    flood_opacity: models.Attr[types.OpacityValue | types.Inherit] = None


class FontSizeAdjust(common.Attr):
    font_size_adjust: models.Attr[
        types.Number | types.None_ | types.Inherit
    ] = None


class FontSize(common.Attr):
    font_size: models.Attr[
        types.AbsoluteSize
        | types.RelativeSize
        | types.Length
        | types.Percentage
        | types.Inherit
    ] = None


class FontStretch(common.Attr):
    font_stretch: models.Attr[
        Literal[
            "normal",
            "wider",
            "narrower",
            "ultra-condensed",
            "extra-condensed",
            "condensed",
            "semi-condensed",
            "semi-expanded",
            "expanded",
            "extra-expanded",
            "ultra-expanded",
        ]
        | types.Inherit
    ] = None


class FontStyle(common.Attr):
    font_style: models.Attr[
        Literal["normal", "italic", "oblique"] | types.Inherit
    ] = None


class FontVariant(common.Attr):
    font_variant: models.Attr[
        Literal["normal", "small-caps"] | types.Inherit
    ] = None


class FontWeight(common.Attr):
    font_weight: models.Attr[
        Literal[
            "normal",
            "bold",
            "bolder",
            "lighter",
            100,
            200,
            300,
            400,
            500,
            600,
            700,
            800,
            900,
        ]
        | types.Inherit
    ] = None


class GlyphOrientationHorizontal(common.Attr):
    glyph_orientation_horizontal: models.Attr[
        types.Angle | types.Inherit
    ] = None


class GlyphOrientationVertical(common.Attr):
    glyph_orientation_vertical: models.Attr[
        types.Auto | types.Angle | types.Inherit
    ] = None


class ImageRendering(common.Attr):
    image_rendering: models.Attr[
        types.Auto
        | Literal["optimizeSpeed", "optimizeQuality"]
        | types.Inherit
    ] = None


class Kerning(common.Attr):
    kerning: models.Attr[types.Auto | types.Length | types.Inherit] = None


class LetterSpacing(common.Attr):
    letter_spacing: models.Attr[
        Literal["normal"] | types.Length | types.Inherit
    ] = None


class LightingColor(common.Attr):
    lighting_color: models.Attr[
        Literal["currentColor"]
        | types.Color
        | types.Inherit
        | types.Unparsed
    ] = None


class MarkerEnd(common.Attr):
    marker_end: models.Attr[
        types.FuncIri | types.None_ | types.Inherit
    ] = None


class MarkerMid(common.Attr):
    marker_mid: models.Attr[
        types.FuncIri | types.None_ | types.Inherit
    ] = None


class MarkerStart(common.Attr):
    marker_start: models.Attr[
        types.FuncIri | types.None_ | types.Inherit
    ] = None


class Mask(common.Attr):
    mask: models.Attr[types.FuncIri | types.None_ | types.Inherit] = None


class Opacity(common.Attr):
    opacity: models.Attr[types.OpacityValue | types.Inherit] = None


class Overflow(common.Attr):
    overflow: models.Attr[
        Literal["visible", "hidden", "scroll"] | types.Auto | types.Inherit
    ] = None


class PointerEvents(common.Attr):
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
        | types.All
        | types.None_
        | types.Inherit
    ] = None


class ShapeRendering(common.Attr):
    shape_rendering: models.Attr[
        types.Auto
        | Literal["optimizeSpeed", "crispEdges", "geometricPrecision"]
        | types.Inherit
    ] = None


class StopColor(common.Attr):
    stop_color: models.Attr[
        Literal["currentColor"]
        | types.Inherit
        | types.Unparsed  # <color> <icccolor>
    ] = None


class StopOpacity(common.Attr):
    stop_opacity: models.Attr[types.OpacityValue | types.Inherit] = None


class StrokeDasharray(common.Attr):
    stroke_dasharray: models.Attr[
        types.None_ | types.Dasharray | types.Inherit
    ] = None


class StrokeDashoffset(common.Attr):
    stroke_dashoffset: models.Attr[
        types.Percentage | types.Length | types.Inherit
    ] = None


class StrokeLinecap(common.Attr):
    stroke_linecap: models.Attr[
        Literal["butt", "round", "square"] | types.Inherit
    ] = None


class StrokeLinejoin(common.Attr):
    stroke_linejoin: models.Attr[
        Literal["miter", "round", "bevel"] | types.Inherit
    ] = None


class StrokeMiterlimit(common.Attr):
    stroke_miterlimit: models.Attr[types.Miterlimit | types.Inherit] = None


class StrokeOpacity(common.Attr):
    stroke_opacity: models.Attr[types.OpacityValue | types.Inherit] = None


class StrokeWidth(common.Attr):
    stroke_width: models.Attr[
        types.Percentage | types.Length | types.Inherit
    ] = None


class Stroke(common.Attr):
    stroke: models.Attr[types.Paint] = None


class TextAnchor(common.Attr):
    text_anchor: models.Attr[
        Literal["start", "middle", "end"] | types.Inherit
    ] = None


class TextDecoration(common.Attr):
    text_decoration: models.Attr[
        types.None_
        | Literal["underline", "overline", "line-through", "blink"]
        | types.Inherit
    ] = None


class TextRendering(common.Attr):
    text_rendering: models.Attr[
        types.Auto
        | Literal[
            "optimizeSpeed", "optimizeLegibility", "geometricPrecision"
        ]
        | types.Inherit
    ] = None


class UnicodeBidi(common.Attr):
    unicode_bidi: models.Attr[
        Literal["normal", "embed", "bidi-override"] | types.Inherit
    ] = None


class Visibility(common.Attr):
    visibility: models.Attr[
        Literal["visible", "hidden", "collapse"] | types.Inherit
    ] = None


class WordSpacing(common.Attr):
    word_spacing: models.Attr[
        Literal["normal"] | types.Length | types.Inherit
    ] = None


class WritingMode(common.Attr):
    writing_mode: models.Attr[
        Literal["lr-tb", "rl-tb", "tb-rl", "lr", "rl", "tb"]
        | types.Inherit
    ] = None
