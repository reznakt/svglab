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

from svglab import entities, errors, serialize
from svglab.attrparse import color, length
from svglab.utils import iterutils


Mask: TypeAlias = npt.NDArray[np.bool_]
BBox: TypeAlias = tuple[int, int, int, int]

_ImageArray: TypeAlias = npt.NDArray[np.uint8]

_ElementT = TypeVar("_ElementT", bound=entities.Element)

_BLACK: Final = color.Color((0, 0, 0))


@runtime_checkable
class _SvgElementLike(Protocol):
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


def _compute_render_size(
    svg: entities.Element,
    *,
    width: float | None = None,
    height: float | None = None,
) -> tuple[float, float]:
    if not isinstance(svg, _SvgElementLike):
        msg = "Svg must be an instance of _SvgElementLike"
        raise TypeError(msg)

    svg_width = _length_to_user_units(length=svg.width)
    svg_height = _length_to_user_units(svg.height)

    if svg_width is not None and svg_height is not None:
        if width is not None and height is None:
            ratio = width / svg_width
            height = svg_height * ratio
        elif width is None and height is not None:
            ratio = height / svg_height
            width = svg_width * ratio
        elif width is not None and height is not None:
            ratio = (svg_width / svg_height) / (width / height)

            if ratio > 1:
                height = height / ratio
            elif ratio < 1:
                width = width / ratio

    width = width if width is not None else svg_width
    height = height if height is not None else svg_height

    if width is None or height is None:
        msg = (
            "Unable to determine image dimensions: "
            f"{svg.width=}, {svg.height=}, {width=}, {height=}"
        )
        raise ValueError(msg)

    return width, height


def render(  # noqa: D103
    svg: entities.Element,
    *,
    width: float | None = None,
    height: float | None = None,
) -> PIL.Image.Image:
    if not isinstance(svg, _SvgElementLike):
        raise TypeError("Element must be an SVG element")

    render_size = _compute_render_size(svg, width=width, height=height)
    svg = copy.copy(svg)

    svg.width = length.Length(render_size[0])
    svg.height = length.Length(render_size[1])

    xml = svg.to_xml(formatter=serialize.MINIMAL_FORMATTER)
    raw = cast(bytes, resvg_py.svg_to_bytes(svg_string=xml))

    return PIL.Image.open(io.BytesIO(raw))


def _copy_tree(element: _ElementT) -> tuple[_ElementT, _SvgElementLike]:
    """Resolve the root `Svg` element and create a deep copy of the SVG tree.

    The source element is identified in the copied tree and returned for easy
    access.

    Args:
        element: The element in the SVG tree to copy.

    Returns:
        A tuple of the copied element and the root `Svg` element of the copied
        tree.

    Raises:
        ValueError: If the element is not a part of an SVG tree.

    """
    svg = iterutils.take_last(element.ancestors)

    if not isinstance(svg, _SvgElementLike):
        raise ValueError("Element must be part of an SVG tree")  # noqa: TRY004

    original_id = element.id
    element.id = uuid.uuid4().hex

    try:
        svg = copy.deepcopy(svg)
        candidates = svg.find_all(type(element))
        this = next(
            element for element in candidates if element.id == element.id
        )
    finally:
        element.id = original_id

    return this, svg


def _make_element_visible(element: entities.Element, /) -> None:
    del element.display
    element.fill = _BLACK
    element.fill_opacity = 1
    element.opacity = 1
    element.stroke = _BLACK
    element.stroke_opacity = 1
    element.visibility = "visible"

    for child in element.find_all(recursive=False):
        _make_element_visible(child)


def _render_tree(
    element: entities.Element,
    *,
    render_this: bool,
    render_other: bool,
    make_element_visible: bool,
    width: float | None = None,
    height: float | None = None,
) -> PIL.Image.Image:
    """Resolve the root `Svg` element and render the SVG tree to an image.

    Args:
        element: The element in the SVG tree to render.
        render_this: Whether to render the specified element.
        render_other: Whether to render all other elements in the tree.
        make_element_visible: Whether to attempt to make the specified element
            visible, even if it would normally not be rendered (e.g., if due
            to a transparent fill).
        width: The width of the rendered image, in pixels. If `None`, the width
            attribute of the SVG element is used.
        height: The height of the rendered image, in pixels. If `None`, the
            height attribute of the SVG element is used.

    Returns:
        The rendered image.

    Raises:
        ValueError: If `make_element_visible` is `True` and `render_this`
        is `False`.

    """
    if make_element_visible and not render_this:
        raise ValueError(
            "make_element_visible cannot be True if render_this is False"
        )

    element_copy, svg = _copy_tree(element)
    assert isinstance(svg, entities.Element)

    for t in svg.find_all():
        # do not hide the parents of our element as that would make it
        # invisible
        # TODO: this is quite suboptimal performance-wise; optimize this
        if render_other or t in element_copy.ancestors:
            t.visibility = "visible"
        else:
            t.visibility = "hidden"

    element_copy.visibility = "visible" if render_this else "hidden"

    if make_element_visible:
        _make_element_visible(element_copy)

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
    element: entities.Element,
    *,
    width: float | None = None,
    height: float | None = None,
) -> Mask:
    img = _render_tree(
        element,
        render_this=True,
        render_other=False,
        make_element_visible=True,
        width=width,
        height=height,
    )
    array: Mask = np.array(img)

    return array[:, :, 3] > 0  # alpha channel > 0


def visible_mask(  # noqa: D103
    element: entities.Element,
    *,
    width: float | None = None,
    height: float | None = None,
) -> Mask:
    without_element = _render_tree(
        element,
        render_this=False,
        render_other=True,
        make_element_visible=False,
        width=width,
        height=height,
    )

    with_element = _render_tree(
        element,
        render_this=True,
        render_other=True,
        make_element_visible=False,
        width=width,
        height=height,
    )

    without_element_array: _ImageArray = np.array(without_element)
    with_element_array: _ImageArray = np.array(with_element)

    diff = np.any(without_element_array != with_element_array, axis=2)
    assert isinstance(diff, np.ndarray)

    return diff


def bbox(element: entities.Element) -> BBox | None:  # noqa: D103
    img = _render_tree(
        element,
        render_this=True,
        render_other=False,
        make_element_visible=True,
    )

    return img.getbbox()


def visible_bbox(element: entities.Element) -> BBox | None:  # noqa: D103
    mask = visible_mask(element)
    img = _mask_to_image(mask)

    return img.getbbox()
