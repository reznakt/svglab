import collections

import bs4
from typing_extensions import Final, Literal, TypeAlias, cast

import svglab.protocols
from svglab.elements import common, names, svg, text_elements
from svglab.utils import miscutils


Parser: TypeAlias = Literal["html.parser", "lxml", "lxml-xml", "html5lib"]
""" Type for parsers supported by BeautifulSoup. """


DEFAULT_PARSER: Final[Parser] = "lxml-xml"


_TAG_NAME_TO_CLASS: Final = {
    common.tag_name(cls): cls
    for cls in miscutils.get_all_subclasses(common.Tag)
    if cls.__name__ in names.TAG_NAME_TO_NORMALIZED.inverse
}

_BS_TO_TEXT_ELEMENT: Final[
    dict[
        type[bs4.NavigableString],
        type[
            text_elements.CData
            | text_elements.Comment
            | text_elements.RawText
        ],
    ]
] = {
    bs4.CData: text_elements.CData,
    bs4.Comment: text_elements.Comment,
    bs4.NavigableString: text_elements.RawText,
}


def _get_root_svg_fragments(soup: bs4.Tag) -> list[bs4.Tag]:
    """Find all root SVG fragments in the given BeautifulSoup object.

    The function performs a breadth-first search until it finds an
    SVG fragment. It then returns a list of all SVG fragments found in the same
    depth of the tree. This allows us to consider an SVG fragment as a root
    element when using HTML parsers that implicitly wrap the document in
    certain HTML tags (e.g., <html>).

    Args:
        soup: A BeautifulSoup tag object representing the root of the document.

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


def _convert_element(backend: bs4.PageElement) -> common.Element | None:
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
            tag_class = _TAG_NAME_TO_CLASS[
                cast(names.TagName, backend.name)
            ]

            for key, value in backend.attrs.items():
                backend.attrs[key] = str(value).strip()

            tag = tag_class.model_validate(
                {"prefix": backend.prefix, **backend.attrs}, strict=False
            )

            for child in backend.children:
                grandchild = _convert_element(child)

                if grandchild is not None:
                    tag.add_child(grandchild)
            return tag
        case _:
            return None


def parse_svg(
    markup: str
    | bytes
    | svglab.protocols.SupportsRead[str]
    | svglab.protocols.SupportsRead[bytes],
    /,
    *,
    parser: Parser = DEFAULT_PARSER,
) -> svg.Svg:
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
        msg = (
            f"Expected 1 <svg> element, found {len(svg_fragments)}."
            " This does not look like a valid SVG."
        )

        raise ValueError(msg)

    svg_ = _convert_element(svg_fragments[0])

    if not isinstance(svg_, svg.Svg):
        msg = f"Expected an <svg> element, found {type(svg_).__name__}."
        raise TypeError(msg)

    return svg_
