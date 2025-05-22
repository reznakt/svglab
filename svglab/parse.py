"""Logic for parsing SVG documents."""

import collections
import warnings

import bs4
from typing_extensions import Final, Literal, TypeAlias, cast

from svglab import entities, protocols
from svglab.elements import elements, names
from svglab.utils import miscutils


warnings.filterwarnings("ignore", category=bs4.XMLParsedAsHTMLWarning)

_Markup: TypeAlias = (
    str
    | bytes
    | protocols.SupportsRead[str]
    | protocols.SupportsRead[bytes]
)


_ELEMENT_NAME_TO_CLASS: Final = {
    entities.element_name(cls()): cls
    for cls in miscutils.get_all_subclasses(entities.Element)
    if cls.__name__ in names.ELEMENT_NAME_TO_NORMALIZED.inverse
}

_BS_TO_TEXT_ELEMENT: Final[
    dict[
        type[bs4.NavigableString],
        type[entities.CData | entities.Comment | entities.RawText],
    ]
] = {
    bs4.CData: entities.CData,
    bs4.Comment: entities.Comment,
    bs4.NavigableString: entities.RawText,
}


def _get_root_svg_fragments(soup: bs4.Tag) -> list[bs4.Tag]:
    """Find all root SVG fragments in the given BeautifulSoup object.

    The function performs a breadth-first search until it finds an
    SVG fragment. It then returns a list of all SVG fragments found in the same
    depth of the tree. This allows us to consider an SVG fragment as a root
    element when using HTML parsers that implicitly wrap the document in
    certain HTML elements (e.g., <html>).

    Args:
        soup: A BeautifulSoup `Tag` object representing the root of the
        document.

    Returns:
        A list of SVG fragments found in the document.

    Examples:
        >>> soup = bs4.BeautifulSoup(
        ...     "<svg><rect/></svg>", features="lxml-xml"
        ... )
        >>> _get_root_svg_fragments(soup)
        [<svg><rect/></svg>]
        >>> soup = bs4.BeautifulSoup(
        ...     "<svg><rect/></svg>", features="html.parser"
        ... )
        >>> _get_root_svg_fragments(soup)
        [<svg><rect></rect></svg>]

    """
    queue: collections.deque[bs4.Tag] = collections.deque([soup])

    while queue:
        node = queue.popleft()

        if svg_fragments := node.find_all("svg"):
            return svg_fragments

        queue.extend(
            child for child in node.children if isinstance(child, bs4.Tag)
        )

    return []


def _convert_element(backend: bs4.PageElement) -> entities.Entity | None:
    """Convert a BeautifulSoup element to an `Element` instance.

    Args:
        backend: A BeautifulSoup element to convert.

    Returns:
        An `Element` instance representing the given BeautifulSoup element.

    Raises:
        TypeError: If the given element cannot be converted.

    """
    match backend:
        case bs4.NavigableString():
            cls = _BS_TO_TEXT_ELEMENT.get(type(backend))

            if cls is None:
                return None

            text = backend.get_text(strip=True)

            return cls(text) if text else None
        case bs4.Tag():
            element_class = _ELEMENT_NAME_TO_CLASS.get(
                cast(names.ElementName, backend.name),
                entities.UnknownElement,
            )

            attrs = {"prefix": backend.prefix}

            for key, value in backend.attrs.items():
                attrs[key] = str(value).strip()

            if element_class is entities.UnknownElement:
                attrs["element_name"] = backend.name

            element = element_class.model_validate(attrs, strict=False)

            for child in backend.children:
                grandchild = _convert_element(child)

                if grandchild is not None:
                    element.add_child(grandchild)
            return element
        case _:
            return None


def _get_markup_head(markup: _Markup, limit: int = 30) -> str:
    match markup:
        case str():
            return (
                markup if len(markup) <= limit else f"{markup[:limit]}..."
            )
        case bytes():
            return _get_markup_head(markup.decode(), limit=limit)
        case protocols.SupportsRead():
            return _get_markup_head(markup.read(limit + 1), limit=limit)


def parse_svg(
    markup: _Markup,
    /,
    *,
    parser: Literal[
        "html.parser", "lxml", "lxml-xml", "html5lib"
    ] = "lxml-xml",
) -> elements.Svg:
    """Parse an SVG document.

    The document must be a valid XML document containing a single SVG
    document fragment.

    Args:
        markup: A string or a file-like object representing markup
        to be parsed.
        parser: The name of the parser to use. Defaults to 'lxml-xml'.

    Returns:
        The parsed SVG document in the form of an `Svg` instance.

    Raises:
        ValueError: If the markup does not contain a single SVG
        document fragment

    Examples:
        >>> svg = parse_svg("<svg><rect/></svg>")
        >>> type(svg).__name__
        'Svg'

    """
    soup = bs4.BeautifulSoup(markup, features=parser)
    svg_fragments = _get_root_svg_fragments(soup)

    if len(svg_fragments) != 1:
        markup_head = _get_markup_head(markup)
        msg = (
            f"Expected one <svg> element, found {len(svg_fragments)}; this "
            f"does not look like a well-formed SVG (markup: {markup_head})."
        )

        raise ValueError(msg)

    return cast(elements.Svg, _convert_element(svg_fragments[0]))
