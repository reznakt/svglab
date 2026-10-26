"""Prepare the playground's interpreter: a renderer, a runner and completions.

The page runs this file in a namespace of its own once svglab is installed,
calls `setup`, and from then on talks to the interpreter only through `run`
and `complete`.
"""

import base64
import io
import linecache
import rlcompleter
import sys
import traceback
import types
from collections.abc import Callable

import PIL.Image
import pyodide.code  # pyright: ignore[reportMissingImports]
import pyodide.ffi  # pyright: ignore[reportMissingImports]

import __main__


_FILENAME = "<playground>"
_namespace = __main__.__dict__
_completer = rlcompleter.Completer(_namespace)


def setup(
    render: Callable[[str, str | None, float], pyodide.ffi.JsBuffer],
) -> None:
    """Put a renderer where svglab expects its compiled one.

    `svglab._resvg` is an extension module with no WebAssembly build, so a
    module of the same shape takes its place, backed by `render`: resvg
    compiled to WebAssembly. Only the background and the zoom are passed on;
    the other render options are ignored.

    Args:
        render: Renders a document to PNG, given its markup, a CSS
            background color or `None`, and a zoom factor.

    """

    class RenderError(Exception):
        """The document could not be rendered."""

    class PanicError(BaseException):
        """The renderer panicked; never raised here."""

    def render_pixels(
        svg: str,
        /,
        *,
        background: tuple[int, int, int, int] | None,
        zoom: float,
        **_options: object,
    ) -> tuple[int, int, bytes]:
        color = None

        if background is not None:
            red, green, blue, alpha = background
            color = f"rgba({red}, {green}, {blue}, {alpha / 255})"

        try:
            png = render(svg, color, zoom).to_bytes()
        except pyodide.ffi.JsException as error:
            raise RenderError(str(error)) from error

        image = PIL.Image.open(io.BytesIO(png)).convert("RGBA")

        return *image.size, image.tobytes()

    module = types.ModuleType("svglab._resvg")
    module.__dict__.update(
        RenderError=RenderError,
        PanicError=PanicError,
        render=render_pixels,
    )
    sys.modules[module.__name__] = module


async def run(source: str) -> str | None:
    """Run code in the namespace shared by every run.

    A traceback is printed without the interpreter's own frames, and a value
    on the last line is printed the way the REPL would print it.

    Args:
        source: The code to run.

    Returns:
        The value of the last line as a PNG data URL if it is an image,
        otherwise `None`.

    """
    # gives the frames of the code their source lines in a traceback
    linecache.cache[_FILENAME] = (
        len(source),
        None,
        source.splitlines(keepends=True),
        _FILENAME,
    )

    try:
        result = await pyodide.code.eval_code_async(
            source, _namespace, filename=_FILENAME
        )
    except BaseException as error:  # ruff: ignore[BLE001]
        frames = error.__traceback__

        while frames and frames.tb_frame.f_code.co_filename != _FILENAME:
            frames = frames.tb_next

        traceback.print_exception(error.with_traceback(frames))

        return None

    if not isinstance(result, PIL.Image.Image):
        if result is not None:
            print(repr(result))

        return None

    buffer = io.BytesIO()
    result.save(buffer, format="PNG")

    return "data:image/png;base64," + base64.b64encode(
        buffer.getvalue()
    ).decode("ascii")


def complete(prefix: str) -> list[str]:
    """Complete a name, or an attribute of an object, from the namespace.

    Args:
        prefix: The name or the dotted expression to complete, such as
            `svg.fi`.

    Returns:
        The completions in full, with `(` appended to the callable ones.

    """
    if "." in prefix:
        return _completer.attr_matches(prefix)

    return _completer.global_matches(prefix)
