from svglab import models
from svglab.elements import attrtypes


class _AttrBase(models.BaseModel):
    pass


class Common(_AttrBase):
    """Common attributes shared by all SVG elements."""

    id: models.Attr[attrtypes.Id] = None
    xml_base: models.Attr[attrtypes.XmlBase] = None
    xml_lang: models.Attr[attrtypes.XmlLang] = None
    xml_space: models.Attr[attrtypes.XmlSpace] = None


class Points(_AttrBase):
    points: models.Attr[attrtypes.Points] = None


class CenterPoints(_AttrBase):
    cx: models.Attr[attrtypes.Cx] = None
    cy: models.Attr[attrtypes.Cy] = None


class WidthHeight(_AttrBase):
    width: models.Attr[attrtypes.Width] = None
    height: models.Attr[attrtypes.Height] = None


class PathData(_AttrBase):
    d: models.Attr[attrtypes.D] = None


class Radius(_AttrBase):
    r: models.Attr[attrtypes.R] = None


class RadiusXY(_AttrBase):
    rx: models.Attr[attrtypes.Rx] = None
    ry: models.Attr[attrtypes.Ry] = None


class Transform(_AttrBase):
    transform: models.Attr[attrtypes.Transform] = None


class Presentation(_AttrBase):
    opacity: models.Attr[attrtypes.Opacity] = None
    fill: models.Attr[attrtypes.Fill] = None
    fill_opacity: models.Attr[attrtypes.FillOpacity] = None
    stroke: models.Attr[attrtypes.Stroke] = None
    stroke_opacity: models.Attr[attrtypes.StrokeOpacity] = None
    stroke_width: models.Attr[attrtypes.StrokeWidth] = None
    stroke_linecap: models.Attr[attrtypes.StrokeLinecap] = None
    stroke_linejoin: models.Attr[attrtypes.StrokeLinejoin] = None
    stroke_dasharray: models.Attr[attrtypes.StrokeDasharray] = None
    stroke_dashoffset: models.Attr[attrtypes.StrokeDashoffset] = None
