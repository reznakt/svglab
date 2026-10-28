"""Prepare the playground's interpreter: a renderer, a runner and a console.

The page runs this file in a namespace of its own once svglab is installed,
and from then on talks to the interpreter through the `Session` that `setup`
returns.
"""

import base64
import io
import linecache
import re
import sys
import traceback
import types
from collections.abc import Callable

import PIL.Image
import pyodide.code  # pyright: ignore[reportMissingImports]
import pyodide.console  # pyright: ignore[reportMissingImports]
import pyodide.ffi  # pyright: ignore[reportMissingImports]
from typing_extensions import TYPE_CHECKING

import __main__


if TYPE_CHECKING:
    import jedi  # pyright: ignore[reportMissingImports]


_FILENAME = "<playground>"

# element classes take every attribute as an argument; past this, a hover
# shows only the name
_LONGEST_SIGNATURE = 200


def _one_line(signature: str) -> str:
    """Join a signature that its source spreads over several lines."""
    signature = re.sub(r"\s*\n\s*", " ", signature)

    # the spaces and trailing commas the line breaks leave inside brackets
    return re.sub(r"(?<=[\[(]) | (?=[\])])|,(?= ?[\])])", "", signature)


def _markdown(docstring: str) -> str:
    """Render a docstring as Markdown, keeping its lines and indentation.

    Markdown would join the lines of a section such as `Args:` into one
    paragraph, and turn its indented lines into code blocks.

    Args:
        docstring: The docstring to render.

    Returns:
        The docstring as Markdown.

    """
    return "  \n".join(
        re.sub(r"^ +", lambda spaces: "&nbsp;" * len(spaces[0]), line)
        for line in docstring.splitlines()
    )


def _parameter_docs(docstring: str) -> dict[str, str]:
    """Split the `Args:` section of a docstring by parameter.

    Args:
        docstring: The docstring, in the Google style.

    Returns:
        The description of each parameter, as Markdown, by its name.

    """
    docs: dict[str, list[str]] = {}
    current = None
    lines = iter(docstring.splitlines())

    for line in lines:
        if line == "Args:":
            break

    for line in lines:
        if line and not line.startswith(" "):
            break  # the next section

        if entry := re.fullmatch(r" {4}\**(\w+): (.*)", line):
            current = docs[entry[1]] = [entry[2]]
        elif current is not None:
            current.append(line.removeprefix(" " * 8))

    return {
        name: _markdown("\n".join(text).strip())
        for name, text in docs.items()
    }


def _column(line: str, offset: int | None) -> int:
    """Turn a frame's UTF-8 offset from 0 into Monaco's column from 1."""
    if offset is None:
        return 0

    return len(line.encode()[:offset].decode(errors="ignore")) + 1


def _locate(error: BaseException, source: str) -> dict[str, object] | None:
    """Find where in the code an exception was raised.

    Args:
        error: The exception.
        source: The code that raised it.

    Returns:
        The span of the innermost expression of the code that raised the
        exception, or of the syntax error, and the exception's message, as a
        marker of Monaco's; `None` if the code is not to blame.

    """
    lines = [*source.splitlines(), ""]

    if isinstance(error, SyntaxError):
        if error.filename != _FILENAME or error.lineno is None:
            return None

        start = (error.lineno, error.offset or 1)
        end = (error.end_lineno or start[0], error.end_offset or 0)
    else:
        frame = next(
            (
                frame
                for frame in reversed(
                    traceback.extract_tb(error.__traceback__)
                )
                if frame.filename == _FILENAME
            ),
            None,
        )

        if frame is None or frame.lineno is None:
            return None

        end_line = frame.end_lineno or frame.lineno
        start = (
            frame.lineno,
            _column(lines[frame.lineno - 1], frame.colno) or 1,
        )
        end = (end_line, _column(lines[end_line - 1], frame.end_colno))

    # a span with no width would not show, so the whole line stands for it
    if end <= start:
        end = (start[0], len(lines[start[0] - 1]) + 1)

    return {
        "message": traceback.format_exception_only(error)[-1].strip(),
        "startLineNumber": start[0],
        "startColumn": start[1],
        "endLineNumber": end[0],
        "endColumn": end[1],
    }


class Session:
    """Runs the code in the editor, with a console on what it leaves behind."""

    def __init__(self, show_image: Callable[[str], object]) -> None:
        """Start a session in the interpreter's main namespace.

        Args:
            show_image: Displays an image, given as a PNG data URL.

        """
        self._show_image = show_image
        self._namespace = __main__.__dict__
        self._pristine = dict(self._namespace)
        self._console = pyodide.console.Console(self._namespace)

    def _display(self, value: object) -> None:
        """Print a value the way the REPL would, or display it if an image."""
        if isinstance(value, PIL.Image.Image):
            buffer = io.BytesIO()
            value.save(buffer, format="PNG")
            data = base64.b64encode(buffer.getvalue()).decode("ascii")
            self._show_image(f"data:image/png;base64,{data}")
        elif value is not None:
            print(repr(value))

    async def run(self, source: str) -> dict[str, object] | None:
        """Run code in a fresh namespace, which the console then works in.

        A traceback is printed without the interpreter's own frames, and a
        value on the last line is displayed.

        Args:
            source: The code to run.

        Returns:
            Where the code raised an exception, as a marker of Monaco's, or
            `None` if it raised none.

        """
        self.reset()

        # gives the frames of the code their source lines in a traceback
        linecache.cache[_FILENAME] = (
            len(source),
            None,
            source.splitlines(keepends=True),
            _FILENAME,
        )

        try:
            result = await pyodide.code.eval_code_async(
                source, self._namespace, filename=_FILENAME
            )
        except BaseException as error:  # ruff: ignore[BLE001]
            frames = error.__traceback__

            while (
                frames and frames.tb_frame.f_code.co_filename != _FILENAME
            ):
                frames = frames.tb_next

            traceback.print_exception(error.with_traceback(frames))

            return _locate(error, source)
        else:
            self._display(result)

        return None

    def reset(self) -> None:
        """Empty the namespace, and drop an unfinished console statement."""
        self._namespace.clear()
        self._namespace.update(self._pristine)
        self._console.buffer.clear()

    async def push(self, line: str) -> bool:
        """Enter a line into the console.

        Args:
            line: The line, without its trailing newline.

        Returns:
            Whether the statement is unfinished and the console waits for
            more lines.

        """
        future = self._console.push(line)

        if future.syntax_check == "incomplete":
            return True

        try:
            self._display(await future)
        except BaseException:  # ruff: ignore[BLE001]
            print(future.formatted_error, end="", file=sys.stderr)

        return False

    def _jedi(self, source: str) -> "jedi.Interpreter":
        """Analyze code with Jedi, which knows the namespace too.

        Names are therefore resolved before a run from the code, and after it
        from the objects the run made as well.

        Args:
            source: The code.

        Returns:
            Jedi's view of the code.

        """
        # the worker loads Jedi only once the session is ready to run code
        import jedi  # pyright: ignore[reportMissingImports]  # ruff: ignore[PLC0415]

        return jedi.Interpreter(source, [self._namespace])

    def complete(
        self, source: str, line: int, column: int
    ) -> list[dict[str, str]]:
        """Complete the name at a position in the code.

        Args:
            source: The code.
            line: The line of the position, counted from 1.
            column: The column of the position, counted from 0.

        Returns:
            The completions, best first: each name, with `=` after a keyword
            argument's, and its kind, such as `function` or `param`.

        """
        # Jedi gives up on some code, and a completion is not worth an error
        try:
            completions = self._jedi(source).complete(line, column)
        except Exception:  # ruff: ignore[BLE001]
            return []

        return [
            {"name": completion.name_with_symbols, "kind": completion.type}
            for completion in completions
            if completion.type != "path"
        ]

    def signatures(
        self, source: str, line: int, column: int
    ) -> dict[str, object] | None:
        """Document the call around a position in the code, for its arguments.

        Args:
            source: The code.
            line: The line of the position, counted from 1.
            column: The column of the position, counted from 0.

        Returns:
            The signatures of what is called, with the docs of each parameter
            and the one being entered, as a `SignatureHelp` of Monaco's;
            `None` outside of a call, or if its signatures are too long to
            show, as those of the element classes are.

        """
        try:
            found = self._jedi(source).get_signatures(line, column)
        except Exception:  # ruff: ignore[BLE001]
            return None

        signatures = []

        for signature in found:
            label = _one_line(signature.to_string())

            if len(label) > _LONGEST_SIGNATURE:
                continue

            docstring = signature.docstring(raw=True)
            docs = _parameter_docs(docstring)
            summary = docstring.split("\n\n", 1)[0]
            parameters = []
            end = label.index("(")

            # each parameter as the span of the label it takes up
            for parameter in signature.params:
                text = _one_line(parameter.to_string())
                start = label.find(text, end)

                if start >= 0:
                    end = start + len(text)

                doc = docs.get(parameter.name)
                parameters.append(
                    {
                        "label": [start, end] if start >= 0 else [0, 0],
                        "documentation": {"value": doc} if doc else None,
                    }
                )

            signatures.append(
                {
                    "label": label,
                    "documentation": {"value": summary}
                    if summary
                    else None,
                    "parameters": parameters,
                    "activeParameter": (
                        -1 if signature.index is None else signature.index
                    ),
                }
            )

        if not signatures:
            return None

        return {"signatures": signatures, "activeSignature": 0}

    def describe(self, source: str, line: int, column: int) -> str | None:
        """Document the name at a position in the code, as Markdown.

        Args:
            source: The code.
            line: The line of the name, counted from 1.
            column: The column of the name, counted from 0.

        Returns:
            The signatures and the docstring of what the name refers to, or
            `None` if it refers to nothing Jedi can find.

        """
        try:
            names = self._jedi(source).help(line, column)
        except Exception:  # ruff: ignore[BLE001]
            return None

        if not names:
            return None

        name = names[0]
        signatures = [
            _one_line(signature.to_string())
            if len(_one_line(signature.to_string())) <= _LONGEST_SIGNATURE
            else f"{name.name}(...)"
            for signature in name.get_signatures()
        ]
        parts = [
            "```python\n"
            + ("\n".join(signatures) or name.description)
            + "\n```"
        ]

        if docstring := name.docstring(raw=True):
            parts.append(_markdown(docstring))

        return "\n\n".join(parts)


def setup(
    render: Callable[[str, str | None, float], pyodide.ffi.JsBuffer],
    show_image: Callable[[str], object],
) -> Session:
    """Put a renderer where svglab expects its compiled one; start a session.

    `svglab._resvg` is an extension module with no WebAssembly build, so a
    module of the same shape takes its place, backed by `render`: resvg
    compiled to WebAssembly. Only the background and the zoom are passed on;
    the other render options are ignored.

    Args:
        render: Renders a document to PNG, given its markup, a CSS
            background color or `None`, and a zoom factor.
        show_image: Displays an image, given as a PNG data URL.

    Returns:
        The session the page runs code in.

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

    return Session(show_image)
