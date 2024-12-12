import typing
from typing import Final, Literal, TypeAlias

import bidict

__all__ = [
    "TAG_NAMES",
    "TAG_NAME_TO_NORMALIZED",
    "TagName",
]

TagName: TypeAlias = Literal[
    "a",
    "altGlyph",
    "altGlyphDef",
    "altGlyphItem",
    "animate",
    "animateColor",
    "animateMotion",
    "animateTransform",
    "circle",
    "clipPath",
    "color-profile",
    "cursor",
    "defs",
    "desc",
    "ellipse",
    "feBlend",
    "feColorMatrix",
    "feComponentTransfer",
    "feComposite",
    "feConvolveMatrix",
    "feDiffuseLighting",
    "feDisplacementMap",
    "feDistantLight",
    "feFlood",
    "feFuncA",
    "feFuncB",
    "feFuncG",
    "feFuncR",
    "feGaussianBlur",
    "feImage",
    "feMerge",
    "feMergeNode",
    "feMorphology",
    "feOffset",
    "fePointLight",
    "feSpecularLighting",
    "feSpotLight",
    "feTile",
    "feTurbulence",
    "filter",
    "font-face-format",
    "font-face-name",
    "font-face-src",
    "font-face-uri",
    "font-face",
    "font",
    "foreignObject",
    "g",
    "glyph",
    "glyphRef",
    "hkern",
    "image",
    "line",
    "linearGradient",
    "marker",
    "mask",
    "metadata",
    "missing-glyph",
    "mpath",
    "path",
    "pattern",
    "polygon",
    "polyline",
    "radialGradient",
    "rect",
    "script",
    "set",
    "stop",
    "style",
    "svg",
    "switch",
    "symbol",
    "text",
    "textPath",
    "title",
    "tref",
    "tspan",
    "use",
    "view",
    "vkern",
]
"""Type for all SVG tag names."""


TAG_NAMES: Final[frozenset[TagName]] = frozenset(typing.get_args(TagName))
"""A set of all SVG tag names."""


def normalize_tag_name(name: TagName, /) -> str:
    """Convert an SVG tag name to an appropriate class name.

    Args:
        name: The tag name to normalize.

    Returns:
        The normalized tag name in `PascalCase`.

    Raises:
        ValueError: If the tag name cannot be normalized.

    Examples:
    >>> normalize_tag_name("circle")
    'Circle'
    >>> normalize_tag_name("feGaussianBlur")
    'FeGaussianBlur'
    >>> normalize_tag_name("font-face-name")
    'FontFaceName'

    """
    return "".join(part[0].upper() + part[1:] for part in name.split("-"))


TAG_NAME_TO_NORMALIZED: Final = bidict.frozenbidict(
    {tag: normalize_tag_name(tag) for tag in TAG_NAMES}
)
"""
A bidirectional mapping from SVG tag names to normalized Python identifiers.
"""
