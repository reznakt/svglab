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
