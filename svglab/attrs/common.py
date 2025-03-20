from typing_extensions import Literal

from svglab import models
from svglab.attrs import typedefs


class Attr(models.BaseModel):
    pass


# definitions of attributes that are both regular and presentation attributes
# are merged together; this is a bit of a hack
# TODO: figure out how the standard intends us to handle this


class FontWeight(Attr):
    font_weight: models.Attr[
        typedefs.All
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
        | typedefs.Inherit
    ] = None


class FontStretch(Attr):
    font_stretch: models.Attr[
        typedefs.All
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
        | typedefs.Inherit
    ] = None


class FontStyle(Attr):
    font_style: models.Attr[
        typedefs.All
        | models.List[Literal["normal", "italic", "oblique"]]
        | typedefs.Inherit
    ] = None


class FontVariant(Attr):
    font_variant: models.Attr[
        Literal["normal", "small-caps"] | typedefs.Inherit
    ] = None


class FontSize(Attr):
    font_size: models.Attr[
        typedefs.AbsoluteSize
        | typedefs.RelativeSize
        | typedefs.Length
        | typedefs.Percentage
        | typedefs.Inherit
        | typedefs.All
        | typedefs.ListOfLengths
    ] = None


class Fill(Attr):
    fill: models.Attr[typedefs.Paint | Literal["freeze", "remove"]] = None
