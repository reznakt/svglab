import importlib.metadata
import typing

__version__: typing.Final = importlib.metadata.version(__name__)

from pydantic_extra_types.color import Color

from .elements import (
    CData,
    Comment,
    Element,
    G,
    Rect,
    Svg,
    Text,
    TextElement,
)
from .parse import parse_svg

__all__ = [
    "CData",
    "Color",
    "Comment",
    "Element",
    "G",
    "Rect",
    "Svg",
    "Text",
    "TextElement",
    "parse_svg",
]
