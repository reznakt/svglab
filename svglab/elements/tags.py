import contextlib
import os
import pathlib
from typing import Literal, final, overload

from svglab import attrs, models, serialize, types
from svglab.elements import common

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


class AttrBase(models.BaseModel):
    pass


class CommonAttrs(AttrBase):
    """Common attributes shared by all SVG elements."""

    id: models.Attr[str] = None
    xml_base: models.Attr[str] = None
    xml_lang: models.Attr[str] = None
    xml_space: models.Attr[Literal["default", "preserve"]] = None


# ! WARNING: `PairedTag` and `Tag` must always go last in the inheritance list


@final
class A(CommonAttrs, common.PairedTag):
    pass


@final
class AltGlyph(CommonAttrs, common.Tag):
    pass


@final
class AltGlyphDef(CommonAttrs, common.Tag):
    pass


@final
class AltGlyphItem(CommonAttrs, common.Tag):
    pass


@final
class Animate(CommonAttrs, common.Tag):
    pass


@final
class AnimateColor(CommonAttrs, common.Tag):
    pass


@final
class AnimateMotion(CommonAttrs, common.Tag):
    pass


@final
class AnimateTransform(CommonAttrs, common.Tag):
    pass


@final
class Circle(CommonAttrs, common.Tag):
    pass


@final
class ClipPath(CommonAttrs, common.Tag):
    pass


@final
class ColorProfile(CommonAttrs, common.Tag):
    pass


@final
class Cursor(CommonAttrs, common.Tag):
    pass


@final
class Defs(CommonAttrs, common.PairedTag):
    pass


@final
class Desc(CommonAttrs, common.Tag):
    pass


@final
class Ellipse(CommonAttrs, common.Tag):
    pass


@final
class FeBlend(CommonAttrs, common.Tag):
    pass


@final
class FeColorMatrix(CommonAttrs, common.Tag):
    pass


@final
class FeComponentTransfer(CommonAttrs, common.Tag):
    pass


@final
class FeComposite(CommonAttrs, common.Tag):
    pass


@final
class FeConvolveMatrix(CommonAttrs, common.Tag):
    pass


@final
class FeDiffuseLighting(CommonAttrs, common.Tag):
    pass


@final
class FeDisplacementMap(CommonAttrs, common.Tag):
    pass


@final
class FeDistantLight(CommonAttrs, common.Tag):
    pass


@final
class FeFlood(CommonAttrs, common.Tag):
    pass


@final
class FeFuncA(CommonAttrs, common.Tag):
    pass


@final
class FeFuncB(CommonAttrs, common.Tag):
    pass


@final
class FeFuncG(CommonAttrs, common.Tag):
    pass


@final
class FeFuncR(CommonAttrs, common.Tag):
    pass


@final
class FeGaussianBlur(CommonAttrs, common.Tag):
    pass


@final
class FeImage(CommonAttrs, common.Tag):
    pass


@final
class FeMerge(CommonAttrs, common.Tag):
    pass


@final
class FeMergeNode(CommonAttrs, common.Tag):
    pass


@final
class FeMorphology(CommonAttrs, common.Tag):
    pass


@final
class FeOffset(CommonAttrs, common.Tag):
    pass


@final
class FePointLight(CommonAttrs, common.Tag):
    pass


@final
class FeSpecularLighting(CommonAttrs, common.Tag):
    pass


@final
class FeSpotLight(CommonAttrs, common.Tag):
    pass


@final
class FeTile(CommonAttrs, common.Tag):
    pass


@final
class FeTurbulence(CommonAttrs, common.Tag):
    pass


@final
class Filter(CommonAttrs, common.Tag):
    pass


@final
class Font(CommonAttrs, common.Tag):
    pass


@final
class FontFace(CommonAttrs, common.Tag):
    pass


@final
class FontFaceFormat(CommonAttrs, common.Tag):
    pass


@final
class FontFaceName(CommonAttrs, common.Tag):
    pass


@final
class FontFaceSrc(CommonAttrs, common.Tag):
    pass


@final
class FontFaceUri(CommonAttrs, common.Tag):
    pass


@final
class ForeignObject(CommonAttrs, common.Tag):
    pass


@final
class G(CommonAttrs, common.PairedTag):
    pass


@final
class Glyph(CommonAttrs, common.PairedTag):
    pass


@final
class GlyphRef(CommonAttrs, common.Tag):
    pass


@final
class Hkern(CommonAttrs, common.Tag):
    pass


@final
class Image(CommonAttrs, common.Tag):
    pass


@final
class Line(CommonAttrs, common.Tag):
    pass


@final
class LinearGradient(CommonAttrs, common.Tag):
    pass


@final
class Marker(CommonAttrs, common.PairedTag):
    pass


@final
class Mask(CommonAttrs, common.PairedTag):
    pass


@final
class Metadata(CommonAttrs, common.Tag):
    pass


@final
class MissingGlyph(CommonAttrs, common.PairedTag):
    pass


@final
class Mpath(CommonAttrs, common.Tag):
    pass


@final
class Path(CommonAttrs, common.Tag):
    pass


@final
class Pattern(CommonAttrs, common.PairedTag):
    pass


@final
class Polygon(CommonAttrs, common.Tag):
    pass


@final
class Polyline(CommonAttrs, common.Tag):
    pass


@final
class RadialGradient(CommonAttrs, common.Tag):
    pass


@final
class Rect(CommonAttrs, common.Tag):
    x: models.Attr[float] = None
    y: models.Attr[float] = None
    width: models.Attr[attrs.LengthType] = None
    height: models.Attr[attrs.LengthType] = None
    transform: models.Attr[attrs.TransformType] = None
    color: models.Attr[attrs.ColorType] = None


@final
class Script(CommonAttrs, common.Tag):
    pass


@final
class Set(CommonAttrs, common.Tag):
    pass


@final
class Stop(CommonAttrs, common.Tag):
    pass


@final
class Style(CommonAttrs, common.Tag):
    pass


@final
class Svg(CommonAttrs, common.PairedTag):
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
        file: types.SupportsWrite[str],
        /,
        *,
        pretty: bool = True,
        trailing_newline: bool = True,
        formatter: serialize.Formatter | None = None,
    ) -> None: ...

    def save(
        self,
        path_or_file: str | os.PathLike[str] | types.SupportsWrite[str],
        /,
        *,
        pretty: bool = True,
        trailing_newline: bool = True,
        formatter: serialize.Formatter | None = None,
    ) -> None:
        """Convert the SVG document fragment to XML and write it to a file.

        Args:
        path_or_file: The path to the file to save the XML to, or a file-like object.
        pretty: Whether to produce pretty-printed XML.
        indent: The number of spaces to indent each level of the document.
        trailing_newline: Whether to add a trailing newline to the file.
        formatter: The formatter to use for serialization.

        Examples:
        >>> import sys
        >>> svg = Svg(id="foo").add_child(Rect())
        >>> formatter = serialize.Formatter(indent=4)
        >>> svg.save(
        ...     sys.stdout, pretty=True, trailing_newline=False, formatter=formatter
        ... )
        <svg id="foo">
            <rect/>
        </svg>

        """
        with contextlib.ExitStack() as stack:
            output = self.to_xml(pretty=pretty, formatter=formatter)
            file: types.SupportsWrite[str]

            match path_or_file:
                case str() | os.PathLike() as path:
                    file = stack.enter_context(pathlib.Path(path).open("w"))
                case types.SupportsWrite() as file:
                    pass

            file.write(output)

            if trailing_newline:
                file.write("\n")


@final
class Switch(CommonAttrs, common.PairedTag):
    pass


@final
class Symbol(CommonAttrs, common.PairedTag):
    pass


@final
class Text(CommonAttrs, common.Tag):
    pass


@final
class TextPath(CommonAttrs, common.Tag):
    pass


@final
class Title(CommonAttrs, common.Tag):
    pass


@final
class Tref(CommonAttrs, common.Tag):
    pass


@final
class Tspan(CommonAttrs, common.Tag):
    pass


@final
class Use(CommonAttrs, common.Tag):
    pass


@final
class View(CommonAttrs, common.Tag):
    pass


@final
class Vkern(CommonAttrs, common.Tag):
    pass
