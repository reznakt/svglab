import contextlib
import os
import pathlib
from typing import final, overload

import pydantic

from svglab import attrs, constants, models, serialize, types
from svglab.elements import common

__all__ = ["G", "Rect", "Svg"]


class CommonAttrs(pydantic.BaseModel):
    id: models.Attr[str] = None
    class_: models.Attr[str] = None
    color: models.Attr[attrs.ColorType] = None


class GeometricAttrs(pydantic.BaseModel):
    x: models.Attr[float] = None
    y: models.Attr[float] = None
    width: models.Attr[attrs.LengthType] = None
    height: models.Attr[attrs.LengthType] = None
    transform: models.Attr[attrs.TransformType] = None


@final
class Rect(CommonAttrs, GeometricAttrs, common.Tag):
    pass


@final
class G(CommonAttrs, common.PairedTag):
    pass


@final
class Svg(CommonAttrs, common.PairedTag):
    xmlns: models.Attr[str] = constants.DEFAULT_XMLNS

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
