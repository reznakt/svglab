import contextlib
import os
import pathlib
from typing import final, overload

from svglab import models, serialize, utils
from svglab.elements import attrdefs, attrtypes, common

__all__ = [
    "A",
    "AltGlyph",
    "AltGlyphDef",
    "AltGlyphItem",
    "Animate",
    "AnimateColor",
    "AnimateMotion",
    "AnimateTransform",
    "Circle",
    "ClipPath",
    "ColorProfile",
    "Cursor",
    "Defs",
    "Desc",
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
    "Font",
    "FontFace",
    "FontFaceFormat",
    "FontFaceName",
    "FontFaceSrc",
    "FontFaceUri",
    "ForeignObject",
    "G",
    "Glyph",
    "GlyphRef",
    "Hkern",
    "Image",
    "Line",
    "LinearGradient",
    "Marker",
    "Mask",
    "Metadata",
    "MissingGlyph",
    "Mpath",
    "Path",
    "Pattern",
    "Polygon",
    "Polyline",
    "RadialGradient",
    "Rect",
    "Script",
    "Set",
    "Stop",
    "Style",
    "Svg",
    "Switch",
    "Symbol",
    "Text",
    "TextPath",
    "Title",
    "Tref",
    "Tspan",
    "Use",
    "View",
    "Vkern",
]


# ! WARNING: `PairedTag` and `Tag` must always go last in the inheritance list


@final
class A(attrdefs.Common, attrdefs.Transform, common.PairedTag):
    pass


@final
class AltGlyph(attrdefs.Common, attrdefs.Presentation, common.Tag):
    pass


@final
class AltGlyphDef(attrdefs.Common, common.Tag):
    pass


@final
class AltGlyphItem(attrdefs.Common, common.Tag):
    pass


@final
class Animate(attrdefs.Common, common.Tag):
    pass


@final
class AnimateColor(attrdefs.Common, common.Tag):
    pass


@final
class AnimateMotion(attrdefs.Common, common.Tag):
    pass


@final
class AnimateTransform(attrdefs.Common, common.Tag):
    pass


@final
class Circle(
    attrdefs.CenterPoints,
    attrdefs.Common,
    attrdefs.Presentation,
    attrdefs.Radius,
    attrdefs.Transform,
    common.Tag,
):
    pass


@final
class ClipPath(attrdefs.Common, attrdefs.Transform, common.Tag):
    pass


@final
class ColorProfile(attrdefs.Common, common.Tag):
    pass


@final
class Cursor(attrdefs.Common, common.Tag):
    pass


@final
class Defs(attrdefs.Common, attrdefs.Transform, common.PairedTag):
    pass


@final
class Desc(attrdefs.Common, common.Tag):
    pass


@final
class Ellipse(
    attrdefs.CenterPoints,
    attrdefs.Common,
    attrdefs.Presentation,
    attrdefs.Transform,
    common.Tag,
):
    rx: models.Attr[attrtypes.Length] = None
    ry: models.Attr[attrtypes.Length] = None


@final
class FeBlend(attrdefs.Common, common.Tag):
    pass


@final
class FeColorMatrix(attrdefs.Common, common.Tag):
    pass


@final
class FeComponentTransfer(attrdefs.Common, common.Tag):
    pass


@final
class FeComposite(attrdefs.Common, common.Tag):
    pass


@final
class FeConvolveMatrix(attrdefs.Common, common.Tag):
    pass


@final
class FeDiffuseLighting(attrdefs.Common, common.Tag):
    pass


@final
class FeDisplacementMap(attrdefs.Common, common.Tag):
    pass


@final
class FeDistantLight(attrdefs.Common, common.Tag):
    pass


@final
class FeFlood(attrdefs.Common, common.Tag):
    pass


@final
class FeFuncA(attrdefs.Common, common.Tag):
    pass


@final
class FeFuncB(attrdefs.Common, common.Tag):
    pass


@final
class FeFuncG(attrdefs.Common, common.Tag):
    pass


@final
class FeFuncR(attrdefs.Common, common.Tag):
    pass


@final
class FeGaussianBlur(attrdefs.Common, common.Tag):
    pass


@final
class FeImage(attrdefs.Common, common.Tag):
    pass


@final
class FeMerge(attrdefs.Common, common.Tag):
    pass


@final
class FeMergeNode(attrdefs.Common, common.Tag):
    pass


@final
class FeMorphology(attrdefs.Common, common.Tag):
    pass


@final
class FeOffset(attrdefs.Common, common.Tag):
    pass


@final
class FePointLight(attrdefs.Common, common.Tag):
    pass


@final
class FeSpecularLighting(attrdefs.Common, common.Tag):
    pass


@final
class FeSpotLight(attrdefs.Common, common.Tag):
    pass


@final
class FeTile(attrdefs.Common, common.Tag):
    pass


@final
class FeTurbulence(attrdefs.Common, common.Tag):
    pass


@final
class Filter(attrdefs.Common, common.Tag):
    pass


@final
class Font(attrdefs.Common, common.Tag):
    pass


@final
class FontFace(attrdefs.Common, common.Tag):
    pass


@final
class FontFaceFormat(attrdefs.Common, common.Tag):
    pass


@final
class FontFaceName(attrdefs.Common, common.Tag):
    pass


@final
class FontFaceSrc(attrdefs.Common, common.Tag):
    pass


@final
class FontFaceUri(attrdefs.Common, common.Tag):
    pass


@final
class ForeignObject(attrdefs.Common, attrdefs.Transform, common.Tag):
    pass


@final
class G(attrdefs.Common, attrdefs.Transform, common.PairedTag):
    pass


@final
class Glyph(attrdefs.Common, attrdefs.PathData, common.PairedTag):
    pass


@final
class GlyphRef(attrdefs.Common, common.Tag):
    pass


@final
class Hkern(attrdefs.Common, common.Tag):
    pass


@final
class Image(attrdefs.Common, attrdefs.Transform, common.Tag):
    pass


@final
class Line(
    attrdefs.Common, attrdefs.Transform, attrdefs.Presentation, common.Tag
):
    x1: models.Attr[attrtypes.Coordinate] = None
    y1: models.Attr[attrtypes.Coordinate] = None
    x2: models.Attr[attrtypes.Coordinate] = None
    y2: models.Attr[attrtypes.Coordinate] = None


@final
class LinearGradient(attrdefs.Common, common.Tag):
    pass


@final
class Marker(attrdefs.Common, common.PairedTag):
    pass


@final
class Mask(attrdefs.Common, common.PairedTag):
    pass


@final
class Metadata(attrdefs.Common, common.Tag):
    pass


@final
class MissingGlyph(
    attrdefs.Common,
    attrdefs.PathData,
    attrdefs.Transform,
    common.PairedTag,
):
    pass


@final
class Mpath(attrdefs.Common, common.Tag):
    pass


@final
class Path(
    attrdefs.Common, attrdefs.PathData, attrdefs.Presentation, common.Tag
):
    pass


@final
class Pattern(attrdefs.Common, common.PairedTag):
    pass


@final
class Polygon(
    attrdefs.Common,
    attrdefs.Points,
    attrdefs.Transform,
    attrdefs.Presentation,
    common.Tag,
):
    pass


@final
class Polyline(
    attrdefs.Common,
    attrdefs.Points,
    attrdefs.Transform,
    attrdefs.Presentation,
    common.Tag,
):
    pass


@final
class RadialGradient(attrdefs.Common, common.Tag):
    pass


@final
class Rect(
    attrdefs.Common,
    attrdefs.Presentation,
    attrdefs.RadiusXY,
    attrdefs.Transform,
    attrdefs.WidthHeight,
    common.Tag,
):
    x: models.Attr[attrtypes.Coordinate] = None
    y: models.Attr[attrtypes.Coordinate] = None
    color: models.Attr[attrtypes.Color] = None


@final
class Script(attrdefs.Common, common.Tag):
    pass


@final
class Set(attrdefs.Common, common.Tag):
    pass


@final
class Stop(attrdefs.Common, common.Tag):
    pass


@final
class Style(attrdefs.Common, common.Tag):
    pass


@final
class Svg(attrdefs.Common, attrdefs.WidthHeight, common.PairedTag):
    xmlns: models.Attr[str] = "http://www.w3.org/2000/svg"

    @overload
    def save(
        self,
        path: str | os.PathLike[str],
        /,
        *,
        pretty: bool = True,
        trailing_newline: bool = True,
        formatter: serialize.Formatter | None = None,
    ) -> None: ...

    @overload
    def save(
        self,
        file: utils.SupportsWrite[str],
        /,
        *,
        pretty: bool = True,
        trailing_newline: bool = True,
        formatter: serialize.Formatter | None = None,
    ) -> None: ...

    def save(
        self,
        path_or_file: str | os.PathLike[str] | utils.SupportsWrite[str],
        /,
        *,
        pretty: bool = True,
        trailing_newline: bool = True,
        formatter: serialize.Formatter | None = None,
    ) -> None:
        """Convert the SVG document fragment to XML and write it to a file.

        Args:
        path_or_file: The path to the file to save the XML to,
        or a file-like object.
        pretty: Whether to produce pretty-printed XML.
        indent: The number of spaces to indent each level of the document.
        trailing_newline: Whether to add a trailing newline to the file.
        formatter: The formatter to use for serialization.

        Examples:
        >>> import sys
        >>> svg = Svg(id="foo").add_child(Rect())
        >>> formatter = serialize.Formatter(indent=4)
        >>> svg.save(
        ...     sys.stdout,
        ...     pretty=True,
        ...     trailing_newline=False,
        ...     formatter=formatter,
        ... )
        <svg id="foo">
            <rect/>
        </svg>

        """
        with contextlib.ExitStack() as stack:
            output = self.to_xml(pretty=pretty, formatter=formatter)
            file: utils.SupportsWrite[str]

            match path_or_file:
                case str() | os.PathLike() as path:
                    file = stack.enter_context(
                        pathlib.Path(path).open("w")
                    )
                case utils.SupportsWrite() as file:
                    pass

            file.write(output)

            if trailing_newline:
                file.write("\n")


@final
class Switch(attrdefs.Common, attrdefs.Transform, common.PairedTag):
    pass


@final
class Symbol(attrdefs.Common, common.PairedTag):
    pass


@final
class Text(
    attrdefs.Common, attrdefs.Transform, attrdefs.Presentation, common.Tag
):
    pass


@final
class TextPath(attrdefs.Common, attrdefs.Presentation, common.Tag):
    pass


@final
class Title(attrdefs.Common, common.Tag):
    pass


@final
class Tref(attrdefs.Common, attrdefs.Presentation, common.Tag):
    pass


@final
class Tspan(attrdefs.Common, attrdefs.Presentation, common.Tag):
    pass


@final
class Use(attrdefs.Common, attrdefs.Transform, common.Tag):
    pass


@final
class View(attrdefs.Common, common.Tag):
    pass


@final
class Vkern(attrdefs.Common, common.Tag):
    pass
