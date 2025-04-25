"""Groups of attributes that are commonly used together."""

from svglab.attrs import common, presentation, regular


class Core(
    regular.Id,
    regular.Lang,
    regular.XmlBase,
    regular.XmlLang,
    regular.XmlSpace,
):
    """The core attributes.

    From the SVG 1.1 specification:
    > "The core attributes are those attributes that can be specified on any
    SVG element."
    """


class Presentation(
    common.Fill,
    common.FontFamily,
    common.FontSize,
    common.FontStretch,
    common.FontStyle,
    common.FontVariant,
    common.FontWeight,
    presentation.BaselineShift,
    presentation.ClipPath,
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
    presentation.TextAlign,
    presentation.TextAlignAll,
    presentation.TextAlignLast,
    presentation.TextAnchor,
    presentation.TextDecoration,
    presentation.TextIndent,
    presentation.TextRendering,
    presentation.Transform,
    presentation.TransformOrigin,
    presentation.UnicodeBidi,
    presentation.VectorEffect,
    presentation.Visibility,
    presentation.WhiteSpace,
    presentation.WordSpacing,
    presentation.WritingMode,
):
    """The presentation attributes.

    From the SVG 1.1 specification:
    > "An XML attribute on an SVG element which specifies a value for a given
    property for that element."
    """


class AnimationEvents(
    regular.OnBegin, regular.OnEnd, regular.OnLoad, regular.OnRepeat
):
    """The animation event attributes.

    From the SVG 1.1 specification:
    > "An animation event attribute is an event attribute that specifies script
    to run for a particular animation-related event."
    """


class AnimationAttributeTarget(
    regular.AttributeName, regular.AttributeType
):
    """The animation attribute target attributes.

    From the SVG 1.1 specification:
    > "[...] identify the target attribute or property for the given target
    element whose value changes over time."

    """


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
    """The animation timing attributes.

    From the SVG 1.1 specification:
    > "They are common to all animation elements and control the timing of the
    animation, including what causes the animation to start and end, whether
    the animation runs repeatedly, and whether to retain the end state the
    animation once the animation ends."
    """


class AnimationValue(
    regular.By,
    regular.CalcMode,
    regular.From,
    regular.KeySplines,
    regular.KeyTimes,
    regular.To,
    regular.ValuesList,
):
    """The animation value attributes.

    From the SVG 1.1 specification:
    > "They are common to elements `animate`, `animateColor`, `animateMotion`
    and `animateTransform`. These attributes define the values that are
    assigned to the target attribute or property over time. The attributes
    [...] provide control over the relative timing of keyframes and the
    interpolation method between discrete values."
    """


class AnimationAddition(regular.Accumulate, regular.Additive):
    """The animation addition attributes.

    From the SVG 1.1 specification:
    > "[...] are common to elements `animate`, `animateColor`, `animateMotion`
    and `animateTransform`."
    """


class ConditionalProcessing(
    regular.RequiredFeatures,
    regular.RequiredExtensions,
    regular.SystemLanguage,
):
    """The conditional processing attributes.

    From the SVG 1.1 specification:
    > "A conditional processing attribute is one that controls whether or not
    the element on which it appears is processed. Most elements, but not all,
    may have conditional processing attributes specified on them."
    """


class DocumentEvents(
    regular.OnAbort,
    regular.OnError,
    regular.OnResize,
    regular.OnScroll,
    regular.OnUnload,
    regular.OnZoom,
):
    """The document event attributes.

    From the SVG 1.1 specification:
    > "A document event attribute is an event attribute that specifies script
    to run for a particular document-wide event."
    """


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
    """The graphical event attributes.

    From the SVG 1.1 specification:
    > "A graphical event attribute is an event attribute that specifies script
    to run for a particular user interaction event."
    """


class Event(GraphicalEvents, AnimationEvents, DocumentEvents):
    """All event attributes."""


class FilterPrimitives(
    regular.XCoordinate,
    regular.YCoordinate,
    regular.Width,
    regular.Height,
    regular.Result,
):
    """The filter primitive attributes.

    From the SVG 1.1 specification:
    > "The filter primitive attributes is the set of attributes that are common
    to all filter primitive elements."
    """


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
    """The XLink attributes.

    From the SVG 1.1 specification:
    > "The XLink attributes are the seven attributes defined in the XML Linking
    Language specification, which are used on various SVG elements that can
    reference resources."
    """


class TransferFunction(
    regular.Amplitude,
    regular.Exponent,
    regular.Intercept,
    regular.OffsetNumber,
    regular.Slope,
    regular.TableValues,
    regular.TypeFeFunc,
):
    """The transfer function attributes.

    From the SVG 1.1 specification:
    > "[...] apply to sub-elements `feFuncR`, `feFuncG`, `feFuncB` and
    `feFuncA` that define the transfer functions."
    """
