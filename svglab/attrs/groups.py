"""Groups of attributes that are commonly used together."""

from svglab.attrs import common, presentation, regular


class CoreAttrs(
    regular.IdAttr,
    regular.LangAttr,
    regular.XmlBaseAttr,
    regular.XmlLangAttr,
    regular.XmlSpaceAttr,
):
    """The core attributes.

    From the SVG 1.1 specification:
    > "The core attributes are those attributes that can be specified on any
    SVG element."
    """


class PresentationAttrs(
    common.FillAttr,
    common.FontFamilyAttr,
    common.FontSizeAttr,
    common.FontStretchAttr,
    common.FontStyleAttr,
    common.FontVariantAttr,
    common.FontWeightAttr,
    presentation.BaselineShiftAttr,
    presentation.ClipPathAttr,
    presentation.ClipRuleAttr,
    presentation.ColorAttr,
    presentation.ColorInterpolationAttr,
    presentation.ColorInterpolationFiltersAttr,
    presentation.ColorProfileAttr,
    presentation.ColorRenderingAttr,
    presentation.CursorAttr,
    presentation.DirectionAttr,
    presentation.DisplayAttr,
    presentation.DominantBaselineAttr,
    presentation.FillOpacityAttr,
    presentation.FillRuleAttr,
    presentation.FontSizeAdjustAttr,
    presentation.GlyphOrientationHorizontalAttr,
    presentation.GlyphOrientationVerticalAttr,
    presentation.ImageRenderingAttr,
    presentation.KerningAttr,
    presentation.LetterSpacingAttr,
    presentation.MarkerEndAttr,
    presentation.MarkerMidAttr,
    presentation.MarkerStartAttr,
    presentation.MaskAttr,
    presentation.OpacityAttr,
    presentation.OverflowAttr,
    presentation.PaintOrderAttr,
    presentation.PointerEventsAttr,
    presentation.ShapeRenderingAttr,
    presentation.StopColorAttr,
    presentation.StopOpacityAttr,
    presentation.StrokeAttr,
    presentation.StrokeDasharrayAttr,
    presentation.StrokeDashoffsetAttr,
    presentation.StrokeLinecapAttr,
    presentation.StrokeLinejoinAttr,
    presentation.StrokeMiterlimitAttr,
    presentation.StrokeOpacityAttr,
    presentation.StrokeWidthAttr,
    presentation.TextAlignAttr,
    presentation.TextAlignAllAttr,
    presentation.TextAlignLastAttr,
    presentation.TextAnchorAttr,
    presentation.TextDecorationAttr,
    presentation.TextIndentAttr,
    presentation.TextRenderingAttr,
    presentation.TransformAttr,
    presentation.TransformOriginAttr,
    presentation.UnicodeBidiAttr,
    presentation.VectorEffectAttr,
    presentation.VisibilityAttr,
    presentation.WhiteSpaceAttr,
    presentation.WordSpacingAttr,
    presentation.WritingModeAttr,
):
    """The presentation attributes.

    From the SVG 1.1 specification:
    > "An XML attribute on an SVG element which specifies a value for a given
    property for that element."
    """


class AnimationEventsAttrs(
    regular.OnBeginAttr,
    regular.OnEndAttr,
    regular.OnLoadAttr,
    regular.OnRepeatAttr,
):
    """The animation event attributes.

    From the SVG 1.1 specification:
    > "An animation event attribute is an event attribute that specifies script
    to run for a particular animation-related event."
    """


class AnimationAttributeTargetAttrs(
    regular.AttributeNameAttr, regular.AttributeTypeAttr
):
    """The animation attribute target attributes.

    From the SVG 1.1 specification:
    > "[...] identify the target attribute or property for the given target
    element whose value changes over time."

    """


class AnimationTimingAttrs(
    regular.BeginAttr,
    regular.DurAttr,
    regular.EndAttr,
    common.FillAttr,
    regular.MaxAttr,
    regular.MinAttr,
    regular.RepeatCountAttr,
    regular.RepeatDurAttr,
    regular.RestartAttr,
):
    """The animation timing attributes.

    From the SVG 1.1 specification:
    > "They are common to all animation elements and control the timing of the
    animation, including what causes the animation to start and end, whether
    the animation runs repeatedly, and whether to retain the end state the
    animation once the animation ends."
    """


class AnimationValueAttrs(
    regular.ByAttr,
    regular.CalcModeAttr,
    regular.FromAttr,
    regular.KeySplinesAttr,
    regular.KeyTimesAttr,
    regular.ToAttr,
    regular.ValuesListAttr,
):
    """The animation value attributes.

    From the SVG 1.1 specification:
    > "They are common to elements `animate`, `animateColor`, `animateMotion`
    and `animateTransform`. These attributes define the values that are
    assigned to the target attribute or property over time. The attributes
    [...] provide control over the relative timing of keyframes and the
    interpolation method between discrete values."
    """


class AnimationAdditionAttrs(regular.AccumulateAttr, regular.AdditiveAttr):
    """The animation addition attributes.

    From the SVG 1.1 specification:
    > "[...] are common to elements `animate`, `animateColor`, `animateMotion`
    and `animateTransform`."
    """


class ConditionalProcessingAttrs(
    regular.RequiredFeaturesAttr,
    regular.RequiredExtensionsAttr,
    regular.SystemLanguageAttr,
):
    """The conditional processing attributes.

    From the SVG 1.1 specification:
    > "A conditional processing attribute is one that controls whether or not
    the element on which it appears is processed. Most elements, but not all,
    may have conditional processing attributes specified on them."
    """


class DocumentEventsAttrs(
    regular.OnAbortAttr,
    regular.OnErrorAttr,
    regular.OnResizeAttr,
    regular.OnScrollAttr,
    regular.OnUnloadAttr,
    regular.OnZoomAttr,
):
    """The document event attributes.

    From the SVG 1.1 specification:
    > "A document event attribute is an event attribute that specifies script
    to run for a particular document-wide event."
    """


class GraphicalEventsAttrs(
    regular.OnActivateAttr,
    regular.OnClickAttr,
    regular.OnFocusInAttr,
    regular.OnFocusOutAttr,
    regular.OnLoadAttr,
    regular.OnMouseDownAttr,
    regular.OnMouseMoveAttr,
    regular.OnMouseOutAttr,
    regular.OnMouseOverAttr,
    regular.OnMouseUpAttr,
):
    """The graphical event attributes.

    From the SVG 1.1 specification:
    > "A graphical event attribute is an event attribute that specifies script
    to run for a particular user interaction event."
    """


class EventAttrs(
    GraphicalEventsAttrs, AnimationEventsAttrs, DocumentEventsAttrs
):
    """All event attributes."""


class FilterPrimitivesAttrs(
    regular.XCoordinateAttr,
    regular.YCoordinateAttr,
    regular.WidthAttr,
    regular.HeightAttr,
    regular.ResultAttr,
):
    """The filter primitive attributes.

    From the SVG 1.1 specification:
    > "The filter primitive attributes is the set of attributes that are common
    to all filter primitive elements."
    """


class XlinkAttrs(
    regular.HrefAttr,
    regular.XlinkActuateOnLoadAttr,
    regular.XlinkArcroleAttr,
    regular.XlinkHrefAttr,
    regular.XlinkRoleAttr,
    regular.XlinkShowAttr,
    regular.XlinkTitleAttr,
    regular.XlinkTypeAttr,
):
    """The XLink attributes.

    From the SVG 1.1 specification:
    > "The XLink attributes are the seven attributes defined in the XML Linking
    Language specification, which are used on various SVG elements that can
    reference resources."
    """


class TransferFunctionAttrs(
    regular.AmplitudeAttr,
    regular.ExponentAttr,
    regular.InterceptAttr,
    regular.OffsetNumberAttr,
    regular.SlopeAttr,
    regular.TableValuesAttr,
    regular.TypeFeFuncAttr,
):
    """The transfer function attributes.

    From the SVG 1.1 specification:
    > "[...] apply to sub-elements `feFuncR`, `feFuncG`, `feFuncB` and
    `feFuncA` that define the transfer functions."
    """
