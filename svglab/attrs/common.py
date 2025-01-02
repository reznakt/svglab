from typing import Literal

from svglab import models
from svglab.attrs import types


class Attr(models.BaseModel):
    pass


# definitions of attributes that are both regular and presentation attributes
# are merged together; this is a bit of a hack
# TODO: figure out how the standard intends us to handle this


class FontWeight(Attr):
    font_weight: models.Attr[
        types.All
        | models.List[
            Literal[
                "normal",
                "bold",
                "bolder",
                "lighter",
                100,
                200,
                300,
                400,
                500,
                600,
                700,
                800,
                900,
            ]
        ]
        | types.Inherit
    ] = None


class FontStretch(Attr):
    font_stretch: models.Attr[
        types.All
        | Literal[
            "condensed ",
            "condensed",
            "expanded",
            "extra-condensed",
            "extra-expanded",
            "narrower",
            "normal",
            "semi-condensed",
            "semi-expanded",
            "ultra-condensed",
            "ultra-expanded",
            "wider",
        ]
        | types.Inherit
    ] = None


class FontStyle(Attr):
    font_style: models.Attr[
        types.All
        | models.List[Literal["normal", "italic", "oblique"]]
        | types.Inherit
    ] = None


class FontVariant(Attr):
    font_variant: models.Attr[
        Literal["normal", "small-caps"] | types.Inherit
    ] = None


class Fill(Attr):
    fill: models.Attr[types.Paint | Literal["freeze", "remove"]] = None
