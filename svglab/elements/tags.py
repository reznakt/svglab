import contextlib
import os
import pathlib
from typing import final, overload

from svglab import attrs, models, serialize, utils
from svglab.elements import common


# ! WARNING: `PairedTag` and `Tag` must always go last in the inheritance list


@final
class A(attrs.Common, attrs.Transform, common.PairedTag):
    pass


@final
class AltGlyph(attrs.Common, attrs.Presentation, common.Tag):
    pass


@final
class AltGlyphDef(attrs.Common, common.Tag):
    pass


@final
class AltGlyphItem(attrs.Common, common.Tag):
    pass


@final
class Animate(attrs.Common, common.Tag):
    pass


@final
class AnimateColor(attrs.Common, common.Tag):
    pass


@final
class AnimateMotion(attrs.Common, common.Tag):
    pass


@final
class AnimateTransform(attrs.Common, common.Tag):
    pass


@final
class Circle(
    attrs.CenterPoints,
    attrs.Common,
    attrs.Presentation,
    attrs.Radius,
    attrs.Transform,
    common.Tag,
):
    pass


@final
class ClipPath(attrs.Common, attrs.Transform, common.Tag):
    pass


@final
class ColorProfile(attrs.Common, common.Tag):
    pass


@final
class Cursor(attrs.Common, common.Tag):
    pass


@final
class Defs(attrs.Common, attrs.Transform, common.PairedTag):
    pass


@final
class Desc(attrs.Common, common.Tag):
    pass


@final
class Ellipse(
    attrs.CenterPoints,
    attrs.Common,
    attrs.Presentation,
    attrs.Transform,
    common.Tag,
):
    rx: models.Attr[attrs.Rx] = None
    ry: models.Attr[attrs.Ry] = None


@final
class FeBlend(attrs.Common, common.Tag):
    pass


@final
class FeColorMatrix(attrs.Common, common.Tag):
    pass


@final
class FeComponentTransfer(attrs.Common, common.Tag):
    pass


@final
class FeComposite(attrs.Common, common.Tag):
    pass


@final
class FeConvolveMatrix(attrs.Common, common.Tag):
    pass


@final
class FeDiffuseLighting(attrs.Common, common.Tag):
    pass


@final
class FeDisplacementMap(attrs.Common, common.Tag):
    pass


@final
class FeDistantLight(attrs.Common, common.Tag):
    pass


@final
class FeFlood(attrs.Common, common.Tag):
    pass


@final
class FeFuncA(attrs.Common, common.Tag):
    pass


@final
class FeFuncB(attrs.Common, common.Tag):
    pass


@final
class FeFuncG(attrs.Common, common.Tag):
    pass


@final
class FeFuncR(attrs.Common, common.Tag):
    pass


@final
class FeGaussianBlur(attrs.Common, common.Tag):
    pass


@final
class FeImage(attrs.Common, common.Tag):
    pass


@final
class FeMerge(attrs.Common, common.Tag):
    pass


@final
class FeMergeNode(attrs.Common, common.Tag):
    pass


@final
class FeMorphology(attrs.Common, common.Tag):
    pass


@final
class FeOffset(attrs.Common, common.Tag):
    pass


@final
class FePointLight(attrs.Common, common.Tag):
    pass


@final
class FeSpecularLighting(attrs.Common, common.Tag):
    pass


@final
class FeSpotLight(attrs.Common, common.Tag):
    pass


@final
class FeTile(attrs.Common, common.Tag):
    pass


@final
class FeTurbulence(attrs.Common, common.Tag):
    pass


@final
class Filter(attrs.Common, common.Tag):
    pass


@final
class Font(attrs.Common, common.Tag):
    pass


@final
class FontFace(attrs.Common, common.Tag):
    pass


@final
class FontFaceFormat(attrs.Common, common.Tag):
    pass


@final
class FontFaceName(attrs.Common, common.Tag):
    pass


@final
class FontFaceSrc(attrs.Common, common.Tag):
    pass


@final
class FontFaceUri(attrs.Common, common.Tag):
    pass


@final
class ForeignObject(attrs.Common, attrs.Transform, common.Tag):
    pass


@final
class G(attrs.Common, attrs.Transform, common.PairedTag):
    pass


@final
class Glyph(attrs.Common, attrs.PathData, common.PairedTag):
    pass


@final
class GlyphRef(attrs.Common, common.Tag):
    pass


@final
class Hkern(attrs.Common, common.Tag):
    pass


@final
class Image(attrs.Common, attrs.Transform, common.Tag):
    pass


@final
class Line(attrs.Common, attrs.Transform, attrs.Presentation, common.Tag):
    x1: models.Attr[attrs.X1] = None
    y1: models.Attr[attrs.Y1] = None
    x2: models.Attr[attrs.X2] = None
    y2: models.Attr[attrs.Y2] = None


@final
class LinearGradient(attrs.Common, common.Tag):
    pass


@final
class Marker(attrs.Common, common.PairedTag):
    pass


@final
class Mask(attrs.Common, common.PairedTag):
    pass


@final
class Metadata(attrs.Common, common.Tag):
    pass


@final
class MissingGlyph(
    attrs.Common, attrs.PathData, attrs.Transform, common.PairedTag
):
    pass


@final
class Mpath(attrs.Common, common.Tag):
    pass


@final
class Path(attrs.Common, attrs.PathData, attrs.Presentation, common.Tag):
    pass


@final
class Pattern(attrs.Common, common.PairedTag):
    pass


@final
class Polygon(
    attrs.Common,
    attrs.Points,
    attrs.Transform,
    attrs.Presentation,
    common.Tag,
):
    pass


@final
class Polyline(
    attrs.Common,
    attrs.Points,
    attrs.Transform,
    attrs.Presentation,
    common.Tag,
):
    pass


@final
class RadialGradient(attrs.Common, common.Tag):
    pass


@final
class Rect(
    attrs.Common,
    attrs.Presentation,
    attrs.RadiusXY,
    attrs.Transform,
    attrs.WidthHeight,
    common.Tag,
):
    x: models.Attr[attrs.X] = None
    y: models.Attr[attrs.Y] = None
    color: models.Attr[attrs.Color] = None


@final
class Script(attrs.Common, common.Tag):
    pass


@final
class Set(attrs.Common, common.Tag):
    pass


@final
class Stop(attrs.Common, common.Tag):
    pass


@final
class Style(attrs.Common, common.Tag):
    pass


@final
class Svg(attrs.Common, attrs.WidthHeight, common.PairedTag):
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
class Switch(attrs.Common, attrs.Transform, common.PairedTag):
    pass


@final
class Symbol(attrs.Common, common.PairedTag):
    pass


@final
class Text(attrs.Common, attrs.Transform, attrs.Presentation, common.Tag):
    pass


@final
class TextPath(attrs.Common, attrs.Presentation, common.Tag):
    pass


@final
class Title(attrs.Common, common.Tag):
    pass


@final
class Tref(attrs.Common, attrs.Presentation, common.Tag):
    pass


@final
class Tspan(attrs.Common, attrs.Presentation, common.Tag):
    pass


@final
class Use(attrs.Common, attrs.Transform, common.Tag):
    pass


@final
class View(attrs.Common, common.Tag):
    pass


@final
class Vkern(attrs.Common, common.Tag):
    pass
