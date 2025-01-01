from svglab.attrs import presentation, regular


class Common(
    regular.Id, regular.XmlBase, regular.XmlLang, regular.XmlSpace
):
    pass


class CxCy(regular.Cx, regular.Cy):
    pass


class WidthHeight(regular.Width, regular.Height):
    pass


class RxRy(regular.Rx, regular.Ry):
    pass


class CommonPresentation(
    presentation.Opacity,
    regular.Fill,  # TODO: Change to presentation.Fill
    presentation.FillOpacity,
    presentation.Stroke,
    presentation.StrokeOpacity,
    presentation.StrokeWidth,
    presentation.StrokeLinecap,
    presentation.StrokeLinejoin,
    presentation.StrokeDasharray,
    presentation.StrokeDashoffset,
):
    pass
