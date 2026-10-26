"""Functions related to rendering and other graphics operations."""

import itertools
from collections.abc import Iterator

import bs4
import numpy as np
import numpy.typing as npt
import PIL.Image
from typing_extensions import (
    Final,
    Literal,
    Protocol,
    TypeAlias,
    TypeIs,
    runtime_checkable,
)

from svglab.attrparse.color import Color
from svglab.attrparse.length import Length
from svglab.entities import Element
from svglab.errors import SvgUnitConversionError
from svglab.resvg import RenderOptions, render_array
from svglab.resvg import render as resvg_render
from svglab.serialize import MINIMAL_FORMATTER, serialize_attr
from svglab.utils.bsutils import beautifulsoup_to_str


Mask: TypeAlias = npt.NDArray[np.bool_]
BBox: TypeAlias = tuple[int, int, int, int]

_ImageArray: TypeAlias = npt.NDArray[np.uint8]


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


def _render_soup(
    svg: Element, *, width: float | None, height: float | None
) -> bs4.Tag:
    """Convert an SVG element to the tree that is rendered of it.

    Args:
        svg: The SVG element to convert.
        width: The width of the rendered image, in pixels, or `None`.
        height: The height of the rendered image, in pixels, or `None`.

    Returns:
        The `BeautifulSoup` tree of the element, its size set to the render
        size. Editing the tree changes what is rendered without touching the
        element.

    Raises:
        TypeError: If the element is not an SVG element.

    """
    if not _is_svg_element_like(svg):
        raise TypeError("Element must be an SVG element")

    render_width, render_height = _compute_render_size(
        svg, width=width, height=height
    )

    with MINIMAL_FORMATTER:
        soup = svg.to_beautifulsoup_object()
        soup["width"] = serialize_attr("width", Length(render_width))
        soup["height"] = serialize_attr("height", Length(render_height))

    return soup


def _render_xml(soup: bs4.Tag, /) -> str:
    """Convert a tree from `_render_soup` to the XML that is rendered."""
    with MINIMAL_FORMATTER:
        return beautifulsoup_to_str(soup, pretty=True)


def render(  # ruff: ignore[D103]
    svg: Element,
    options: RenderOptions | None = None,
    *,
    background: Color | None = None,
    height: float | None = None,
    width: float | None = None,
    zoom: float = 1,
) -> PIL.Image.Image:
    xml = _render_xml(_render_soup(svg, width=width, height=height))

    return resvg_render(xml, options, background=background, zoom=zoom)


def _render_tree_soup(
    element: Element, *, width: float | None, height: float | None
) -> tuple[bs4.Tag, bs4.Tag]:
    """Resolve the root `Svg` element and convert the SVG tree for rendering.

    The tree is converted as `_render_soup` converts it, so what is rendered
    can be changed without copying or touching the elements. The tag of the
    source element is identified in the converted tree and returned for easy
    access.

    Args:
        element: The element in the SVG tree to convert.
        width: The width of the rendered image, in pixels, or `None`.
        height: The height of the rendered image, in pixels, or `None`.

    Returns:
        A tuple of the tag of the element and the tag of the root `Svg`
        element.

    Raises:
        ValueError: If the element is not a part of an SVG tree.

    """
    indices: list[int] = []
    child = element

    while (parent := child.parent) is not None:
        siblings = (c for c in parent.children if isinstance(c, Element))
        indices.append(
            next(i for i, c in enumerate(siblings) if c is child)
        )
        child = parent

    if not _is_svg_element_like(child):
        raise ValueError("Element must be part of an SVG tree")

    soup = _render_soup(child, width=width, height=height)
    tag = soup

    # each element becomes one tag, in order, among any text and comments
    for index in reversed(indices):
        tag = [c for c in tag.children if isinstance(c, bs4.Tag)][index]

    return tag, soup


def _iter_tags(tag: bs4.Tag, /) -> Iterator[bs4.Tag]:
    """Iterate over a tag and all of its descendant tags."""
    return itertools.chain(
        [tag], (t for t in tag.descendants if isinstance(t, bs4.Tag))
    )


def _make_tag_visible(tag: bs4.Tag, /) -> None:
    with MINIMAL_FORMATTER:
        visible = {
            name: serialize_attr(name, value)
            for name, value in (
                ("fill", _BLACK),
                ("fill-opacity", 1),
                ("opacity", 1),
                ("stroke", _BLACK),
                ("stroke-opacity", 1),
                ("visibility", "visible"),
            )
        }

    for t in _iter_tags(tag):
        t.attrs.pop("display", None)
        t.attrs.update(visible)


def _set_tag_visibility(
    tag: bs4.Tag, visibility: Literal["visible", "hidden"]
) -> None:
    for t in _iter_tags(tag):
        t["visibility"] = visibility


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

    tag, soup = _render_tree_soup(element, width=width, height=height)

    # a descendant can override an inherited visibility, so hiding the
    # element's ancestors along with everything else does not hide it
    for t in soup.descendants:
        if isinstance(t, bs4.Tag):
            t["visibility"] = "visible" if render_other else "hidden"

    _set_tag_visibility(tag, "visible" if render_this else "hidden")

    if make_element_visible:
        _make_tag_visible(tag)

    return render_array(_render_xml(soup))


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
    tag, soup = _render_tree_soup(element, width=width, height=height)

    with_element = render_array(_render_xml(soup))

    _set_tag_visibility(tag, "hidden")

    without_element = render_array(_render_xml(soup))

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
