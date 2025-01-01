import contextlib
import os
import pathlib
from typing import final, overload

from svglab import models, serialize, utils
from svglab.attrs import groups, presentation, regular
from svglab.elements import common


# ! WARNING: `PairedTag` and `Tag` must always go last in the inheritance list


@final
class A(groups.Common, groups.Transform, common.PairedTag):
    pass


@final
class AltGlyph(groups.Common, groups.Presentation, common.Tag):
    pass


@final
class AltGlyphDef(groups.Common, common.Tag):
    pass


@final
class AltGlyphItem(groups.Common, common.Tag):
    pass


@final
class Animate(groups.Common, common.Tag):
    pass


@final
class AnimateColor(groups.Common, common.Tag):
    pass


@final
class AnimateMotion(groups.Common, common.Tag):
    pass


@final
class AnimateTransform(groups.Common, common.Tag):
    pass


@final
class Circle(
    groups.CenterPoints,
    groups.Common,
    groups.Presentation,
    groups.Radius,
    groups.Transform,
    common.Tag,
):
    pass


@final
class ClipPath(groups.Common, groups.Transform, common.Tag):
    pass


@final
class ColorProfile(groups.Common, common.Tag):
    pass


@final
class Cursor(groups.Common, common.Tag):
    pass


@final
class Defs(groups.Common, groups.Transform, common.PairedTag):
    pass


@final
class Desc(groups.Common, common.Tag):
    pass


@final
class Ellipse(
    groups.CenterPoints,
    groups.Common,
    groups.Presentation,
    groups.Transform,
    common.Tag,
):
    rx: models.Attr[regular.Rx] = None
    ry: models.Attr[regular.Ry] = None


@final
class FeBlend(groups.Common, common.Tag):
    pass


@final
class FeColorMatrix(groups.Common, common.Tag):
    pass


@final
class FeComponentTransfer(groups.Common, common.Tag):
    pass


@final
class FeComposite(groups.Common, common.Tag):
    pass


@final
class FeConvolveMatrix(groups.Common, common.Tag):
    pass


@final
class FeDiffuseLighting(groups.Common, common.Tag):
    pass


@final
class FeDisplacementMap(groups.Common, common.Tag):
    pass


@final
class FeDistantLight(groups.Common, common.Tag):
    pass


@final
class FeFlood(groups.Common, common.Tag):
    pass


@final
class FeFuncA(groups.Common, common.Tag):
    pass


@final
class FeFuncB(groups.Common, common.Tag):
    pass


@final
class FeFuncG(groups.Common, common.Tag):
    pass


@final
class FeFuncR(groups.Common, common.Tag):
    pass


@final
class FeGaussianBlur(groups.Common, common.Tag):
    pass


@final
class FeImage(groups.Common, common.Tag):
    pass


@final
class FeMerge(groups.Common, common.Tag):
    pass


@final
class FeMergeNode(groups.Common, common.Tag):
    pass


@final
class FeMorphology(groups.Common, common.Tag):
    pass


@final
class FeOffset(groups.Common, common.Tag):
    pass


@final
class FePointLight(groups.Common, common.Tag):
    pass


@final
class FeSpecularLighting(groups.Common, common.Tag):
    pass


@final
class FeSpotLight(groups.Common, common.Tag):
    pass


@final
class FeTile(groups.Common, common.Tag):
    pass


@final
class FeTurbulence(groups.Common, common.Tag):
    pass


@final
class Filter(groups.Common, common.Tag):
    pass


@final
class Font(groups.Common, common.Tag):
    pass


@final
class FontFace(groups.Common, common.Tag):
    pass


@final
class FontFaceFormat(groups.Common, common.Tag):
    pass


@final
class FontFaceName(groups.Common, common.Tag):
    pass


@final
class FontFaceSrc(groups.Common, common.Tag):
    pass


@final
class FontFaceUri(groups.Common, common.Tag):
    pass


@final
class ForeignObject(groups.Common, groups.Transform, common.Tag):
    pass


@final
class G(groups.Common, groups.Transform, common.PairedTag):
    pass


@final
class Glyph(groups.Common, groups.PathData, common.PairedTag):
    pass


@final
class GlyphRef(groups.Common, common.Tag):
    pass


@final
class Hkern(groups.Common, common.Tag):
    pass


@final
class Image(groups.Common, groups.Transform, common.Tag):
    pass


@final
class Line(
    groups.Common, groups.Transform, groups.Presentation, common.Tag
):
    x1: models.Attr[regular.X1] = None
    y1: models.Attr[regular.Y1] = None
    x2: models.Attr[regular.X2] = None
    y2: models.Attr[regular.Y2] = None


@final
class LinearGradient(groups.Common, common.Tag):
    pass


@final
class Marker(groups.Common, common.PairedTag):
    pass


@final
class Mask(groups.Common, common.PairedTag):
    pass


@final
class Metadata(groups.Common, common.Tag):
    pass


@final
class MissingGlyph(
    groups.Common, groups.PathData, groups.Transform, common.PairedTag
):
    pass


@final
class Mpath(groups.Common, common.Tag):
    pass


@final
class Path(
    groups.Common, groups.PathData, groups.Presentation, common.Tag
):
    pass


@final
class Pattern(groups.Common, common.PairedTag):
    pass


@final
class Polygon(
    groups.Common,
    groups.Points,
    groups.Transform,
    groups.Presentation,
    common.Tag,
):
    pass


@final
class Polyline(
    groups.Common,
    groups.Points,
    groups.Transform,
    groups.Presentation,
    common.Tag,
):
    pass


@final
class RadialGradient(groups.Common, common.Tag):
    pass


@final
class Rect(
    groups.Common,
    groups.Presentation,
    groups.RadiusXY,
    groups.Transform,
    groups.WidthHeight,
    common.Tag,
):
    x: models.Attr[regular.X] = None
    y: models.Attr[regular.Y] = None
    color: models.Attr[presentation.Color] = None


@final
class Script(groups.Common, common.Tag):
    pass


@final
class Set(groups.Common, common.Tag):
    pass


@final
class Stop(groups.Common, common.Tag):
    pass


@final
class Style(groups.Common, common.Tag):
    pass


@final
class Svg(groups.Common, groups.WidthHeight, common.PairedTag):
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
class Switch(groups.Common, groups.Transform, common.PairedTag):
    pass


@final
class Symbol(groups.Common, common.PairedTag):
    pass


@final
class Text(
    groups.Common, groups.Transform, groups.Presentation, common.Tag
):
    pass


@final
class TextPath(groups.Common, groups.Presentation, common.Tag):
    pass


@final
class Title(groups.Common, common.Tag):
    pass


@final
class Tref(groups.Common, groups.Presentation, common.Tag):
    pass


@final
class Tspan(groups.Common, groups.Presentation, common.Tag):
    pass


@final
class Use(groups.Common, groups.Transform, common.Tag):
    pass


@final
class View(groups.Common, common.Tag):
    pass


@final
class Vkern(groups.Common, common.Tag):
    pass
