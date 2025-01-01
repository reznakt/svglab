from svglab import models
from svglab.attrs import presentation, regular


class _AttrBase(models.BaseModel):
    pass


class Common(_AttrBase):
    """Common attributes shared by all SVG elements."""

    id: models.Attr[regular.Id] = None
    xml_base: models.Attr[regular.XmlBase] = None
    xml_lang: models.Attr[regular.XmlLang] = None
    xml_space: models.Attr[regular.XmlSpace] = None


class Points(_AttrBase):
    points: models.Attr[regular.Points] = None


class CenterPoints(_AttrBase):
    cx: models.Attr[regular.Cx] = None
    cy: models.Attr[regular.Cy] = None


class WidthHeight(_AttrBase):
    width: models.Attr[regular.Width] = None
    height: models.Attr[regular.Height] = None


class PathData(_AttrBase):
    d: models.Attr[regular.D] = None


class Radius(_AttrBase):
    r: models.Attr[regular.R] = None


class RadiusXY(_AttrBase):
    rx: models.Attr[regular.Rx] = None
    ry: models.Attr[regular.Ry] = None


class Transform(_AttrBase):
    transform: models.Attr[regular.Transform] = None


class Presentation(_AttrBase):
    opacity: models.Attr[presentation.Opacity] = None
    fill: models.Attr[regular.Fill] = (
        None  # TODO: Change to presentation.Fill
    )
    fill_opacity: models.Attr[presentation.FillOpacity] = None
    stroke: models.Attr[presentation.Stroke] = None
    stroke_opacity: models.Attr[presentation.StrokeOpacity] = None
    stroke_width: models.Attr[presentation.StrokeWidth] = None
    stroke_linecap: models.Attr[presentation.StrokeLinecap] = None
    stroke_linejoin: models.Attr[presentation.StrokeLinejoin] = None
    stroke_dasharray: models.Attr[presentation.StrokeDasharray] = None
    stroke_dashoffset: models.Attr[presentation.StrokeDashoffset] = None
