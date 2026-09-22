"""Rendering of SVG documents into raster images."""

import pathlib
from collections.abc import Sequence

import PIL.Image
import pydantic
from typing_extensions import Final, final

from svglab import _resvg, errors, models
from svglab.attrparse import color
from svglab.attrs import typedefs


@final
@models.dataclass(
    frozen=True,
    kw_only=True,
    config=pydantic.ConfigDict(models.DATACLASS_CONFIG, strict=False),
)
class RenderOptions:
    """The settings a document is rendered with."""

    cursive_family: str | None = None
    """
    The font family that resolves the `cursive` generic family. If `None`,
    the renderer's own default is used.
    """

    default_size: tuple[typedefs.Number, typedefs.Number] = (100.0, 100.0)
    """
    The viewport, in pixels, to assume when the document has no `viewBox` and
    a relative `width` or `height`. `Svg.render` resolves the size of the
    document itself, so this only affects documents rendered through
    `svglab.resvg.render` directly.
    """

    dpi: typedefs.Number = 96.0
    """
    The resolution, in dots per inch, used to convert physical units such as
    `cm` and `pt` into pixels.
    """

    fantasy_family: str | None = None
    """
    The font family that resolves the `fantasy` generic family. If `None`,
    the renderer's own default is used.
    """

    font_dirs: Sequence[pathlib.Path] = ()
    """
    Directories to load extra fonts from, recursively. Files that are not
    fonts are skipped.
    """

    font_family: str | None = None
    """
    The font family to use where the document specifies none. If `None`, the
    family the system resolves `serif` to is used.
    """

    font_files: Sequence[pathlib.Path] = ()
    """Extra font files to load."""

    font_size: typedefs.Number = 12.0
    """The font size, in points, to use where the document specifies none."""

    image_rendering: typedefs.ImageRendering = "optimizeQuality"
    """The image rendering method to use where the document specifies none."""

    languages: Sequence[str] = ("en",)
    """
    The languages used to resolve the `systemLanguage` attribute, in order of
    preference, as language tags such as `en` or `en-US`.
    """

    monospace_family: str | None = None
    """
    The font family that resolves the `monospace` generic family. If `None`,
    the renderer's own default is used.
    """

    resources_dir: pathlib.Path | None = None
    """
    The directory that relative paths in the document, such as those of
    referenced images, resolve against. If `None`, paths are used as they are.
    """

    sans_serif_family: str | None = None
    """
    The font family that resolves the `sans-serif` generic family. If `None`,
    the renderer's own default is used.
    """

    serif_family: str | None = None
    """
    The font family that resolves the `serif` generic family. If `None`, the
    renderer's own default is used.
    """

    shape_rendering: typedefs.ShapeRendering = "geometricPrecision"
    """The shape rendering method to use where the document specifies none."""

    skip_system_fonts: bool = False
    """
    Whether to ignore the fonts installed on this system, so that only the
    fonts named by `font_files` and `font_dirs` are available.
    """

    style_sheet: str | None = None
    """
    A CSS stylesheet injected into the document. Its rules override the
    document's own presentation attributes, which makes it a way to restyle a
    document for a single render without editing the tree.
    """

    text_rendering: typedefs.TextRendering = "optimizeLegibility"
    """The text rendering method to use where the document specifies none."""


_DEFAULT_OPTIONS: Final = RenderOptions()


def _to_rgba(value: color.Color, /) -> tuple[int, int, int, int]:
    """Convert a color into its 8-bit RGBA components.

    `as_rgb_tuple` follows the CSS convention, in which the red, green and
    blue channels run from 0 to 255 but the alpha channel runs from 0 to 1;
    the renderer wants all four on the same scale.

    Args:
        value: The color to convert.

    Returns:
        The red, green, blue and alpha components of the color, each in the
        range 0-255.

    Examples:
        >>> from svglab import Color
        >>> _to_rgba(Color("red"))
        (255, 0, 0, 255)
        >>> _to_rgba(Color("rgba(0, 0, 0, 0.5)"))
        (0, 0, 0, 128)

    """
    red, green, blue, *alpha = value.as_rgb_tuple(alpha=True)

    return red, green, blue, round(alpha[0] * 255) if alpha else 255


def render(
    svg: str,
    options: RenderOptions | None = None,
    *,
    background: color.Color | None = None,
    zoom: float = 1,
) -> PIL.Image.Image:
    """Rasterize an SVG document into a Pillow image.

    Args:
        svg: The document to render.
        options: The rendering settings. If `None`, the defaults of
            `RenderOptions` are used.
        background: The color to paint under the document. If `None`, the
            background is transparent.
        zoom: The factor by which to scale the rendered image.

    Returns:
        The rendered image, in `RGBA` mode.

    Raises:
        ValueError: If an argument is not a valid value for its parameter.
        OSError: If a font file named by `font_files` cannot be read.
        MemoryError: If the image does not fit in memory.
        RuntimeError: If the renderer panics, which is a bug in it.
        SvgRenderError: If the document cannot be rasterized, for example
            because it is malformed.

    """
    options = _DEFAULT_OPTIONS if options is None else options

    try:
        width, height, pixels = _resvg.render(
            svg,
            background=_to_rgba(background)
            if background is not None
            else None,
            cursive_family=options.cursive_family,
            default_size=options.default_size,
            dpi=options.dpi,
            fantasy_family=options.fantasy_family,
            font_dirs=options.font_dirs,
            font_family=options.font_family,
            font_files=options.font_files,
            font_size=options.font_size,
            image_rendering=options.image_rendering,
            languages=options.languages,
            monospace_family=options.monospace_family,
            resources_dir=options.resources_dir,
            sans_serif_family=options.sans_serif_family,
            serif_family=options.serif_family,
            shape_rendering=options.shape_rendering,
            skip_system_fonts=options.skip_system_fonts,
            style_sheet=options.style_sheet,
            text_rendering=options.text_rendering,
            zoom=zoom,
        )
    except _resvg.RenderError as e:
        raise errors.SvgRenderError(str(e)) from e
    except _resvg.PanicError as e:
        raise RuntimeError(str(e)) from e

    return PIL.Image.frombuffer(
        "RGBA", (width, height), pixels, "raw", "RGBA", 0, 1
    )
