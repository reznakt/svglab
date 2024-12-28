from typing import Literal

from svglab import models
from svglab.elements import attrtypes


class AttrBase(models.BaseModel):
    pass


class Common(AttrBase):
    """Common attributes shared by all SVG elements."""

    id: models.Attr[attrtypes.Name] = None
    xml_base: models.Attr[attrtypes.Iri] = None
    xml_lang: models.Attr[attrtypes.LanguageId] = None
    xml_space: models.Attr[Literal["default", "preserve"]] = None


class Points(AttrBase):
    points: models.Attr[attrtypes.ListOfPoints] = None


class CenterPoints(AttrBase):
    cx: models.Attr[attrtypes.Coordinate] = None
    cy: models.Attr[attrtypes.Coordinate] = None


class WidthHeight(AttrBase):
    width: models.Attr[attrtypes.Length] = None
    height: models.Attr[attrtypes.Length] = None


class PathData(AttrBase):
    d: models.Attr[attrtypes.PathData] = None


class Radius(AttrBase):
    r: models.Attr[attrtypes.Length] = None


class RadiusXY(AttrBase):
    rx: models.Attr[attrtypes.Length] = None
    ry: models.Attr[attrtypes.Length] = None


class Transform(AttrBase):
    transform: models.Attr[attrtypes.TransformList] = None


class Presentation(AttrBase):
    opacity: models.Attr[attrtypes.OpacityValue] = None
    fill: models.Attr[attrtypes.Paint] = None
    fill_opacity: models.Attr[attrtypes.OpacityValue] = None
    stroke: models.Attr[attrtypes.Paint] = None
    stroke_opacity: models.Attr[attrtypes.OpacityValue] = None
    stroke_width: models.Attr[
        attrtypes.Length | attrtypes.Percentage | attrtypes.Inherit
    ] = None
    stroke_linecap: models.Attr[
        Literal["butt", "round", "square"] | attrtypes.Inherit
    ] = None
    stroke_linejoin: models.Attr[
        Literal["miter", "round", "bevel"] | attrtypes.Inherit
    ] = None
    stroke_dasharray: models.Attr[
        attrtypes.None_ | attrtypes.DashArray | attrtypes.Inherit
    ] = None
    stroke_dashoffset: models.Attr[
        attrtypes.Percentage | attrtypes.Length | attrtypes.Inherit
    ] = None
