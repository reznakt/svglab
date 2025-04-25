"""Functions related to rendering and other graphics operations."""

import copy
import io
import uuid

import numpy as np
import numpy.typing as npt
import PIL.Image
import resvg_py
from typing_extensions import (
    Final,
    Protocol,
    TypeAlias,
    TypeVar,
    cast,
    runtime_checkable,
)

from svglab import errors, serialize
from svglab.attrparse import color, length
from svglab.elements import common
from svglab.utils import iterutils


Mask: TypeAlias = npt.NDArray[np.bool_]
BBox: TypeAlias = tuple[int, int, int, int]

_ImageArray: TypeAlias = npt.NDArray[np.uint8]

_TagT = TypeVar("_TagT", bound=common.Tag)

_BLACK: Final = color.Color((0, 0, 0))


@runtime_checkable
class _SvgTagLike(Protocol):
    width: length.Length | None
    height: length.Length | None

    def render(
        self, width: float | None = None, height: float | None = None
    ) -> PIL.Image.Image: ...


def _length_to_user_units(length: length.Length | None) -> float | None:
    """Convert a length to user units, if possible.

    Args:
        length: The length to convert, or `None`.

    Returns:
        The length in user units, or `None` if the length cannot be converted.

    """
    if length is None:
        return None

    try:
        return float(length)
    except errors.SvgUnitConversionError:
        return None


def render(  # noqa: D103
    svg: common.Tag,
    *,
    width: float | None = None,
    height: float | None = None,
) -> PIL.Image.Image:
    if not isinstance(svg, _SvgTagLike):
        raise TypeError("Tag must be an SVG element")

    svg_width = _length_to_user_units(svg.width)
    svg_height = _length_to_user_units(svg.height)

    if (
        width is not None
        and height is not None
        and svg_width is not None
        and svg_height is not None
        and width / height != svg_width / svg_height
    ):
        msg = (
            "Aspect ratio mismatch: "
            f"{svg.width=}, {svg.height=}, {width=}, {height=}"
        )
        raise ValueError(msg)

    if svg_width is not None and svg_height is not None:
        if width is not None and height is None:
            ratio = width / svg_width
            height = svg_height * ratio

        if width is None and height is not None:
            ratio = height / svg_height
            width = svg_width * ratio

    width = width if width is not None else svg_width
    height = height if height is not None else svg_height

    if width is None or height is None:
        msg = (
            "Unable to determine image dimensions: "
            f"{svg.width=}, {svg.height=}, {width=}, {height=}"
        )
        raise ValueError(msg)

    svg = copy.copy(svg)

    svg.width = length.Length(width)
    svg.height = length.Length(height)

    xml = svg.to_xml(formatter=serialize.MINIMAL_FORMATTER)
    raw = cast(bytes, resvg_py.svg_to_bytes(svg_string=xml))

    return PIL.Image.open(io.BytesIO(raw))


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
    svg = iterutils.take_last(tag.parents)

    if not isinstance(svg, _SvgTagLike):
        raise ValueError("Tag must be part of an SVG tree")  # noqa: TRY004

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
    width: float | None = None,
    height: float | None = None,
) -> PIL.Image.Image:
    """Resolve the root `Svg` tag and render the SVG tree to an image.

    Args:
        tag: The tag in the SVG tree to render.
        render_this: Whether to render the specified tag.
        render_other: Whether to render all other tags in the tree.
        make_tag_visible: Whether to attempt to make the specified tag visible,
            even if it would normally not be rendered (e.g., if due to a
            transparent fill).
        width: The width of the rendered image, in pixels. If `None`, the width
            attribute of the SVG element is used.
        height: The height of the rendered image, in pixels. If `None`, the
            height attribute of the SVG element is used.

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
    assert isinstance(svg, common.Tag)

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

    return svg.render(width=width, height=height)


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


def mask(  # noqa: D103
    tag: common.Tag,
    *,
    width: float | None = None,
    height: float | None = None,
) -> Mask:
    img = _render_tree(
        tag,
        render_this=True,
        render_other=False,
        make_tag_visible=True,
        width=width,
        height=height,
    )
    array: Mask = np.array(img)

    return array[:, :, 3] > 0  # alpha channel > 0


def visible_mask(  # noqa: D103
    tag: common.Tag,
    *,
    width: float | None = None,
    height: float | None = None,
) -> Mask:
    without_tag = _render_tree(
        tag,
        render_this=False,
        render_other=True,
        make_tag_visible=False,
        width=width,
        height=height,
    )

    with_tag = _render_tree(
        tag,
        render_this=True,
        render_other=True,
        make_tag_visible=False,
        width=width,
        height=height,
    )

    without_tag_array: _ImageArray = np.array(without_tag)
    with_tag_array: _ImageArray = np.array(with_tag)

    diff = np.any(without_tag_array != with_tag_array, axis=2)
    assert isinstance(diff, np.ndarray)

    return diff


def bbox(tag: common.Tag) -> BBox | None:  # noqa: D103
    img = _render_tree(
        tag, render_this=True, render_other=False, make_tag_visible=True
    )

    return img.getbbox()


def visible_bbox(tag: common.Tag) -> BBox | None:  # noqa: D103
    mask = visible_mask(tag)
    img = _mask_to_image(mask)

    return img.getbbox()
