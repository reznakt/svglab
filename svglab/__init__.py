"""A manipulation and optimization library for Scalable Vector Graphics (SVG).

This package provides a set of tools for parsing, manipulating, and serializing
SVG files. It allows you to create, modify, and optimize SVG graphics in a
Pythonic way.

The package has a flat import structure, so you can import any symbol directly
by using the following syntax:
```
from svglab import <symbol>
```

Some stuff to get you started:
- use `parse_svg` to parse an SVG string or file into an `Svg` object,
- use `Svg` directly to create a new SVG document from scratch,
- use `.find()` and `.find_all()` to search for elements in the SVG tree,
- use `.to_xml()` to serialize an SVG element to a string,
- use `.save()` to serialize an SVG document and write it to a file,
- use `Formatter` and `set_formatter()` to customize the serialization of SVG
elements.

Example usage:
```
>>> from svglab import parse_svg, Circle, Rect, Length, Rotate
>>> svg = parse_svg("<svg><circle cx='50' cy='50' r='40'/></svg>")
>>> circle = svg.find(Circle)
>>> circle.cx
Length(value=50.0, unit=None)
>>> _ = svg.add_child(
...    Rect(width=Length(100), height=Length(100), transform=[Rotate(45)])
... )
>>> print(svg.to_xml())
<svg>
  <circle cx="50" cy="50" r="40"/>
  <rect height="100" transform="rotate(45)" width="100"/>
</svg>

```
"""

from importlib import metadata as __metadata

import affine as __affine
from typing_extensions import Final as __Final

from svglab import constants as __constants
from svglab.attrparse.angle import Angle, AngleUnit
from svglab.attrparse.color import Color
from svglab.attrparse.d import (
    ArcTo,
    ClosePath,
    CubicBezierTo,
    D,
    HorizontalLineTo,
    LineTo,
    MoveTo,
    PathCommand,
    QuadraticBezierTo,
    SmoothCubicBezierTo,
    SmoothQuadraticBezierTo,
    VerticalLineTo,
)
from svglab.attrparse.length import Length
from svglab.attrparse.point import Point
from svglab.attrparse.points import Points
from svglab.attrparse.transform import (
    Matrix,
    Reifiable,
    Rotate,
    Scale,
    SkewX,
    SkewY,
    Transform,
    TransformFunction,
    Translate,
    compose,
)
from svglab.elements.common import (
    Element,
    Tag,
    TextElement,
    swap_transforms,
)
from svglab.elements.svg import Svg
from svglab.elements.tags import (
    A,
    AltGlyph,
    AltGlyphDef,
    AltGlyphItem,
    Animate,
    AnimateColor,
    AnimateMotion,
    AnimateTransform,
    Circle,
    ClipPath,
    ColorProfile,
    Cursor,
    Defs,
    Desc,
    Ellipse,
    FeBlend,
    FeColorMatrix,
    FeComponentTransfer,
    FeComposite,
    FeConvolveMatrix,
    FeDiffuseLighting,
    FeDisplacementMap,
    FeDistantLight,
    FeFlood,
    FeFuncA,
    FeFuncB,
    FeFuncG,
    FeFuncR,
    FeGaussianBlur,
    FeImage,
    FeMerge,
    FeMergeNode,
    FeMorphology,
    FeOffset,
    FePointLight,
    FeSpecularLighting,
    FeSpotLight,
    FeTile,
    FeTurbulence,
    Filter,
    Font,
    FontFace,
    FontFaceFormat,
    FontFaceName,
    FontFaceSrc,
    FontFaceUri,
    ForeignObject,
    G,
    Glyph,
    GlyphRef,
    Hkern,
    Image,
    Line,
    LinearGradient,
    Marker,
    Mask,
    Metadata,
    MissingGlyph,
    Mpath,
    Path,
    Pattern,
    Polygon,
    Polyline,
    RadialGradient,
    Rect,
    Script,
    Set,
    Stop,
    Style,
    Switch,
    Symbol,
    Text,
    TextPath,
    Title,
    Tref,
    Tspan,
    Use,
    View,
    Vkern,
)
from svglab.elements.text_elements import CData, Comment, RawText
from svglab.elements.traits import (
    BasicShape,
    ContainerElement,
    DescriptiveElement,
    FilterPrimitiveElement,
    GradientElement,
    GraphicsElement,
    GraphicsReferencingElement,
    LightSourceElement,
    Shape,
    StructuralElement,
    TextContentBlockElement,
    TextContentChildElement,
    TextContentElement,
)
from svglab.errors import (
    SvgElementNotFoundError,
    SvgError,
    SvgPathError,
    SvgPathMissingMoveToError,
    SvgReifyError,
    SvgTransformSwapError,
    SvgUnitConversionError,
)
from svglab.parse import parse_svg
from svglab.serialize import (
    DEFAULT_FORMATTER,
    MINIMAL_FORMATTER,
    FloatPrecisionSettings,
    Formatter,
    get_current_formatter,
    set_formatter,
)
from svglab.utiltypes import LengthUnit


__all__ = [
    "DEFAULT_FORMATTER",
    "MINIMAL_FORMATTER",
    "A",
    "AltGlyph",
    "AltGlyphDef",
    "AltGlyphItem",
    "Angle",
    "AngleUnit",
    "Animate",
    "AnimateColor",
    "AnimateMotion",
    "AnimateTransform",
    "ArcTo",
    "BasicShape",
    "CData",
    "Circle",
    "ClipPath",
    "ClosePath",
    "Color",
    "ColorProfile",
    "Comment",
    "ContainerElement",
    "CubicBezierTo",
    "Cursor",
    "D",
    "Defs",
    "Desc",
    "DescriptiveElement",
    "Element",
    "Ellipse",
    "FeBlend",
    "FeColorMatrix",
    "FeComponentTransfer",
    "FeComposite",
    "FeConvolveMatrix",
    "FeDiffuseLighting",
    "FeDisplacementMap",
    "FeDistantLight",
    "FeFlood",
    "FeFuncA",
    "FeFuncB",
    "FeFuncG",
    "FeFuncR",
    "FeGaussianBlur",
    "FeImage",
    "FeMerge",
    "FeMergeNode",
    "FeMorphology",
    "FeOffset",
    "FePointLight",
    "FeSpecularLighting",
    "FeSpotLight",
    "FeTile",
    "FeTurbulence",
    "Filter",
    "FilterPrimitiveElement",
    "FloatPrecisionSettings",
    "Font",
    "FontFace",
    "FontFaceFormat",
    "FontFaceName",
    "FontFaceSrc",
    "FontFaceUri",
    "ForeignObject",
    "Formatter",
    "G",
    "Glyph",
    "GlyphRef",
    "GradientElement",
    "GraphicsElement",
    "GraphicsReferencingElement",
    "Hkern",
    "HorizontalLineTo",
    "Image",
    "Length",
    "LengthUnit",
    "LightSourceElement",
    "Line",
    "LineTo",
    "LinearGradient",
    "Marker",
    "Mask",
    "Matrix",
    "Metadata",
    "MissingGlyph",
    "MoveTo",
    "Mpath",
    "Path",
    "PathCommand",
    "Pattern",
    "Point",
    "Points",
    "Polygon",
    "Polyline",
    "QuadraticBezierTo",
    "RadialGradient",
    "RawText",
    "Rect",
    "Reifiable",
    "Rotate",
    "Scale",
    "Script",
    "Set",
    "Shape",
    "SkewX",
    "SkewY",
    "SmoothCubicBezierTo",
    "SmoothQuadraticBezierTo",
    "Stop",
    "StructuralElement",
    "Style",
    "Svg",
    "SvgElementNotFoundError",
    "SvgError",
    "SvgPathError",
    "SvgPathMissingMoveToError",
    "SvgReifyError",
    "SvgTransformSwapError",
    "SvgUnitConversionError",
    "Switch",
    "Symbol",
    "Tag",
    "Text",
    "TextContentBlockElement",
    "TextContentChildElement",
    "TextContentElement",
    "TextElement",
    "TextPath",
    "Title",
    "Transform",
    "TransformFunction",
    "Translate",
    "Tref",
    "Tspan",
    "Use",
    "VerticalLineTo",
    "View",
    "Vkern",
    "compose",
    "get_current_formatter",
    "parse_svg",
    "set_formatter",
    "swap_transforms",
]


__affine.set_epsilon(__constants.FLOAT_ABSOLUTE_TOLERANCE)

__version__: __Final = __metadata.version(__name__)
