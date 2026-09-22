import os
from collections.abc import Sequence

from typing_extensions import TypeAlias

from svglab.attrs.typedefs import (
    ImageRendering,
    ShapeRendering,
    TextRendering,
)

_Path: TypeAlias = str | os.PathLike[str]

class RenderError(Exception): ...
class PanicError(BaseException): ...

def render(
    svg: str,
    /,
    *,
    background: tuple[int, int, int, int] | None,
    cursive_family: str | None,
    default_size: tuple[float, float],
    dpi: float,
    fantasy_family: str | None,
    font_dirs: Sequence[_Path],
    font_family: str | None,
    font_files: Sequence[_Path],
    font_size: float,
    image_rendering: ImageRendering,
    languages: Sequence[str],
    monospace_family: str | None,
    resources_dir: _Path | None,
    sans_serif_family: str | None,
    serif_family: str | None,
    shape_rendering: ShapeRendering,
    skip_system_fonts: bool,
    style_sheet: str | None,
    text_rendering: TextRendering,
    zoom: float,
) -> tuple[int, int, bytes]: ...
