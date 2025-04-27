"""Definitions of presentation attributes."""

# ruff: noqa:  D101

from typing_extensions import Literal

from svglab import models
from svglab.attrs import common, typedefs


class AlignmentBaseline(common.Attr):
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


class BaselineShift(common.Attr):
    baseline_shift: models.Attr[
        Literal["baseline", "sub", "super"]
        | typedefs.Percentage
        | typedefs.Length
        | typedefs.Inherit
    ] = None


class ClipPath(common.Attr):
    clip_path: models.Attr[
        typedefs.FuncIri | typedefs.None_ | typedefs.Inherit
    ] = None


class ClipRule(common.Attr):
    clip_rule: models.Attr[
        Literal["nonzero", "evenodd"] | typedefs.Inherit
    ] = None


class Clip(common.Attr):
    clip: models.Attr[
        typedefs.Shape | typedefs.Auto | typedefs.Inherit
    ] = None


class ColorInterpolationFilters(common.Attr):
    color_interpolation_filters: models.Attr[
        typedefs.Auto | Literal["sRGB", "linearRGB"] | typedefs.Inherit
    ] = None


class ColorInterpolation(common.Attr):
    color_interpolation: models.Attr[
        typedefs.Auto | Literal["sRGB", "linearRGB"] | typedefs.Inherit
    ] = None


class ColorProfile(common.Attr):
    color_profile: models.Attr[
        typedefs.Auto
        | Literal["sRGB"]
        | typedefs.Name
        | typedefs.Iri
        | typedefs.Inherit
    ] = None


class ColorRendering(common.Attr):
    color_rendering: models.Attr[
        typedefs.Auto
        | Literal["optimizeSpeed", "optimizeQuality"]
        | typedefs.Inherit
    ] = None


class Color(common.Attr):
    color: models.Attr[typedefs.Color | typedefs.Inherit] = None


class Cursor(common.Attr):
    cursor: models.Attr[
        typedefs.CursorValue
        | typedefs.Inherit
        | models.List[typedefs.CursorValue]
    ] = None


class Direction(common.Attr):
    direction: models.Attr[Literal["ltr", "rtl"] | typedefs.Inherit] = None


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
        | typedefs.None_
        | typedefs.Inherit
    ] = None


class DominantBaseline(common.Attr):
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


class EnableBackground(common.Attr):
    enable_background: models.Attr[
        Literal["accumulate"]
        | typedefs.Inherit
        | typedefs.Unparsed  # new [ <x> <y> <width> <height> ]
    ] = None


class FillOpacity(common.Attr):
    fill_opacity: models.Attr[typedefs.OpacityValue | typedefs.Inherit] = (
        None
    )


class FillRule(common.Attr):
    fill_rule: models.Attr[
        Literal["nonzero", "evenodd"] | typedefs.Inherit
    ] = None


class Filter(common.Attr):
    filter: models.Attr[
        typedefs.FuncIri | typedefs.None_ | typedefs.Inherit
    ] = None


class FloodColor(common.Attr):
    flood_color: models.Attr[
        Literal["currentColor"]
        | typedefs.Inherit
        | typedefs.IccColor
        | typedefs.Color
    ] = None


class FloodOpacity(common.Attr):
    flood_opacity: models.Attr[
        typedefs.OpacityValue | typedefs.Inherit
    ] = None


class FontSizeAdjust(common.Attr):
    font_size_adjust: models.Attr[
        typedefs.Number | typedefs.None_ | typedefs.Inherit
    ] = None


class GlyphOrientationHorizontal(common.Attr):
    glyph_orientation_horizontal: models.Attr[
        typedefs.Angle | typedefs.Inherit
    ] = None


class GlyphOrientationVertical(common.Attr):
    glyph_orientation_vertical: models.Attr[
        typedefs.Auto | typedefs.Angle | typedefs.Inherit
    ] = None


class ImageRendering(common.Attr):
    image_rendering: models.Attr[
        typedefs.Auto
        | Literal["optimizeSpeed", "optimizeQuality"]
        | typedefs.Inherit
    ] = None


class Kerning(common.Attr):
    kerning: models.Attr[
        typedefs.Auto | typedefs.Length | typedefs.Inherit
    ] = None


class LetterSpacing(common.Attr):
    letter_spacing: models.Attr[
        Literal["normal"] | typedefs.Length | typedefs.Inherit
    ] = None


class LightingColor(common.Attr):
    lighting_color: models.Attr[
        Literal["currentColor"]
        | typedefs.Color
        | typedefs.Inherit
        | typedefs.Unparsed
    ] = None


class MarkerEnd(common.Attr):
    marker_end: models.Attr[
        typedefs.FuncIri | typedefs.None_ | typedefs.Inherit
    ] = None


class MarkerMid(common.Attr):
    marker_mid: models.Attr[
        typedefs.FuncIri | typedefs.None_ | typedefs.Inherit
    ] = None


class MarkerStart(common.Attr):
    marker_start: models.Attr[
        typedefs.FuncIri | typedefs.None_ | typedefs.Inherit
    ] = None


class Mask(common.Attr):
    mask: models.Attr[
        typedefs.FuncIri | typedefs.None_ | typedefs.Inherit
    ] = None


class Opacity(common.Attr):
    opacity: models.Attr[typedefs.OpacityValue | typedefs.Inherit] = None


class Overflow(common.Attr):
    overflow: models.Attr[
        Literal["visible", "hidden", "scroll"]
        | typedefs.Auto
        | typedefs.Inherit
    ] = None


class PaintOrder(common.Attr):
    paint_order: (
        models.Attr[Literal["normal", "fill", "stroke", "markers"]]
        | typedefs.Inherit
    ) = None


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
        | typedefs.All
        | typedefs.None_
        | typedefs.Inherit
    ] = None


class ShapeRendering(common.Attr):
    shape_rendering: models.Attr[
        typedefs.Auto
        | Literal["optimizeSpeed", "crispEdges", "geometricPrecision"]
        | typedefs.Inherit
    ] = None


class StopColor(common.Attr):
    stop_color: models.Attr[
        Literal["currentColor"]
        | typedefs.Inherit
        | typedefs.IccColor
        | typedefs.Color
    ] = None


class StopOpacity(common.Attr):
    stop_opacity: models.Attr[typedefs.OpacityValue | typedefs.Inherit] = (
        None
    )


class StrokeDasharray(common.Attr):
    stroke_dasharray: models.Attr[
        typedefs.None_ | typedefs.Dasharray | typedefs.Inherit
    ] = None


class StrokeDashoffset(common.Attr):
    stroke_dashoffset: models.Attr[
        typedefs.Percentage | typedefs.Length | typedefs.Inherit
    ] = None


class StrokeLinecap(common.Attr):
    stroke_linecap: models.Attr[
        Literal["butt", "round", "square"] | typedefs.Inherit
    ] = None


class StrokeLinejoin(common.Attr):
    stroke_linejoin: models.Attr[
        Literal["miter", "round", "bevel", "miter-clip", "arcs"]
        | typedefs.Inherit
    ] = None


class StrokeMiterlimit(common.Attr):
    stroke_miterlimit: models.Attr[
        typedefs.Miterlimit | typedefs.Inherit
    ] = None


class StrokeOpacity(common.Attr):
    stroke_opacity: models.Attr[
        typedefs.OpacityValue | typedefs.Inherit
    ] = None


class StrokeWidth(common.Attr):
    stroke_width: models.Attr[
        typedefs.Percentage | typedefs.Length | typedefs.Inherit
    ] = None


class Stroke(common.Attr):
    stroke: models.Attr[typedefs.Paint] = None


class TextAlign(common.Attr):
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


class TextAlignAll(common.Attr):
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


class TextAlignLast(common.Attr):
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


class TextAnchor(common.Attr):
    text_anchor: models.Attr[
        Literal["start", "middle", "end"] | typedefs.Inherit
    ] = None


class TextDecoration(common.Attr):
    text_decoration: models.Attr[
        typedefs.None_
        | Literal["underline", "overline", "line-through", "blink"]
        | typedefs.Inherit
    ] = None


class TextIndent(common.Attr):
    text_indent: models.Attr[
        typedefs.Length
        | typedefs.Percentage
        | Literal["each-line", "hanging"]
        | typedefs.Inherit
    ] = None


class TextRendering(common.Attr):
    text_rendering: models.Attr[
        typedefs.Auto
        | Literal[
            "optimizeSpeed", "optimizeLegibility", "geometricPrecision"
        ]
        | typedefs.Inherit
    ] = None


class TransformOrigin(common.Attr):
    transform_origin: models.Attr[typedefs.TransformOrigin] = None


class Transform(common.Attr):
    transform: models.Attr[typedefs.TransformList] = None


class UnicodeBidi(common.Attr):
    unicode_bidi: models.Attr[
        Literal["normal", "embed", "bidi-override"] | typedefs.Inherit
    ] = None


class VectorEffect(common.Attr):
    vector_effect: models.Attr[
        Literal[
            "non-scaling-stroke",
            "non-scaling-size",
            "non-rotation",
            "fixed-position",
        ]
        | typedefs.None_
    ] = None


class Visibility(common.Attr):
    visibility: models.Attr[
        Literal["visible", "hidden", "collapse"] | typedefs.Inherit
    ] = None


class WhiteSpace(common.Attr):
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


class WordSpacing(common.Attr):
    word_spacing: models.Attr[
        Literal["normal"] | typedefs.Length | typedefs.Inherit
    ] = None


class WritingMode(common.Attr):
    writing_mode: models.Attr[
        Literal["lr-tb", "rl-tb", "tb-rl", "lr", "rl", "tb"]
        | typedefs.Inherit
    ] = None
