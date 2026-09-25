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
    TypeVar,
    cast,
    runtime_checkable,
)

from svglab import entities, errors, resvg, serialize
from svglab.attrparse import color, length


Mask: TypeAlias = npt.NDArray[np.bool_]
BBox: TypeAlias = tuple[int, int, int, int]

_ImageArray: TypeAlias = npt.NDArray[np.uint8]

_ElementT = TypeVar("_ElementT", bound=entities.Element)


_BLACK: Final = color.Color((0, 0, 0))


@runtime_checkable
class _SvgElementLike(Protocol):
    width: length.Length | None
    height: length.Length | None
    viewBox: tuple[float, float, float, float] | None  # noqa: N815

    def render(
        self,
        options: resvg.RenderOptions | None = None,
        *,
        background: color.Color | None = None,
        height: float | None = None,
        width: float | None = None,
        zoom: float = 1,
    ) -> PIL.Image.Image: ...


def _positive_user_units(value: length.Length | None, /) -> float | None:
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
        >>> _positive_user_units(Length(0))
        >>> _positive_user_units(None)

    """
    if value is None:
        return None

    try:
        user_units = float(value)
    except errors.SvgUnitConversionError:
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
    svg: entities.Element,
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
    if not isinstance(svg, _SvgElementLike):
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


def render(  # noqa: D103
    svg: entities.Element,
    options: resvg.RenderOptions | None = None,
    *,
    background: color.Color | None = None,
    height: float | None = None,
    width: float | None = None,
    zoom: float = 1,
) -> PIL.Image.Image:
    if not isinstance(svg, _SvgElementLike):
        raise TypeError("Element must be an SVG element")

    render_size = _compute_render_size(svg, width=width, height=height)
    svg = copy.copy(svg)

    svg.width = length.Length(render_size[0])
    svg.height = length.Length(render_size[1])

    xml = svg.to_xml(formatter=serialize.MINIMAL_FORMATTER)

    return resvg.render(xml, options, background=background, zoom=zoom)


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

    if not isinstance(svg, _SvgElementLike):
        raise ValueError("Element must be part of an SVG tree")  # noqa: TRY004

    memo: dict[int, object] = {}
    svg = copy.deepcopy(svg, memo)
    this = cast(_ElementT, memo[id(element)])

    return this, svg


def _iter_tree(element: entities.Element, /) -> Iterator[entities.Element]:
    """Iterate over an element and all of its descendant elements."""
    return itertools.chain([element], element.find_all())


def _make_element_visible(element: entities.Element, /) -> None:
    for elem in _iter_tree(element):
        del elem.display
        elem.fill = _BLACK
        elem.fill_opacity = 1
        elem.opacity = 1
        elem.stroke = _BLACK
        elem.stroke_opacity = 1
        elem.visibility = "visible"


def _set_element_visibility(
    element: entities.Element, visibility: Literal["visible", "hidden"]
) -> None:
    for elem in _iter_tree(element):
        elem.visibility = visibility


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
        if render_other:
            t.visibility = "visible"
        else:
            t.visibility = "hidden"

    _set_element_visibility(
        element_copy, "visible" if render_this else "hidden"
    )

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
    array: _ImageArray = np.array(img)

    return array[:, :, 3] > 0  # alpha channel > 0


def visible_mask(  # noqa: D103
    element: entities.Element,
    *,
    width: float | None = None,
    height: float | None = None,
) -> Mask:
    element_copy, svg = _copy_tree(element)
    assert isinstance(svg, entities.Element)

    for t in svg.find_all():
        t.visibility = "visible"

    with_element: _ImageArray = np.array(
        svg.render(width=width, height=height)
    )

    _set_element_visibility(element_copy, "hidden")

    without_element: _ImageArray = np.array(
        svg.render(width=width, height=height)
    )

    diff: Mask = np.any(without_element != with_element, axis=2)

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
