"""Definitions of presentation attributes."""

# ruff: noqa:  D101

from typing_extensions import Literal

from svglab import models
from svglab.attrs import common, typedefs


class AlignmentBaselineAttr(common.Attr):
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


class BaselineShiftAttr(common.Attr):
    baseline_shift: models.Attr[
        Literal["baseline", "sub", "super"]
        | typedefs.Percentage
        | typedefs.Length
        | typedefs.Inherit
    ] = None


class ClipPathAttr(common.Attr):
    clip_path: models.Attr[
        typedefs.FuncIri | typedefs.None_ | typedefs.Inherit
    ] = None


class ClipRuleAttr(common.Attr):
    clip_rule: models.Attr[
        Literal["nonzero", "evenodd"] | typedefs.Inherit
    ] = None


class ClipAttr(common.Attr):
    clip: models.Attr[
        typedefs.Shape | typedefs.Auto | typedefs.Inherit
    ] = None


class ColorInterpolationFiltersAttr(common.Attr):
    color_interpolation_filters: models.Attr[
        typedefs.Auto | Literal["sRGB", "linearRGB"] | typedefs.Inherit
    ] = None


class ColorInterpolationAttr(common.Attr):
    color_interpolation: models.Attr[
        typedefs.Auto | Literal["sRGB", "linearRGB"] | typedefs.Inherit
    ] = None


class ColorProfileAttr(common.Attr):
    color_profile: models.Attr[
        typedefs.Auto
        | Literal["sRGB"]
        | typedefs.Name
        | typedefs.Iri
        | typedefs.Inherit
    ] = None


class ColorRenderingAttr(common.Attr):
    color_rendering: models.Attr[
        typedefs.Auto
        | Literal["optimizeSpeed", "optimizeQuality"]
        | typedefs.Inherit
    ] = None


class ColorAttr(common.Attr):
    color: models.Attr[typedefs.Color | typedefs.Inherit] = None


class CursorAttr(common.Attr):
    cursor: models.Attr[
        typedefs.CursorValue
        | typedefs.Inherit
        | models.List[typedefs.CursorValue]
    ] = None


class DirectionAttr(common.Attr):
    direction: models.Attr[Literal["ltr", "rtl"] | typedefs.Inherit] = None


class DisplayAttr(common.Attr):
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


class DominantBaselineAttr(common.Attr):
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


class EnableBackgroundAttr(common.Attr):
    enable_background: models.Attr[
        Literal["accumulate"]
        | typedefs.Inherit
        | typedefs.Unparsed  # new [ <x> <y> <width> <height> ]
    ] = None


class FillOpacityAttr(common.Attr):
    fill_opacity: models.Attr[typedefs.OpacityValue | typedefs.Inherit] = (
        None
    )


class FillRuleAttr(common.Attr):
    fill_rule: models.Attr[
        Literal["nonzero", "evenodd"] | typedefs.Inherit
    ] = None


class FilterAttr(common.Attr):
    filter: models.Attr[
        typedefs.FuncIri | typedefs.None_ | typedefs.Inherit
    ] = None


class FloodColorAttr(common.Attr):
    flood_color: models.Attr[
        Literal["currentColor"]
        | typedefs.Inherit
        | typedefs.IccColor
        | typedefs.Color
    ] = None


class FloodOpacityAttr(common.Attr):
    flood_opacity: models.Attr[
        typedefs.OpacityValue | typedefs.Inherit
    ] = None


class FontSizeAdjustAttr(common.Attr):
    font_size_adjust: models.Attr[
        typedefs.Number | typedefs.None_ | typedefs.Inherit
    ] = None


class GlyphOrientationHorizontalAttr(common.Attr):
    glyph_orientation_horizontal: models.Attr[
        typedefs.Angle | typedefs.Inherit
    ] = None


class GlyphOrientationVerticalAttr(common.Attr):
    glyph_orientation_vertical: models.Attr[
        typedefs.Auto | typedefs.Angle | typedefs.Inherit
    ] = None


class ImageRenderingAttr(common.Attr):
    image_rendering: models.Attr[
        typedefs.Auto
        | Literal["optimizeSpeed", "optimizeQuality"]
        | typedefs.Inherit
    ] = None


class KerningAttr(common.Attr):
    kerning: models.Attr[
        typedefs.Auto | typedefs.Length | typedefs.Inherit
    ] = None


class LetterSpacingAttr(common.Attr):
    letter_spacing: models.Attr[
        Literal["normal"] | typedefs.Length | typedefs.Inherit
    ] = None


class LightingColorAttr(common.Attr):
    lighting_color: models.Attr[
        Literal["currentColor"]
        | typedefs.Color
        | typedefs.Inherit
        | typedefs.Unparsed
    ] = None


class MarkerEndAttr(common.Attr):
    marker_end: models.Attr[
        typedefs.FuncIri | typedefs.None_ | typedefs.Inherit
    ] = None


class MarkerMidAttr(common.Attr):
    marker_mid: models.Attr[
        typedefs.FuncIri | typedefs.None_ | typedefs.Inherit
    ] = None


class MarkerStartAttr(common.Attr):
    marker_start: models.Attr[
        typedefs.FuncIri | typedefs.None_ | typedefs.Inherit
    ] = None


class MaskAttr(common.Attr):
    mask: models.Attr[
        typedefs.FuncIri | typedefs.None_ | typedefs.Inherit
    ] = None


class OpacityAttr(common.Attr):
    opacity: models.Attr[typedefs.OpacityValue | typedefs.Inherit] = None


class OverflowAttr(common.Attr):
    overflow: models.Attr[
        Literal["visible", "hidden", "scroll"]
        | typedefs.Auto
        | typedefs.Inherit
    ] = None


class PaintOrderAttr(common.Attr):
    paint_order: (
        models.Attr[Literal["normal", "fill", "stroke", "markers"]]
        | typedefs.Inherit
    ) = None


class PointerEventsAttr(common.Attr):
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


class ShapeRenderingAttr(common.Attr):
    shape_rendering: models.Attr[
        typedefs.Auto
        | Literal["optimizeSpeed", "crispEdges", "geometricPrecision"]
        | typedefs.Inherit
    ] = None


class StopColorAttr(common.Attr):
    stop_color: models.Attr[
        Literal["currentColor"]
        | typedefs.Inherit
        | typedefs.IccColor
        | typedefs.Color
    ] = None


class StopOpacityAttr(common.Attr):
    stop_opacity: models.Attr[typedefs.OpacityValue | typedefs.Inherit] = (
        None
    )


class StrokeDasharrayAttr(common.Attr):
    stroke_dasharray: models.Attr[
        typedefs.None_ | typedefs.Dasharray | typedefs.Inherit
    ] = None


class StrokeDashoffsetAttr(common.Attr):
    stroke_dashoffset: models.Attr[
        typedefs.Percentage | typedefs.Length | typedefs.Inherit
    ] = None


class StrokeLinecapAttr(common.Attr):
    stroke_linecap: models.Attr[
        Literal["butt", "round", "square"] | typedefs.Inherit
    ] = None


class StrokeLinejoinAttr(common.Attr):
    stroke_linejoin: models.Attr[
        Literal["miter", "round", "bevel", "miter-clip", "arcs"]
        | typedefs.Inherit
    ] = None


class StrokeMiterlimitAttr(common.Attr):
    stroke_miterlimit: models.Attr[
        typedefs.Miterlimit | typedefs.Inherit
    ] = None


class StrokeOpacityAttr(common.Attr):
    stroke_opacity: models.Attr[
        typedefs.OpacityValue | typedefs.Inherit
    ] = None


class StrokeWidthAttr(common.Attr):
    stroke_width: models.Attr[
        typedefs.Percentage | typedefs.Length | typedefs.Inherit
    ] = None


class StrokeAttr(common.Attr):
    stroke: models.Attr[typedefs.Paint] = None


class TextAlignAttr(common.Attr):
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


class TextAlignAllAttr(common.Attr):
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


class TextAlignLastAttr(common.Attr):
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


class TextAnchorAttr(common.Attr):
    text_anchor: models.Attr[
        Literal["start", "middle", "end"] | typedefs.Inherit
    ] = None


class TextDecorationAttr(common.Attr):
    text_decoration: models.Attr[
        typedefs.None_
        | Literal["underline", "overline", "line-through", "blink"]
        | typedefs.Inherit
    ] = None


class TextIndentAttr(common.Attr):
    text_indent: models.Attr[
        typedefs.Length
        | typedefs.Percentage
        | Literal["each-line", "hanging"]
        | typedefs.Inherit
    ] = None


class TextRenderingAttr(common.Attr):
    text_rendering: models.Attr[
        typedefs.Auto
        | Literal[
            "optimizeSpeed", "optimizeLegibility", "geometricPrecision"
        ]
        | typedefs.Inherit
    ] = None


class TransformOriginAttr(common.Attr):
    transform_origin: models.Attr[typedefs.TransformOrigin] = None


class TransformAttr(common.Attr):
    transform: models.Attr[typedefs.TransformList] = None


class UnicodeBidiAttr(common.Attr):
    unicode_bidi: models.Attr[
        Literal["normal", "embed", "bidi-override"] | typedefs.Inherit
    ] = None


class VectorEffectAttr(common.Attr):
    vector_effect: models.Attr[
        Literal[
            "non-scaling-stroke",
            "non-scaling-size",
            "non-rotation",
            "fixed-position",
        ]
        | typedefs.None_
    ] = None


class VisibilityAttr(common.Attr):
    visibility: models.Attr[
        Literal["visible", "hidden", "collapse"] | typedefs.Inherit
    ] = None


class WhiteSpaceAttr(common.Attr):
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


class WordSpacingAttr(common.Attr):
    word_spacing: models.Attr[
        Literal["normal"] | typedefs.Length | typedefs.Inherit
    ] = None


class WritingModeAttr(common.Attr):
    writing_mode: models.Attr[
        Literal["lr-tb", "rl-tb", "tb-rl", "lr", "rl", "tb"]
        | typedefs.Inherit
    ] = None
