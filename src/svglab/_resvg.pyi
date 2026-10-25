from svglab.resvg import RenderOptions

class RenderError(Exception): ...
class PanicError(BaseException): ...

def render(
    svg: str,
    options: RenderOptions,
    /,
    *,
    background: tuple[int, int, int, int] | None,
    zoom: float,
) -> tuple[int, int, bytes]: ...
