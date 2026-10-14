"""Groups of attributes that are commonly used together."""

from svglab.attrs.attrdefs import (
    AccumulateAttr,
    AdditiveAttr,
    AlignmentBaselineAttr,
    AmplitudeAttr,
    AttributeNameAttr,
    AttributeTypeAttr,
    BaselineShiftAttr,
    BeginAttr,
    ByAttr,
    CalcModeAttr,
    ClipAttr,
    ClipPathAttr,
    ClipRuleAttr,
    ColorAttr,
    ColorInterpolationAttr,
    ColorInterpolationFiltersAttr,
    ColorProfileAttr,
    ColorRenderingAttr,
    CursorAttr,
    DirectionAttr,
    DisplayAttr,
    DominantBaselineAttr,
    DurAttr,
    EnableBackgroundAttr,
    EndAttr,
    ExponentAttr,
    FillAttr,
    FillOpacityAttr,
    FillRuleAttr,
    FilterAttr,
    FloodColorAttr,
    FloodOpacityAttr,
    FontFamilyAttr,
    FontSizeAdjustAttr,
    FontSizeAttr,
    FontStretchAttr,
    FontStyleAttr,
    FontVariantAttr,
    FontWeightAttr,
    FromAttr,
    GlyphOrientationHorizontalAttr,
    GlyphOrientationVerticalAttr,
    HeightAttr,
    HrefAttr,
    IdAttr,
    ImageRenderingAttr,
    InterceptAttr,
    KerningAttr,
    KeySplinesAttr,
    KeyTimesAttr,
    LangAttr,
    LetterSpacingAttr,
    LightingColorAttr,
    MarkerEndAttr,
    MarkerMidAttr,
    MarkerStartAttr,
    MaskAttr,
    MaxAttr,
    MinAttr,
    OffsetNumberAttr,
    OnAbortAttr,
    OnActivateAttr,
    OnBeginAttr,
    OnClickAttr,
    OnEndAttr,
    OnErrorAttr,
    OnFocusInAttr,
    OnFocusOutAttr,
    OnLoadAttr,
    OnMouseDownAttr,
    OnMouseMoveAttr,
    OnMouseOutAttr,
    OnMouseOverAttr,
    OnMouseUpAttr,
    OnRepeatAttr,
    OnResizeAttr,
    OnScrollAttr,
    OnUnloadAttr,
    OnZoomAttr,
    OpacityAttr,
    OverflowAttr,
    PaintOrderAttr,
    PointerEventsAttr,
    RepeatCountAttr,
    RepeatDurAttr,
    RequiredExtensionsAttr,
    RequiredFeaturesAttr,
    RestartAttr,
    ResultAttr,
    ShapeRenderingAttr,
    SlopeAttr,
    StopColorAttr,
    StopOpacityAttr,
    StrokeAttr,
    StrokeDasharrayAttr,
    StrokeDashoffsetAttr,
    StrokeLinecapAttr,
    StrokeLinejoinAttr,
    StrokeMiterlimitAttr,
    StrokeOpacityAttr,
    StrokeWidthAttr,
    SystemLanguageAttr,
    TableValuesAttr,
    TextAlignAllAttr,
    TextAlignAttr,
    TextAlignLastAttr,
    TextAnchorAttr,
    TextDecorationAttr,
    TextIndentAttr,
    TextRenderingAttr,
    ToAttr,
    TransformAttr,
    TransformOriginAttr,
    TypeFeFuncAttr,
    UnicodeBidiAttr,
    ValuesListAttr,
    VectorEffectAttr,
    VisibilityAttr,
    WhiteSpaceAttr,
    WidthAttr,
    WordSpacingAttr,
    WritingModeAttr,
    XCoordinateAttr,
    XlinkActuateOnLoadAttr,
    XlinkArcroleAttr,
    XlinkHrefAttr,
    XlinkRoleAttr,
    XlinkShowAttr,
    XlinkTitleAttr,
    XlinkTypeAttr,
    XmlBaseAttr,
    XmlLangAttr,
    XmlSpaceAttr,
    YCoordinateAttr,
)


class CoreAttrs(IdAttr, LangAttr, XmlBaseAttr, XmlLangAttr, XmlSpaceAttr):
    """The core attributes.

    From the SVG 1.1 specification:
    > "The core attributes are those attributes that can be specified on any
    SVG element."
    """


class PresentationAttrs(
    AlignmentBaselineAttr,
    BaselineShiftAttr,
    ClipAttr,
    ClipPathAttr,
    ClipRuleAttr,
    ColorAttr,
    ColorInterpolationAttr,
    ColorInterpolationFiltersAttr,
    ColorProfileAttr,
    ColorRenderingAttr,
    CursorAttr,
    DirectionAttr,
    DisplayAttr,
    DominantBaselineAttr,
    EnableBackgroundAttr,
    FillAttr,
    FillOpacityAttr,
    FillRuleAttr,
    FilterAttr,
    FloodColorAttr,
    FloodOpacityAttr,
    FontFamilyAttr,
    FontSizeAdjustAttr,
    FontSizeAttr,
    FontStretchAttr,
    FontStyleAttr,
    FontVariantAttr,
    FontWeightAttr,
    GlyphOrientationHorizontalAttr,
    GlyphOrientationVerticalAttr,
    ImageRenderingAttr,
    KerningAttr,
    LetterSpacingAttr,
    LightingColorAttr,
    MarkerEndAttr,
    MarkerMidAttr,
    MarkerStartAttr,
    MaskAttr,
    OpacityAttr,
    OverflowAttr,
    PaintOrderAttr,
    PointerEventsAttr,
    ShapeRenderingAttr,
    StopColorAttr,
    StopOpacityAttr,
    StrokeAttr,
    StrokeDasharrayAttr,
    StrokeDashoffsetAttr,
    StrokeLinecapAttr,
    StrokeLinejoinAttr,
    StrokeMiterlimitAttr,
    StrokeOpacityAttr,
    StrokeWidthAttr,
    TextAlignAllAttr,
    TextAlignAttr,
    TextAlignLastAttr,
    TextAnchorAttr,
    TextDecorationAttr,
    TextIndentAttr,
    TextRenderingAttr,
    TransformAttr,
    TransformOriginAttr,
    UnicodeBidiAttr,
    VectorEffectAttr,
    VisibilityAttr,
    WhiteSpaceAttr,
    WordSpacingAttr,
    WritingModeAttr,
):
    """The presentation attributes.

    From the SVG 1.1 specification:
    > "An XML attribute on an SVG element which specifies a value for a given
    property for that element."
    """


class AnimationEventsAttrs(
    OnBeginAttr, OnEndAttr, OnLoadAttr, OnRepeatAttr
):
    """The animation event attributes.

    From the SVG 1.1 specification:
    > "An animation event attribute is an event attribute that specifies script
    to run for a particular animation-related event."
    """


class AnimationAttributeTargetAttrs(AttributeNameAttr, AttributeTypeAttr):
    """The animation attribute target attributes.

    From the SVG 1.1 specification:
    > "[...] identify the target attribute or property for the given target
    element whose value changes over time."

    """


class AnimationTimingAttrs(
    BeginAttr,
    DurAttr,
    EndAttr,
    FillAttr,
    MaxAttr,
    MinAttr,
    RepeatCountAttr,
    RepeatDurAttr,
    RestartAttr,
):
    """The animation timing attributes.

    From the SVG 1.1 specification:
    > "They are common to all animation elements and control the timing of the
    animation, including what causes the animation to start and end, whether
    the animation runs repeatedly, and whether to retain the end state the
    animation once the animation ends."
    """


class AnimationValueAttrs(
    ByAttr,
    CalcModeAttr,
    FromAttr,
    KeySplinesAttr,
    KeyTimesAttr,
    ToAttr,
    ValuesListAttr,
):
    """The animation value attributes.

    From the SVG 1.1 specification:
    > "They are common to elements `animate`, `animateColor`, `animateMotion`
    and `animateTransform`. These attributes define the values that are
    assigned to the target attribute or property over time. The attributes
    [...] provide control over the relative timing of keyframes and the
    interpolation method between discrete values."
    """


class AnimationAdditionAttrs(AccumulateAttr, AdditiveAttr):
    """The animation addition attributes.

    From the SVG 1.1 specification:
    > "[...] are common to elements `animate`, `animateColor`, `animateMotion`
    and `animateTransform`."
    """


class ConditionalProcessingAttrs(
    RequiredFeaturesAttr, RequiredExtensionsAttr, SystemLanguageAttr
):
    """The conditional processing attributes.

    From the SVG 1.1 specification:
    > "A conditional processing attribute is one that controls whether or not
    the element on which it appears is processed. Most elements, but not all,
    may have conditional processing attributes specified on them."
    """


class DocumentEventsAttrs(
    OnAbortAttr,
    OnErrorAttr,
    OnResizeAttr,
    OnScrollAttr,
    OnUnloadAttr,
    OnZoomAttr,
):
    """The document event attributes.

    From the SVG 1.1 specification:
    > "A document event attribute is an event attribute that specifies script
    to run for a particular document-wide event."
    """


class GraphicalEventsAttrs(
    OnActivateAttr,
    OnClickAttr,
    OnFocusInAttr,
    OnFocusOutAttr,
    OnLoadAttr,
    OnMouseDownAttr,
    OnMouseMoveAttr,
    OnMouseOutAttr,
    OnMouseOverAttr,
    OnMouseUpAttr,
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
    XCoordinateAttr, YCoordinateAttr, WidthAttr, HeightAttr, ResultAttr
):
    """The filter primitive attributes.

    From the SVG 1.1 specification:
    > "The filter primitive attributes is the set of attributes that are common
    to all filter primitive elements."
    """


class XlinkAttrs(
    HrefAttr,
    XlinkActuateOnLoadAttr,
    XlinkArcroleAttr,
    XlinkHrefAttr,
    XlinkRoleAttr,
    XlinkShowAttr,
    XlinkTitleAttr,
    XlinkTypeAttr,
):
    """The XLink attributes.

    From the SVG 1.1 specification:
    > "The XLink attributes are the seven attributes defined in the XML Linking
    Language specification, which are used on various SVG elements that can
    reference resources."
    """


class TransferFunctionAttrs(
    AmplitudeAttr,
    ExponentAttr,
    InterceptAttr,
    OffsetNumberAttr,
    SlopeAttr,
    TableValuesAttr,
    TypeFeFuncAttr,
):
    """The transfer function attributes.

    From the SVG 1.1 specification:
    > "[...] apply to sub-elements `feFuncR`, `feFuncG`, `feFuncB` and
    `feFuncA` that define the transfer functions."
    """
