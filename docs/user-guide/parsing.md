# Parsing

<span style="font-variant: small-caps;">svglab</span> can read SVG content from a variety of sources and turn it into a fully typed tree of [element](elements.md) objects. The entry point is a single function: `parse_svg()`.

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
2. **Type conversion** &mdash; every recognized element becomes an instance of its corresponding <span style="font-variant: small-caps;">svglab</span> class (e.g. `<rect>` → `Rect`), and attribute values are converted from strings to their proper types ([`Length`](attributes.md#length), [`Color`](attributes.md#color), [`Transform`](attributes.md#compound-types), and so on).

!!! info "Embedded SVGs"
    Some files embed an `<svg>` element inside a wrapper (for example, an HTML document). `parse_svg()` performs a breadth-first search and returns the first `<svg>` element it finds, so these files work out of the box.

## Choosing a parser

Under the hood, <span style="font-variant: small-caps;">svglab</span> delegates XML parsing to a third-party parser. You can choose which one via the `parser` argument:

```python
svg = parse_svg(content, parser="lxml-xml")   # default, fast and strict
svg = parse_svg(content, parser="xml")         # stdlib fallback
```

The default (`lxml-xml`) is recommended for most use cases. It's fast, handles namespaces well, and gives clear error messages.

!!! warning "Parser availability"
    `lxml-xml` requires the `lxml` package to be installed. If it's missing, fall back to `"xml"` which uses Python's built-in XML parser.

## Unknown elements

If the SVG contains elements that aren't part of the SVG 1.1 specification, they're preserved as `UnknownElement` instances. This ensures nothing is lost during round-tripping:

```python
svg = parse_svg('<svg><my-widget data-v="3"/></svg>')
widget = svg.find("my-widget")

type(widget)          # UnknownElement
widget.element_name   # "my-widget"
widget.extra_attrs    # {"data-v": "3"}
```

See also [Elements: Unknown elements](elements.md#unknown-elements).

## Error handling

If the input is not valid XML, `parse_svg()` raises an exception from the underlying parser. Common causes:

- Malformed XML (unclosed tags, invalid characters)
- Encoding issues (pass `bytes` for non-UTF-8 files)
- No `<svg>` element found in the document

!!! warning "SVG fragments"
    `parse_svg()` expects the input to contain at least one `<svg>` element. You can't parse a bare fragment like `<rect width="100"/>` without wrapping it in an `<svg>` tag first.

## Next steps

- [Elements](elements.md) &mdash; working with the parsed tree
- [Attributes](attributes.md) &mdash; understanding the typed attribute values
- [Serialization](serialization.md) &mdash; writing the tree back to XML
