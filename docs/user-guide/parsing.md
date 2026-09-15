# Parsing

<span class="svglab">svglab</span> can read SVG content from a variety of sources and turn it into a fully typed tree of [element](elements.md) objects. The entry point is a single function: `parse_svg()`.

## Quick start

```python
from svglab import parse_svg

svg = parse_svg('<svg><rect width="100" height="50"/></svg>')
```

That's it &mdash; `svg` is now an `Svg` element whose children, attributes, and text nodes are all accessible as Python objects.

## Input sources

`parse_svg()` accepts several input types, so you can feed it whatever you have:

=== "String"

    ```python
    svg = parse_svg('<svg><circle r="10"/></svg>')
    ```

=== "Bytes"

    ```python
    raw = b'<svg><circle r="10"/></svg>'
    svg = parse_svg(raw)
    ```

=== "File path"

    ```python
    from pathlib import Path

    svg = parse_svg(Path("drawing.svg"))
    ```

=== "File object"

    ```python
    with open("drawing.svg") as f:
        svg = parse_svg(f)
    ```

## What happens during parsing

Parsing is a two-step process:

1. **XML parsing** &mdash; the raw markup is parsed into an XML tree.
2. **Type conversion** &mdash; every recognized element becomes an instance of its corresponding <span class="svglab">svglab</span> class (e.g. `<rect>` → `Rect`), and attribute values are converted from strings to their proper types ([`Length`](attributes.md#length), [`Color`](attributes.md#color), [`Transform`](attributes.md#compound-types), and so on).

!!! info "Embedded SVGs"
    Some files embed an `<svg>` element inside a wrapper (for example, an HTML document). `parse_svg()` searches the document for `<svg>` elements rather than requiring one at the root, so these files work out of the box.

!!! warning "Exactly one `<svg>` per document"
    The document must contain exactly one `<svg>` element. Zero (a bare fragment) and more than one (two sibling icons in a page, or an `<svg>` nested inside another `<svg>`) both raise `ValueError`.

## Choosing a parser

Under the hood, <span class="svglab">svglab</span> delegates XML parsing to a third-party parser. You can choose which one via the `parser` argument:

```python
svg = parse_svg(content, parser="lxml-xml")  # default; XML parser
svg = parse_svg(content, parser="lxml")  # lxml's HTML parser
svg = parse_svg(
    content, parser="html.parser"
)  # Python's built-in HTML parser
svg = parse_svg(content, parser="html5lib")  # lenient, browser-like
```

The default (`lxml-xml`) is recommended for most use cases. It's fast, handles namespaces well, and is the only one of the four that treats the input as XML. The HTML parsers are useful when the `<svg>` is embedded in a real HTML page.

!!! info "No optional installs"
    All four parsers are available out of the box: both `lxml` and `html5lib` are hard dependencies of <span class="svglab">svglab</span>.

## Unknown elements

If the SVG contains elements that aren't part of the SVG 1.1 specification, they're preserved as `UnknownElement` instances so nothing is lost during round-tripping. See [Elements: Unknown elements](elements.md#unknown-elements) for details and examples.

## Error handling

The error you'll see in practice is `ValueError`, raised when the document doesn't contain exactly one `<svg>` element:

```python
parse_svg(
    '<rect width="100"/>'
)  # ValueError: Expected one <svg> element, found 0
```

!!! note "Malformed markup usually doesn't raise"
    The underlying parsers are recovery-oriented: an unclosed tag is quietly repaired rather than reported. Don't rely on `parse_svg()` to validate markup &mdash; if the result looks wrong, the input probably was. Encoding problems are the exception; pass `bytes` for non-UTF-8 files and let the parser detect the encoding.

!!! warning "SVG fragments"
    `parse_svg()` expects the input to contain an `<svg>` element. You can't parse a bare fragment like `<rect width="100"/>` without wrapping it in an `<svg>` tag first.

## Next steps

<div class="grid cards" markdown>

-   __[Elements](elements.md)__ &mdash; working with the parsed tree
-   __[Attributes](attributes.md)__ &mdash; understanding the typed attribute values
-   __[Serialization](serialization.md)__ &mdash; writing the tree back to XML

</div>
