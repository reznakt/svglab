from typing_extensions import final

from svglab.resvg import RenderOptions

class RenderError(Exception): ...
class PanicError(BaseException): ...

@final
class Pixels:
    @property
    def width(self) -> int: ...
    @property
    def height(self) -> int: ...
    def __buffer__(self, flags: int, /) -> memoryview: ...

def render(
    svg: str,
    options: RenderOptions,
    /,
    *,
    background: tuple[int, int, int, int] | None,
    zoom: float,
) -> Pixels: ...
