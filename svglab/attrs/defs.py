from svglab import models
from svglab.attrs import types


class _AttrBase(models.BaseModel):
    pass


class Common(_AttrBase):
    """Common attributes shared by all SVG elements."""

    id: models.Attr[types.Id] = None
    xml_base: models.Attr[types.XmlBase] = None
    xml_lang: models.Attr[types.XmlLang] = None
    xml_space: models.Attr[types.XmlSpace] = None


class Points(_AttrBase):
    points: models.Attr[types.Points] = None


class CenterPoints(_AttrBase):
    cx: models.Attr[types.Cx] = None
    cy: models.Attr[types.Cy] = None


class WidthHeight(_AttrBase):
    width: models.Attr[types.Width] = None
    height: models.Attr[types.Height] = None


class PathData(_AttrBase):
    d: models.Attr[types.D] = None


class Radius(_AttrBase):
    r: models.Attr[types.R] = None


class RadiusXY(_AttrBase):
    rx: models.Attr[types.Rx] = None
    ry: models.Attr[types.Ry] = None


class Transform(_AttrBase):
    transform: models.Attr[types.Transform] = None


class Presentation(_AttrBase):
    opacity: models.Attr[types.Opacity] = None
    fill: models.Attr[types.Fill] = None
    fill_opacity: models.Attr[types.FillOpacity] = None
    stroke: models.Attr[types.Stroke] = None
    stroke_opacity: models.Attr[types.StrokeOpacity] = None
    stroke_width: models.Attr[types.StrokeWidth] = None
    stroke_linecap: models.Attr[types.StrokeLinecap] = None
    stroke_linejoin: models.Attr[types.StrokeLinejoin] = None
    stroke_dasharray: models.Attr[types.StrokeDasharray] = None
    stroke_dashoffset: models.Attr[types.StrokeDashoffset] = None
