import copy
import functools
import io
import uuid

import numpy as np
import numpy.typing as npt
import PIL.Image
import PIL.ImageChops
import resvg_py
from typing_extensions import (
    Final,
    Protocol,
    TypeAlias,
    TypeIs,
    TypeVar,
    cast,
    runtime_checkable,
)

from svglab import utils
from svglab.attrparse import color
from svglab.elements import common


Mask: TypeAlias = npt.NDArray[np.bool_]
BBox: TypeAlias = tuple[int, int, int, int]

_SvgTagLike: TypeAlias = common.Tag
_ImageArray: TypeAlias = npt.NDArray[np.uint8]

_TagT = TypeVar("_TagT", bound=common.Tag)

_BLACK: Final = color.Color((0, 0, 0))


@runtime_checkable
class _SupportsRender(Protocol):
    def render(self) -> PIL.Image.Image: ...


def _looks_like_svg(value: object) -> TypeIs[_SvgTagLike]:
    """Check if a value looks like an SVG tag.

    Acts as a type guard for `_SvgTag`.

    Args:
        value: The value to check.

    Returns:
        `True` if the value looks like an SVG tag, otherwise `False`.

    """
    return isinstance(value, _SvgTagLike) and type(value).__name__ == "Svg"


def _bytes_to_pillow(bytes_: bytes) -> PIL.Image.Image:
    """Convert a byte string to a Pillow image.

    Args:
        bytes_: The byte string to convert.

    Returns:
        A Pillow image.

    """
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


def _copy_tree(tag: _TagT) -> tuple[_TagT, _SvgTagLike]:
    """Resolve the root `Svg` tag and create a deep copy of the SVG tree.

    The source tag is identified in the copied tree and returned for easy
    access.

    Args:
        tag: The tag in the SVG tree to copy.

    Returns:
        A tuple of the copied tag and the root `Svg` tag of the copied tree.

    Raises:
        ValueError: If the tag is not a part of an SVG tree.

    """
    svg = utils.take_last(tag.parents)

    if not _looks_like_svg(svg):
        raise ValueError("Tag must be a part of an SVG tree")

    original_id = tag.id
    tag.id = uuid.uuid4().hex

    try:
        svg = copy.deepcopy(svg)

        candidates = svg.find_all(type(tag))

        this = next(tag for tag in candidates if tag.id == tag.id)
    finally:
        tag.id = original_id

    return this, svg


def _render_tree(
    tag: common.Tag,
    *,
    render_this: bool,
    render_other: bool,
    make_tag_visible: bool,
) -> PIL.Image.Image:
    """Resolve the root `Svg` tag and render the SVG tree to an image.

    Args:
        tag: The tag in the SVG tree to render.
        render_this: Whether to render the specified tag.
        render_other: Whether to render all other tags in the tree.
        make_tag_visible: Whether to attempt to make the specified tag visible,
            even if it would normally not be rendered (e.g., if due to a
            transparent fill).

    Returns:
        The rendered image.

    Raises:
        ValueError: If `make_tag_visible` is `True` and `render_this`
        is `False`.

    """
    if make_tag_visible and not render_this:
        raise ValueError(
            "make_tag_visible cannot be True if render_this is False"
        )

    tag_copy, svg = _copy_tree(tag)

    for t in svg.find_all():
        t.visibility = "visible" if render_other else "hidden"

    tag_copy.visibility = "visible" if render_this else "hidden"

    if make_tag_visible:
        del tag_copy.display
        tag_copy.fill = _BLACK
        tag_copy.fill_opacity = 1
        tag_copy.opacity = 1
        tag_copy.stroke = _BLACK
        tag_copy.stroke_opacity = 1
        tag_copy.visibility = "visible"

    assert isinstance(svg, _SupportsRender)
    return svg.render()


def _mask_to_image(mask: Mask) -> PIL.Image.Image:
    """Convert boolean mask into an RGBA image.

    Areas where the mask is True are set to solid black. All other areas are
    fully transparent. This allows convenient use with
    `PIL.Image.Image.getbbox()`.

    Args:
        mask: A boolean mask given as an NDArray of shape (x, y), where x
            and y are the dimensions of the resulting image.

    Returns:
        An RGBA image representing the mask.

    """
    x, y = mask.shape

    # create fully transparent image
    rgba: _ImageArray = np.zeros((x, y, 4), dtype=np.uint8)

    # set to solid black where mask is True
    rgba[mask, 3] = 255

    return PIL.Image.fromarray(rgba)


def mask(tag: common.Tag) -> Mask:
    img = _render_tree(
        tag, render_this=True, render_other=False, make_tag_visible=True
    )
    array: Mask = np.array(img)

    return array[:, :, 3] > 0  # alpha channel > 0


def visible_mask(tag: common.Tag) -> Mask:
    without_tag = _render_tree(
        tag, render_this=False, render_other=True, make_tag_visible=False
    )

    with_tag = _render_tree(
        tag, render_this=True, render_other=True, make_tag_visible=False
    )

    without_tag_array: _ImageArray = np.array(without_tag)
    with_tag_array: _ImageArray = np.array(with_tag)

    diff = np.any(without_tag_array != with_tag_array, axis=2)
    assert isinstance(diff, np.ndarray)

    return diff


def bbox(tag: common.Tag) -> BBox | None:
    img = _render_tree(
        tag, render_this=True, render_other=False, make_tag_visible=True
    )

    return img.getbbox()


def visible_bbox(tag: common.Tag) -> BBox | None:
    mask = visible_mask(tag)
    img = _mask_to_image(mask)

    return img.getbbox()
