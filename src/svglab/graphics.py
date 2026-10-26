"""Functions related to rendering and other graphics operations."""

import copy
import itertools
from collections.abc import Iterator

import numpy as np
import numpy.typing as npt
import PIL.Image
from typing_extensions import (
    Final,
    Literal,
    Protocol,
    TypeAlias,
    TypeIs,
    TypeVar,
    cast,
    runtime_checkable,
)

from svglab.attrparse.color import Color
from svglab.attrparse.length import Length
from svglab.entities import Element
from svglab.errors import SvgUnitConversionError
from svglab.resvg import RenderOptions, render_array
from svglab.resvg import render as resvg_render
from svglab.serialize import MINIMAL_FORMATTER


Mask: TypeAlias = npt.NDArray[np.bool_]
BBox: TypeAlias = tuple[int, int, int, int]

_ImageArray: TypeAlias = npt.NDArray[np.uint8]

_ElementT = TypeVar("_ElementT", bound=Element)


_BLACK: Final = Color((0, 0, 0))


@runtime_checkable
class _SvgElementLike(Protocol):
    width: Length | None
    height: Length | None
    viewBox: tuple[float, float, float, float] | None  # ruff: ignore[N815]

    def render(
        self,
        options: RenderOptions | None = None,
        *,
        background: Color | None = None,
        height: float | None = None,
        width: float | None = None,
        zoom: float = 1,
    ) -> PIL.Image.Image: ...


_SVG_ELEMENT_LIKE_CLASSES: Final[set[type]] = set()


def _is_svg_element_like(element: object, /) -> TypeIs[_SvgElementLike]:
    """Check whether an object is an `_SvgElementLike`, but quickly.

    `isinstance` against a runtime-checkable protocol looks every member up
    with `inspect.getattr_static`, which walks the whole MRO of the class, and
    an element's many mixins make that take hundreds of microseconds. So the
    class is checked once, and only the fields, which can be deleted from an
    element, are checked every time.

    Args:
        element: The object to check.

    Returns:
        Whether `isinstance(element, _SvgElementLike)` holds.

    """
    if type(element) not in _SVG_ELEMENT_LIKE_CLASSES:
        if not isinstance(element, _SvgElementLike):
            return False

        _SVG_ELEMENT_LIKE_CLASSES.add(type(element))

    return all(
        hasattr(element, name) for name in ("width", "height", "viewBox")
    )


def _positive_user_units(value: Length | None, /) -> float | None:
    """Convert a length to a positive number of user units, if possible.

    Args:
        value: The length to convert, or `None`.

    Returns:
        The length in user units, or `None` if the length cannot be
        converted or is not positive.

    Examples:
        >>> from svglab import Length
        >>> _positive_user_units(Length(1.5))
        1.5
        >>> _positive_user_units(Length(1.5, "px"))
        1.5
        >>> _positive_user_units(Length(0))
        >>> _positive_user_units(Length(-1))
        >>> _positive_user_units(Length(50, "%"))
        >>> _positive_user_units(None)

    """
    if value is None:
        return None

    try:
        user_units = float(value)
    except SvgUnitConversionError:
        return None

    return user_units if user_units > 0 else None


def _viewbox_size(
    viewbox: tuple[float, float, float, float] | None, /
) -> tuple[float, float] | None:
    """Extract the width and height of a viewBox, if they are positive.

    Args:
        viewbox: The viewBox to extract the dimensions from, or `None`.

    Returns:
        The width and height of the viewBox, or `None` if the viewBox is
        `None` or does not define a positive area.

    Examples:
        >>> _viewbox_size((-10, 0, 930, 1000))
        (930.0, 1000.0)
        >>> _viewbox_size((0, 0, 0, 100))
        >>> _viewbox_size(None)

    """
    if viewbox is None:
        return None

    _, _, width, height = viewbox

    if width <= 0 or height <= 0:
        return None

    return float(width), float(height)


def _compute_render_size(
    svg: Element,
    *,
    width: float | None = None,
    height: float | None = None,
) -> tuple[float, float]:
    """Compute the render size of an SVG element.

    The function takes into account the width and height attributes of the
    SVG element, as well as the specified width and height parameters. If
    only one of the width or height parameters is provided, the other
    dimension is computed to preserve the aspect ratio of the SVG element.

    A missing width or height attribute defaults to `100%`, which is
    resolved against the viewBox, if there is one. The viewBox therefore
    provides both the fallback size and the fallback aspect ratio of the
    SVG element.

    Args:
        svg: The SVG element to compute the render size for.
        width: The desired width of the rendered image, in pixels. If `None`,
            the width attribute of the SVG element is used.
        height: The desired height of the rendered image, in pixels. If `None`,
            the height attribute of the SVG element is used.

    Returns:
        A tuple containing the computed width and height of the rendered image,
        in pixels.

    Raises:
        TypeError: If the provided `svg` is not an instance of
            `_SvgElementLike`.
        ValueError: If the width and height cannot be determined from the SVG
            element or the provided parameters.

    Examples:
        >>> from svglab import Svg, Length
        >>> svg = Svg(width=Length(100), height=Length(200))
        >>> _compute_render_size(svg, width=50)
        (50.0, 100.0)
        >>> _compute_render_size(svg, height=100)
        (50.0, 100.0)
        >>> _compute_render_size(svg, width=50, height=100)
        (50.0, 100.0)
        >>> _compute_render_size(svg, width=50, height=1000)
        (50.0, 100.0)
        >>> _compute_render_size(svg)
        (100.0, 200.0)
        >>> _compute_render_size(Svg())  # doctest: +ELLIPSIS
        Traceback (most recent call last):
            ...
        ValueError: Unable to determine image dimensions: ...
        >>> _compute_render_size(Svg(width=Length(0), height=Length(0)))
        Traceback (most recent call last):
            ...
        ValueError: Unable to determine image dimensions: ...
        >>> _compute_render_size(Svg(viewBox=(-10, 0, 930, 1000)))
        (930.0, 1000.0)
        >>> _compute_render_size(
        ...     Svg(viewBox=(-10, 0, 930, 1000)), width=930
        ... )
        (930.0, 1000.0)
        >>> _compute_render_size(
        ...     Svg(height=Length(500), viewBox=(0, 0, 100, 200))
        ... )
        (250.0, 500.0)
        >>> _compute_render_size(svg, width=0)
        Traceback (most recent call last):
            ...
        ValueError: Image dimensions must be positive: width=0, height=None

    """
    if not _is_svg_element_like(svg):
        msg = "Svg must be an instance of _SvgElementLike"
        raise TypeError(msg)

    if (width is not None and width <= 0) or (
        height is not None and height <= 0
    ):
        msg = f"Image dimensions must be positive: {width=}, {height=}"
        raise ValueError(msg)

    # a non-positive dimension carries no aspect ratio; treat it as missing
    svg_width = _positive_user_units(svg.width)
    svg_height = _positive_user_units(svg.height)
    viewbox = _viewbox_size(svg.viewBox)

    if (svg_width is None or svg_height is None) and viewbox is not None:
        vb_width, vb_height = viewbox

        if svg_height is not None:
            svg_width = svg_height * vb_width / vb_height
        elif svg_width is not None:
            svg_height = svg_width * vb_height / vb_width
        else:
            svg_width, svg_height = vb_width, vb_height

    if svg_width is not None and svg_height is not None:
        # fit the SVG into the requested dimensions, preserving the aspect
        # ratio; an unspecified dimension does not constrain the fit
        scales = [
            requested / available
            for requested, available in (
                (width, svg_width),
                (height, svg_height),
            )
            if requested is not None
        ]

        if scales:
            scale = min(scales)
            width = svg_width * scale
            height = svg_height * scale

    width = width if width is not None else svg_width
    height = height if height is not None else svg_height

    if width is None or height is None:
        msg = (
            "Unable to determine image dimensions: "
            f"{svg.width=}, {svg.height=}, {svg.viewBox=}, "
            f"{width=}, {height=}"
        )
        raise ValueError(msg)

    return width, height


def _serialize_for_render(
    svg: Element, *, width: float | None, height: float | None
) -> str:
    """Serialize an SVG element with the size it is to be rendered at.

    Args:
        svg: The SVG element to serialize.
        width: The width of the rendered image, in pixels, or `None`.
        height: The height of the rendered image, in pixels, or `None`.

    Returns:
        The XML of a copy of the element, its size set to the render size.

    Raises:
        TypeError: If the element is not an SVG element.

    """
    if not _is_svg_element_like(svg):
        raise TypeError("Element must be an SVG element")

    render_size = _compute_render_size(svg, width=width, height=height)
    svg = copy.copy(svg)

    svg.width = Length(render_size[0])
    svg.height = Length(render_size[1])

    return svg.to_xml(formatter=MINIMAL_FORMATTER)


def render(  # ruff: ignore[D103]
    svg: Element,
    options: RenderOptions | None = None,
    *,
    background: Color | None = None,
    height: float | None = None,
    width: float | None = None,
    zoom: float = 1,
) -> PIL.Image.Image:
    xml = _serialize_for_render(svg, width=width, height=height)

    return resvg_render(xml, options, background=background, zoom=zoom)


def _render_pixels(
    svg: Element, *, width: float | None, height: float | None
) -> _ImageArray:
    """Render an SVG element with the default options, without a copy.

    Args:
        svg: The SVG element to render.
        width: The width of the rendered image, in pixels, or `None`.
        height: The height of the rendered image, in pixels, or `None`.

    Returns:
        The pixels, as `render_array` returns them.

    """
    return render_array(
        _serialize_for_render(svg, width=width, height=height)
    )


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
    svg = element.get_root()

    if not _is_svg_element_like(svg):
        raise ValueError("Element must be part of an SVG tree")

    memo: dict[int, object] = {}
    svg = copy.deepcopy(svg, memo)
    this = cast(_ElementT, memo[id(element)])

    return this, svg


def _iter_tree(element: Element, /) -> Iterator[Element]:
    """Iterate over an element and all of its descendant elements."""
    return itertools.chain([element], element.find_all())


def _make_element_visible(element: Element, /) -> None:
    for elem in _iter_tree(element):
        del elem.display
        elem.fill = _BLACK
        elem.fill_opacity = 1
        elem.opacity = 1
        elem.stroke = _BLACK
        elem.stroke_opacity = 1
        elem.visibility = "visible"


def _set_element_visibility(
    element: Element, visibility: Literal["visible", "hidden"]
) -> None:
    for elem in _iter_tree(element):
        elem.visibility = visibility


def _render_tree(
    element: Element,
    *,
    render_this: bool,
    render_other: bool,
    make_element_visible: bool,
    width: float | None = None,
    height: float | None = None,
) -> _ImageArray:
    """Resolve the root `Svg` element and render the SVG tree.

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
        The rendered pixels, as `render_array` returns them.

    Raises:
        ValueError: If `make_element_visible` is `True` and `render_this`
            is `False`.

    """
    if make_element_visible and not render_this:
        raise ValueError(
            "make_element_visible cannot be True if render_this is False"
        )

    element_copy, svg = _copy_tree(element)
    assert isinstance(svg, Element)

    for t in svg.find_all():
        # do not hide the parents of our element as that would make it
        # invisible
        # TODO: this is quite suboptimal performance-wise; optimize this
        if render_other:
            t.visibility = "visible"
        else:
            t.visibility = "hidden"

    _set_element_visibility(
        element_copy, "visible" if render_this else "hidden"
    )

    if make_element_visible:
        _make_element_visible(element_copy)

    return _render_pixels(svg, width=width, height=height)


def _mask_bbox(mask: Mask, /) -> BBox | None:
    """Find the bounding box of the `True` values of a mask.

    Args:
        mask: A boolean mask, indexed by row and then by column.

    Returns:
        The bounding box, as `PIL.Image.Image.getbbox` gives it: the left and
        upper edges, and the right and lower edges exclusive. `None` if no
        value is `True`.

    Examples:
        >>> mask = np.zeros((4, 5), dtype=np.bool_)
        >>> _mask_bbox(mask)
        >>> mask[1:3, 2] = True
        >>> _mask_bbox(mask)
        (2, 1, 3, 3)

    """
    rows = np.flatnonzero(mask.any(axis=1))

    if rows.size == 0:
        return None

    columns = np.flatnonzero(mask.any(axis=0))

    return (
        int(columns[0]),
        int(rows[0]),
        int(columns[-1]) + 1,
        int(rows[-1]) + 1,
    )


def mask(  # ruff: ignore[D103]
    element: Element,
    *,
    width: float | None = None,
    height: float | None = None,
) -> Mask:
    pixels = _render_tree(
        element,
        render_this=True,
        render_other=False,
        make_element_visible=True,
        width=width,
        height=height,
    )

    return pixels[:, :, 3] > 0  # alpha channel > 0


def visible_mask(  # ruff: ignore[D103]
    element: Element,
    *,
    width: float | None = None,
    height: float | None = None,
) -> Mask:
    element_copy, svg = _copy_tree(element)
    assert isinstance(svg, Element)

    with_element = _render_pixels(svg, width=width, height=height)

    _set_element_visibility(element_copy, "hidden")

    without_element = _render_pixels(svg, width=width, height=height)

    # each pixel compared as one 32-bit value rather than channel by channel
    diff: Mask = (
        with_element.view(np.uint32) != without_element.view(np.uint32)
    )[:, :, 0]

    return diff


def bbox(element: Element) -> BBox | None:  # ruff: ignore[D103]
    pixels = _render_tree(
        element,
        render_this=True,
        render_other=False,
        make_element_visible=True,
    )

    # Pillow maps the array, and an RGBA image's box is that of its alpha
    return PIL.Image.fromarray(pixels).getbbox()


def visible_bbox(element: Element) -> BBox | None:  # ruff: ignore[D103]
    return _mask_bbox(visible_mask(element))
