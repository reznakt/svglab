from importlib import metadata
from typing import Final

__version__: Final = metadata.version(__name__)

from .elements import (
    AnyElement,
    AnyTextElement,
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
    "AnyElement",
    "AnyTextElement",
    "CData",
    "Comment",
    "Element",
    "G",
    "Rect",
    "Svg",
    "Text",
    "TextElement",
    "parse_svg",
]
