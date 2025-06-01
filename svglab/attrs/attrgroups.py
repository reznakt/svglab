"""Groups of attributes that are commonly used together."""

from svglab.attrs import attrdefs


class CoreAttrs(
    attrdefs.IdAttr,
    attrdefs.LangAttr,
    attrdefs.XmlBaseAttr,
    attrdefs.XmlLangAttr,
    attrdefs.XmlSpaceAttr,
):
    """The core attributes.

    From the SVG 1.1 specification:
    > "The core attributes are those attributes that can be specified on any
    SVG element."
    """


class PresentationAttrs(
    attrdefs.AlignmentBaselineAttr,
    attrdefs.BaselineShiftAttr,
    attrdefs.ClipAttr,
    attrdefs.ClipPathAttr,
    attrdefs.ClipRuleAttr,
    attrdefs.ColorAttr,
    attrdefs.ColorInterpolationAttr,
    attrdefs.ColorInterpolationFiltersAttr,
    attrdefs.ColorProfileAttr,
    attrdefs.ColorRenderingAttr,
    attrdefs.CursorAttr,
    attrdefs.DirectionAttr,
    attrdefs.DisplayAttr,
    attrdefs.DominantBaselineAttr,
    attrdefs.EnableBackgroundAttr,
    attrdefs.FillAttr,
    attrdefs.FillOpacityAttr,
    attrdefs.FillRuleAttr,
    attrdefs.FilterAttr,
    attrdefs.FloodColorAttr,
    attrdefs.FloodOpacityAttr,
    attrdefs.FontFamilyAttr,
    attrdefs.FontSizeAdjustAttr,
    attrdefs.FontSizeAttr,
    attrdefs.FontStretchAttr,
    attrdefs.FontStyleAttr,
    attrdefs.FontVariantAttr,
    attrdefs.FontWeightAttr,
    attrdefs.GlyphOrientationHorizontalAttr,
    attrdefs.GlyphOrientationVerticalAttr,
    attrdefs.ImageRenderingAttr,
    attrdefs.KerningAttr,
    attrdefs.LetterSpacingAttr,
    attrdefs.LightingColorAttr,
    attrdefs.MarkerEndAttr,
    attrdefs.MarkerMidAttr,
    attrdefs.MarkerStartAttr,
    attrdefs.MaskAttr,
    attrdefs.OpacityAttr,
    attrdefs.OverflowAttr,
    attrdefs.PaintOrderAttr,
    attrdefs.PointerEventsAttr,
    attrdefs.ShapeRenderingAttr,
    attrdefs.StopColorAttr,
    attrdefs.StopOpacityAttr,
    attrdefs.StrokeAttr,
    attrdefs.StrokeDasharrayAttr,
    attrdefs.StrokeDashoffsetAttr,
    attrdefs.StrokeLinecapAttr,
    attrdefs.StrokeLinejoinAttr,
    attrdefs.StrokeMiterlimitAttr,
    attrdefs.StrokeOpacityAttr,
    attrdefs.StrokeWidthAttr,
    attrdefs.TextAlignAllAttr,
    attrdefs.TextAlignAttr,
    attrdefs.TextAlignLastAttr,
    attrdefs.TextAnchorAttr,
    attrdefs.TextDecorationAttr,
    attrdefs.TextIndentAttr,
    attrdefs.TextRenderingAttr,
    attrdefs.TransformAttr,
    attrdefs.TransformOriginAttr,
    attrdefs.UnicodeBidiAttr,
    attrdefs.VectorEffectAttr,
    attrdefs.VisibilityAttr,
    attrdefs.WhiteSpaceAttr,
    attrdefs.WordSpacingAttr,
    attrdefs.WritingModeAttr,
):
    """The presentation attributes.

    From the SVG 1.1 specification:
    > "An XML attribute on an SVG element which specifies a value for a given
    property for that element."
    """


class AnimationEventsAttrs(
    attrdefs.OnBeginAttr,
    attrdefs.OnEndAttr,
    attrdefs.OnLoadAttr,
    attrdefs.OnRepeatAttr,
):
    """The animation event attributes.

    From the SVG 1.1 specification:
    > "An animation event attribute is an event attribute that specifies script
    to run for a particular animation-related event."
    """


class AnimationAttributeTargetAttrs(
    attrdefs.AttributeNameAttr, attrdefs.AttributeTypeAttr
):
    """The animation attribute target attributes.

    From the SVG 1.1 specification:
    > "[...] identify the target attribute or property for the given target
    element whose value changes over time."

    """


class AnimationTimingAttrs(
    attrdefs.BeginAttr,
    attrdefs.DurAttr,
    attrdefs.EndAttr,
    attrdefs.FillAttr,
    attrdefs.MaxAttr,
    attrdefs.MinAttr,
    attrdefs.RepeatCountAttr,
    attrdefs.RepeatDurAttr,
    attrdefs.RestartAttr,
):
    """The animation timing attributes.

    From the SVG 1.1 specification:
    > "They are common to all animation elements and control the timing of the
    animation, including what causes the animation to start and end, whether
    the animation runs repeatedly, and whether to retain the end state the
    animation once the animation ends."
    """


class AnimationValueAttrs(
    attrdefs.ByAttr,
    attrdefs.CalcModeAttr,
    attrdefs.FromAttr,
    attrdefs.KeySplinesAttr,
    attrdefs.KeyTimesAttr,
    attrdefs.ToAttr,
    attrdefs.ValuesListAttr,
):
    """The animation value attributes.

    From the SVG 1.1 specification:
    > "They are common to elements `animate`, `animateColor`, `animateMotion`
    and `animateTransform`. These attributes define the values that are
    assigned to the target attribute or property over time. The attributes
    [...] provide control over the relative timing of keyframes and the
    interpolation method between discrete values."
    """


class AnimationAdditionAttrs(
    attrdefs.AccumulateAttr, attrdefs.AdditiveAttr
):
    """The animation addition attributes.

    From the SVG 1.1 specification:
    > "[...] are common to elements `animate`, `animateColor`, `animateMotion`
    and `animateTransform`."
    """


class ConditionalProcessingAttrs(
    attrdefs.RequiredFeaturesAttr,
    attrdefs.RequiredExtensionsAttr,
    attrdefs.SystemLanguageAttr,
):
    """The conditional processing attributes.

    From the SVG 1.1 specification:
    > "A conditional processing attribute is one that controls whether or not
    the element on which it appears is processed. Most elements, but not all,
    may have conditional processing attributes specified on them."
    """


class DocumentEventsAttrs(
    attrdefs.OnAbortAttr,
    attrdefs.OnErrorAttr,
    attrdefs.OnResizeAttr,
    attrdefs.OnScrollAttr,
    attrdefs.OnUnloadAttr,
    attrdefs.OnZoomAttr,
):
    """The document event attributes.

    From the SVG 1.1 specification:
    > "A document event attribute is an event attribute that specifies script
    to run for a particular document-wide event."
    """


class GraphicalEventsAttrs(
    attrdefs.OnActivateAttr,
    attrdefs.OnClickAttr,
    attrdefs.OnFocusInAttr,
    attrdefs.OnFocusOutAttr,
    attrdefs.OnLoadAttr,
    attrdefs.OnMouseDownAttr,
    attrdefs.OnMouseMoveAttr,
    attrdefs.OnMouseOutAttr,
    attrdefs.OnMouseOverAttr,
    attrdefs.OnMouseUpAttr,
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
    attrdefs.XCoordinateAttr,
    attrdefs.YCoordinateAttr,
    attrdefs.WidthAttr,
    attrdefs.HeightAttr,
    attrdefs.ResultAttr,
):
    """The filter primitive attributes.

    From the SVG 1.1 specification:
    > "The filter primitive attributes is the set of attributes that are common
    to all filter primitive elements."
    """


class XlinkAttrs(
    attrdefs.HrefAttr,
    attrdefs.XlinkActuateOnLoadAttr,
    attrdefs.XlinkArcroleAttr,
    attrdefs.XlinkHrefAttr,
    attrdefs.XlinkRoleAttr,
    attrdefs.XlinkShowAttr,
    attrdefs.XlinkTitleAttr,
    attrdefs.XlinkTypeAttr,
):
    """The XLink attributes.

    From the SVG 1.1 specification:
    > "The XLink attributes are the seven attributes defined in the XML Linking
    Language specification, which are used on various SVG elements that can
    reference resources."
    """


class TransferFunctionAttrs(
    attrdefs.AmplitudeAttr,
    attrdefs.ExponentAttr,
    attrdefs.InterceptAttr,
    attrdefs.OffsetNumberAttr,
    attrdefs.SlopeAttr,
    attrdefs.TableValuesAttr,
    attrdefs.TypeFeFuncAttr,
):
    """The transfer function attributes.

    From the SVG 1.1 specification:
    > "[...] apply to sub-elements `feFuncR`, `feFuncG`, `feFuncB` and
    `feFuncA` that define the transfer functions."
    """
