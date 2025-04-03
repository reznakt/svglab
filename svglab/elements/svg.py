"""The definition of the <svg> element.

This module contains the definition of the <svg> element (see the `Svg` class).

The <svg> element is of special importance in SVG documents, as it is the root
of the element tree. For this reason, it contains several methods not found on
other elements, and thus is defined in its own module.
"""

import base64
import contextlib
import os
import pathlib

import PIL.Image
from typing_extensions import final, overload

from svglab import graphics, protocols, serialize
from svglab.attrparse import transform
from svglab.attrs import groups, regular
from svglab.elements import traits
from svglab.utils import mathutils


@final
class Svg(
    groups.ConditionalProcessing,
    groups.DocumentEvents,
    regular.BaseProfile,
    regular.Class,
    regular.ContentScriptType,
    regular.ContentStyleType,
    regular.ExternalResourcesRequired,
    regular.Height,
    regular.PreserveAspectRatio,
    regular.Style,
    regular.Version,
    regular.ViewBox,
    regular.Width,
    regular.XCoordinate,
    regular.Xmlns,
    regular.YCoordinate,
    regular.ZoomAndPan,
    traits.StructuralElement,
    traits.ContainerElement,
):
    """The `<svg>` element.

    The `<svg>` element is the root of an SVG document fragment.

    You can either create a new SVG document from scratch by creating an
    instance of this class, or you can parse an existing SVG document
    using the `parse_svg` function.
    """

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
        file: protocols.SupportsWrite[str],
        /,
        *,
        pretty: bool = True,
        trailing_newline: bool = True,
        formatter: serialize.Formatter | None = None,
    ) -> None: ...

    def save(
        self,
        path_or_file: str
        | os.PathLike[str]
        | protocols.SupportsWrite[str],
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
        >>> from svglab import Rect, Svg
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
            file: protocols.SupportsWrite[str]

            match path_or_file:
                case str() | os.PathLike() as path:
                    file = stack.enter_context(
                        pathlib.Path(path).open("w")
                    )
                case protocols.SupportsWrite() as file:
                    pass

            file.write(output)

            if trailing_newline:
                file.write("\n")

    def set_viewbox(
        self, viewbox: tuple[float, float, float, float]
    ) -> None:
        """Set a new value for the `viewBox` attribute.

        This method sets a new value for the `viewBox` attribute and scales and
        translates the SVG content so that the visual representation of the SVG
        remains unchanged.

        If the `viewBox` is not set, the method uses the `width` and `height`
        attributes to calculate the initial viewBox. If the `width`
        and `height` attributes are not set, the method raises an exception.

        The new `viewBox` must have the same aspect ratio as the old `viewBox`.
        If the aspect ratios differ, the method raises an exception.

        Any attributes of type `Length` in the SVG must be convertible to
        user units. If an attribute is not convertible, the method raises an
        exception.

        Args:
        viewbox: A tuple of four numbers representing the new viewBox.

        Raises:
        ValueError: If `viewBox` is not set and `width` and `height` are not
            set or if the aspect ratios of the old and new viewBox differ.
        SvgUnitConversionError: If an attribute is not convertible to user
            units.

        """
        if self.viewBox is None:
            if self.width is None or self.height is None:
                raise ValueError(
                    "Either viewBox or width and height must be set"
                )
            old_viewbox = (0, 0, float(self.width), float(self.height))
        else:
            old_viewbox = self.viewBox

        old_min_x, old_min_y, old_width, old_height = old_viewbox
        min_x, min_y, width, height = viewbox

        tx = min_x - old_min_x
        ty = min_y - old_min_y

        sx = width / old_width
        sy = height / old_height

        if not mathutils.is_close(sx, sy):
            raise ValueError("Aspect ratios of old and new viewBox differ")

        # skip self; this can be done in a single for loop because the
        # SVG is a tree (probably)
        for child in self.find_all(recursive=False):
            # this is normally done in the reify method, but we need to do it
            # before we prepend the new transformations
            child.decompose_transform_origin()

            child.transform = [
                transform.Translate(tx, ty),
                transform.Scale(sx, sy),
                *(child.transform or []),
            ]

            child.reify(limit=2, recursive=False)

        self.viewBox = viewbox

    def render(
        self, *, width: float | None = None, height: float | None = None
    ) -> PIL.Image.Image:
        """Render an SVG document fragment into a Pillow image.

        If the width and height are not specified, the dimensions of the SVG
        element are used. If only one dimension is specified, the other
        dimension is calculated in a way that preserves the aspect ratio set
        in the SVG element. If both dimensions are specified, the SVG is
        scaled so that the aspect ratio is preserved.

        Args:
        svg: The SVG document fragment to render.
        width: The width of the rendered image, in pixels. If `None`, the width
            attribute of the SVG element is used.
        height: The height of the rendered image, in pixels. If `None`, the
            height attribute of the SVG element is used.

        Returns:
        The rendered image.

        """
        return graphics.render(self, width=width, height=height)

    def show(self) -> None:
        """Render this SVG document fragment and display it on the screen.

        See `PIL.Image.Image.show` for more information.

        """
        self.render().show()

    def to_data_uri(self) -> str:
        """Convert the SVG document fragment to a base64-encoded data URI."""
        xml = self.to_xml(formatter=serialize.MINIMAL_FORMATTER)
        b64 = base64.b64encode(xml.encode()).decode()

        return f"data:image/svg+xml;base64,{b64}"
