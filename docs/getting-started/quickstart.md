# Quickstart

This guide walks through the basics of <span style="font-variant: small-caps;">svglab</span> in a few minutes. By the end, you'll know how to parse, modify, and serialize an SVG document.

## Importing the library

<span style="font-variant: small-caps;">svglab</span> has a **flat import structure** &mdash; everything is available directly from the top-level package:

```python
from svglab import Svg, Circle, Rect, parse_svg, Color, Length
```

## Parsing an SVG

Use `parse_svg()` to read SVG content from a string, file, or path:

=== "From a string"

    ```python
    from svglab import parse_svg

    svg = parse_svg("""
    <svg width="100" height="100" xmlns="http://www.w3.org/2000/svg">
        <circle cx="50" cy="50" r="40" stroke="black" stroke-width="2" fill="red"/>
    </svg>
    """)
    ```

=== "From a file"

    ```python
    from pathlib import Path
    from svglab import parse_svg

    svg = parse_svg(Path("example.svg"))
    ```

The result is a fully typed `Svg` object. See [Parsing](../user-guide/parsing.md) for all supported input types.

## Finding elements

Use `find()` to locate an element in the tree:

```python
from svglab import Circle

circle = svg.find(Circle)
```

!!! tip
    Searching by **class** (like `Circle`) rather than by string (`"circle"`) gives you better autocompletion and type checking in your editor. See [Elements: Searching](../user-guide/elements.md#searching-for-elements) for details.

## Modifying attributes

Attributes are regular Python properties &mdash; read, set, or delete them:

```python
from svglab import Color

circle.fill = Color("blue")    # change fill color
del circle.stroke_width         # remove stroke-width
```

Attribute names follow a simple mapping: hyphens become underscores (`stroke-width` → `stroke_width`), and reserved words get a trailing underscore (`class` → `class_`). See [Attributes](../user-guide/attributes.md) for the full type system.

## Adding elements

Create new elements and add them to the tree:

```python
from svglab import Rect, Length, Color

rect = Rect(
    x=Length(10), y=Length(10),
    width=Length(30), height=Length(30),
    fill=Color("green"),
)
svg.add_child(rect)
```

See [Elements: Building a tree](../user-guide/elements.md#building-a-tree) for grouping, chaining, and more.

## Serializing to XML

Convert the tree back to an XML string with `to_xml()`, or write directly to a file with `save()`:

=== "To string"

    ```python
    xml = svg.to_xml()
    print(xml)
    ```

=== "To file"

    ```python
    svg.save("modified.svg")
    ```

!!! warning
    `print(svg)` produces a human-readable debug representation, **not** valid XML. Always use `to_xml()` or `save()` for serialization.

For fine-grained control over formatting (indentation, color format, precision, and more), see [Serialization](../user-guide/serialization.md).

## What's next?

Now that you have the basics, explore the **User Guide** for deeper coverage:

- [Elements](../user-guide/elements.md) &mdash; creating, searching, and navigating the SVG tree
- [Attributes](../user-guide/attributes.md) &mdash; typed values, validation, and the full attribute catalogue
- [Traits](../user-guide/traits.md) &mdash; what operations are available on which elements
- [Parsing](../user-guide/parsing.md) &mdash; input sources and parser options
- [Serialization](../user-guide/serialization.md) &mdash; the `Formatter` and output customization
- [Path Data](../user-guide/path-data.md) &mdash; working with SVG path commands
- [Transforms](../user-guide/transforms.md) &mdash; affine transformations and composition
- [Graphical Operations](../user-guide/graphics.md) &mdash; rendering, bounding boxes, and masks
