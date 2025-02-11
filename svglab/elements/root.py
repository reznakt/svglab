import contextlib
import os
import pathlib

import PIL.Image
from typing_extensions import overload

from svglab import graphics, protocols, serialize
from svglab.elements import traits


class RootElement(traits.Element):
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

    def render(
        self, *, width: float | None = None, height: float | None = None
    ) -> PIL.Image.Image:
        """Render an SVG document fragment into a Pillow image.

        If the width and height are not specified, the dimensions of the SVG
        element are used. If only one dimension is specified, the other
        dimension is calculated in a way that preserves the aspect ratio set
        in the SVG element. If both dimensions are specified, the aspect ratio
        must match the aspect ratio defined by `width` and `height` attributes
        of the SVG element.

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
