import functools
import io

import PIL.Image
import resvg_py
from typing_extensions import cast


def _bytes_to_pillow(bytes_: bytes) -> PIL.Image.Image:
    fp = io.BytesIO(bytes_)

    return PIL.Image.open(fp)


@functools.lru_cache(maxsize=1)
def render(xml: str) -> PIL.Image.Image:
    """Render an SVG document fragment into a Pillow image.

    Args:
    xml: The SVG document fragment to render, as an XML string.

    Returns:
    The rendered image.

    """
    raw = cast(bytes, resvg_py.svg_to_bytes(svg_string=xml))

    return _bytes_to_pillow(raw)
