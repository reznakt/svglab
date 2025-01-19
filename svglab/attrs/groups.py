from svglab.attrs import common, presentation, regular


class Core(
    regular.Id,
    regular.Lang,
    regular.XmlBase,
    regular.XmlLang,
    regular.XmlSpace,
):
    pass


class Presentation(
    common.Fill,
    common.FontStretch,
    common.FontStyle,
    common.FontVariant,
    common.FontWeight,
    presentation.BaselineShift,
    presentation.ClipRule,
    presentation.Color,
    presentation.ColorInterpolation,
    presentation.ColorInterpolationFilters,
    presentation.ColorProfile,
    presentation.ColorRendering,
    presentation.Cursor,
    presentation.Direction,
    presentation.Display,
    presentation.DominantBaseline,
    presentation.FillOpacity,
    presentation.FillRule,
    presentation.FontSize,
    presentation.FontSizeAdjust,
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
    presentation.PaintOrder,
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
    presentation.VectorEffect,
    presentation.Visibility,
    presentation.WordSpacing,
    presentation.WritingMode,
    presentation.ZIndex,
):
    pass


class AnimationEvents(
    regular.OnBegin, regular.OnEnd, regular.OnLoad, regular.OnRepeat
):
    pass


class AnimationAttributeTarget(
    regular.AttributeName, regular.AttributeType
):
    pass


class AnimationTiming(
    regular.Begin,
    regular.Dur,
    regular.End,
    common.Fill,
    regular.Max,
    regular.Min,
    regular.RepeatCount,
    regular.RepeatDur,
    regular.Restart,
):
    pass


class AnimationValue(
    regular.By,
    regular.CalcMode,
    regular.From,
    regular.KeySplines,
    regular.KeyTimes,
    regular.To,
    regular.ValuesList,
):
    pass


class AnimationAddition(regular.Accumulate, regular.Additive):
    pass


class ConditionalProcessing(
    regular.RequiredFeatures,
    regular.RequiredExtensions,
    regular.SystemLanguage,
):
    pass


class DocumentEvents(
    regular.OnAbort,
    regular.OnError,
    regular.OnResize,
    regular.OnScroll,
    regular.OnUnload,
    regular.OnZoom,
):
    pass


class GraphicalEvents(
    regular.OnActivate,
    regular.OnClick,
    regular.OnFocusIn,
    regular.OnFocusOut,
    regular.OnLoad,
    regular.OnMouseDown,
    regular.OnMouseMove,
    regular.OnMouseOut,
    regular.OnMouseOver,
    regular.OnMouseUp,
):
    pass


class Event(GraphicalEvents, AnimationEvents, DocumentEvents):
    pass


class FilterPrimitives(
    regular.XCoordinate,
    regular.YCoordinate,
    regular.Width,
    regular.Height,
    regular.Result,
):
    pass


class Xlink(
    regular.Href,
    regular.XlinkActuateOnLoad,
    regular.XlinkArcrole,
    regular.XlinkHref,
    regular.XlinkRole,
    regular.XlinkShow,
    regular.XlinkTitle,
    regular.XlinkType,
):
    pass


class TransferFunction(
    regular.Amplitude,
    regular.Exponent,
    regular.Intercept,
    regular.OffsetNumber,
    regular.Slope,
    regular.TableValues,
    regular.TypeFeFunc,
):
    pass
