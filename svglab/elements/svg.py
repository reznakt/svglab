import contextlib
import os
import pathlib

from typing_extensions import final, overload

from svglab import protocols, serialize
from svglab.attrs import groups, regular
from svglab.elements import traits


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
