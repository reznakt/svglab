from svglab.attrs import presentation, regular


class Core(regular.Id, regular.XmlBase, regular.XmlLang, regular.XmlSpace):
    pass


class Presentation(
    presentation.BaselineShift,
    presentation.ClipRule,
    presentation.ColorInterpolation,
    presentation.ColorInterpolationFilters,
    presentation.ColorProfile,
    presentation.ColorRendering,
    presentation.Cursor,
    presentation.Direction,
    presentation.Display,
    presentation.DominantBaseline,
    presentation.Fill,
    presentation.FillOpacity,
    presentation.FillRule,
    presentation.FontSize,
    presentation.FontSizeAdjust,
    presentation.FontStretch,
    presentation.FontStyle,
    presentation.FontVariant,
    presentation.FontWeight,
    presentation.GlyphOrientationHorizontal,
    presentation.GlyphOrientationVertical,
    presentation.ImageRendering,
    presentation.Kerning,
    presentation.LetterSpacing,
    presentation.MarkerEnd,
    presentation.MarkerMid,
    presentation.MarkerStart,
    presentation.Mask,
    presentation.Opacity,
    presentation.Overflow,
    presentation.PointerEvents,
    presentation.ShapeRendering,
    presentation.StopColor,
    presentation.StopOpacity,
    presentation.Stroke,
    presentation.StrokeDasharray,
    presentation.StrokeDashoffset,
    presentation.StrokeLinecap,
    presentation.StrokeLinejoin,
    presentation.StrokeMiterlimit,
    presentation.StrokeOpacity,
    presentation.StrokeWidth,
    presentation.TextAnchor,
    presentation.TextDecoration,
    presentation.TextRendering,
    presentation.UnicodeBidi,
    presentation.Visibility,
    presentation.WordSpacing,
    presentation.WritingMode,
):
    pass


class AnimationEvent(regular.OnBegin, regular.OnEnd, regular.OnRepeat):
    pass


class ConditionalProcessing(
    regular.RequiredFeatures,
    regular.RequiredExtensions,
    regular.SystemLanguage,
):
    pass


class DocumentEvent(
    regular.OnAbort,
    regular.OnError,
    regular.OnResize,
    regular.OnScroll,
    regular.OnUnload,
    regular.OnZoom,
):
    pass


class GraphicalEvent(
    regular.OnFocusIn,
    regular.OnFocusOut,
    regular.OnActivate,
    regular.OnClick,
    regular.OnMouseDown,
    regular.OnMouseUp,
    regular.OnMouseOver,
    regular.OnMouseMove,
    regular.OnMouseOut,
):
    pass


class Event(GraphicalEvent, AnimationEvent, DocumentEvent):
    pass


class FilterPrimitive(
    regular.XCoordinate,
    regular.YCoordinate,
    regular.Width,
    regular.Height,
    regular.Result,
):
    pass


class CxCy(regular.Cx, regular.Cy):
    pass


class WidthHeight(regular.Width, regular.Height):
    pass


class RxRy(regular.Rx, regular.Ry):
    pass
