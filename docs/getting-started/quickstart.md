# Quickstart

This guide will help you get started with <span style="font-variant: small-caps;">svglab</span> by demonstrating simple usage examples.

## Importing the library

Start by verifying that the library is installed correctly by importing it in a Python shell or script:

```python
import svglab
```

<span style="font-variant: small-caps;">svglab</span> has a flat import structure &mdash; this means that all symbols are available directly from the top-level package:

```python
from svglab import Svg, Circle, Rect, Line
```

## Parsing an SVG file

To parse an existing SVG file, use the `#!python parse_svg()` function. The function returns an `#!python Svg` object representing the root `#!xml <svg>` element of the document.

!!! tip
    The `#!python parse_svg()` function can directly read from a file-like object. See the examples below.

=== "From string"

    ```python hl_lines="9"
    from svglab import parse_svg

    svg_content = """
    <svg width="100" height="100" xmlns="http://www.w3.org/2000/svg">
        <circle cx="50" cy="50" r="40" stroke="black" stroke-width="2" fill="red"/>
    </svg>
    """

    svg = parse_svg(svg_content)
    print(svg)
    ```

=== "From file"

    ```python hl_lines="4"
    from svglab import parse_svg

    with open("example.svg", "r") as file:
        svg = parse_svg(file)
        print(svg)
    ```

## Searching for elements

Once we have an `#!python Svg` object, we can obtain a reference to the `#!python Circle` element by using the `#!python find()` method.

```python
circle = svg.find("circle")
print(circle)
```

## Modifying attributes

Element attributes are represented as properties on the element object. We can modify them directly:

!!! note
    Attribute names that are not valid Python identifiers (e.g. `stroke-width`) are converted to valid identifiers by replacing hyphens with underscores (e.g. `stroke_width`). Reserved words are also suffixed with an underscore (e.g. `class` becomes `class_`).

```python
from svglab import Color

circle.fill = Color("blue")  # change fill color to blue
del circle.stroke_width  # remove the stroke-width attribute
```

## Adding new elements

New elements can be created by instantiating the corresponding class. The constructor accepts attribute values as keyword arguments. Child elements can be added using the `#!python add_child()` or `#!python add_children()` methods.

```python
from svglab import Rect

rect = Rect(x=10, y=10, width=30, height=30, fill=Color("green"))
svg.add_child(rect)
```

## Serializing the SVG

Finally, we can serialize the modified SVG back to a string using the `#!python to_xml()` method. The resulting string can be saved to a file or used as needed.

!!! warning
    Calling the `#!python __str__()` method (for example, via `print(svg)`) will produce a human-readable representation of the object, but it is not valid XML. Always use `#!python to_xml()` for serialization.

```python
svg_xml = svg.to_xml()
print(svg_xml)
```

If you want to save the SVG to a file, you can do so as follows:

```python
with open("modified_example.svg", "w") as file:
    svg.save(file)
```
