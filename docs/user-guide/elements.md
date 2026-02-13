# Elements

In SVG, everything you see &mdash; rectangles, circles, text, paths &mdash; is an **element**. <span style="font-variant: small-caps;">svglab</span> mirrors this: every SVG element has a corresponding Python class, and you work with elements the same way you'd think about them in a `.svg` file.

The library covers all **80 elements** defined in the [SVG 1.1 specification](https://www.w3.org/TR/SVG11/).

## Creating elements

There are two ways to get your hands on an element: **parse** one from an existing SVG document, or **create** one from scratch.

### From scratch

Instantiate any element class and pass [attributes](attributes.md) as keyword arguments:

```python
from svglab import Rect, Circle, Length, Color

rect = Rect(
    x=Length(10), y=Length(20),
    width=Length(100), height=Length(50),
    fill=Color("blue"),
)
```

Attributes you don't set default to `None` and won't appear in the serialized output.

### From an SVG document

The `parse_svg()` function turns SVG markup into a tree of element objects. See [Parsing](parsing.md) for the full story.

```python
from svglab import parse_svg

svg = parse_svg("""
<svg width="200" height="200">
    <rect x="10" y="10" width="100" height="50"/>
</svg>
""")
```

## Accessing and modifying attributes

Attributes are plain Python properties &mdash; read them, assign to them, or delete them:

```python
rect = svg.find("rect")

rect.x                     # Length(value=10.0, unit=None)
rect.rx                    # None (not set)
rect.fill = Color("red")   # set an attribute
del rect.fill               # remove it
```

!!! note "Attribute name mapping"
    SVG attribute names that aren't valid Python identifiers are mapped: hyphens become underscores (`stroke-width` → `stroke_width`) and reserved words get a trailing underscore (`class` → `class_`). See [Attributes: How attributes map to Python names](attributes.md#how-attributes-map-to-python-names) for the full rules.
For a deep dive into types, validation, and all available attributes, see [Attributes](attributes.md).

## Building a tree

SVG is hierarchical &mdash; elements contain other elements. <span style="font-variant: small-caps;">svglab</span> provides `add_child()` and `add_children()` for this:

```python
from svglab import Svg, Rect, Circle, G, Length

svg = Svg(width=Length(200), height=Length(200))

svg.add_child(Rect(width=Length(100), height=Length(50)))
svg.add_children(
    Circle(cx=Length(50), cy=Length(50), r=Length(20)),
    Circle(cx=Length(150), cy=Length(50), r=Length(20)),
)
```

!!! tip "Fluent chaining"
    `add_child()` and `add_children()` return the **parent**, so you can chain calls:

    ```python
    svg.add_child(Rect(...)).add_child(Circle(...))
    ```

!!! warning "Elements can only have one parent"
    An element cannot belong to two parents at once. If you try to add an element that's already in a tree, you'll get an error. Remove it from its current parent first.

To remove a child, call `remove_child()`:

```python
circle = svg.find(Circle)
svg.remove_child(circle)
```

!!! tip "Grouping elements"
    The `G` (group) element is a convenient container for applying shared attributes or [transforms](transforms.md) to multiple children:

    ```python
    group = G(id="icons", opacity=0.8)
    group.add_child(Rect(...))
    group.add_child(Circle(...))
    svg.add_child(group)
    ```

## Searching for elements

Once you have a tree, you'll often need to locate specific elements within it.

### `find()` &mdash; first match

Returns the first element matching a type or tag name:

=== "By class"

    ```python
    rect = svg.find(Rect)
    ```

=== "By tag name"

    ```python
    rect = svg.find("rect")
    ```

!!! tip "Prefer searching by class"
    Both forms find the same element, but searching by **class** has a significant advantage: the return type is automatically narrowed. With `svg.find(Rect)`, your editor knows the result is a `Rect` and will autocomplete attributes like `rx` and `ry`. With `svg.find("rect")`, the result is a generic `Element` and you'd need a manual cast to access shape-specific attributes.

### `find_all()` &mdash; all matches

Returns every matching element. By default the search is **recursive**, walking the entire subtree:

```python
all_rects = svg.find_all(Rect)
everything = svg.find_all()               # all elements
direct_only = svg.find_all(recursive=False)  # only direct children
```

!!! note
    `find_all()` returns only **element** nodes. Text content (`RawText`, `CData`, `Comment`) is not included in the results. To access those, look at an element's children directly.

## Navigating the tree

Every element knows where it sits in the tree:

| Attribute / Method | Returns |
|--------------------|--------|
| `parent` | The element's immediate parent (or `None`) |
| `get_root()` | The root `Svg` element |

```python
rect = svg.find(Rect)
rect.parent       # the <svg> or <g> that contains it
rect.get_root()   # the top-level Svg element
```

## Comparing elements

Elements support `==` for **deep structural comparison** &mdash; same type, same attributes, and recursively equal children:

```python
Rect(width=Length(100)) == Rect(width=Length(100))   # True
```

!!! warning "Equality vs. identity"
    `==` checks structural equality, but tree operations like `remove_child()` use **object identity** (`is`). Two elements can be equal without being the same object, so always pass the exact reference you got from `find()` to `remove_child()`.

## Common element types

### Basic shapes

The SVG specification defines six *basic shapes* &mdash; predefined primitives for common geometries. In <span style="font-variant: small-caps;">svglab</span>, they all implement the `BasicShape` [trait](traits.md) and can be [converted to paths](path-data.md#converting-shapes-to-paths).

| Element | Key attributes |
|---------|---------------|
| `Rect` | `x`, `y`, `width`, `height`, `rx`, `ry` |
| `Circle` | `cx`, `cy`, `r` |
| `Ellipse` | `cx`, `cy`, `rx`, `ry` |
| `Line` | `x1`, `y1`, `x2`, `y2` |
| `Polyline` | `points` |
| `Polygon` | `points` |

### Paths

The `Path` element is the most powerful drawing primitive in SVG. Its `d` attribute contains a sequence of drawing commands &mdash; lines, curves, arcs, and more. See [Path Data](path-data.md) for details.

### Container elements

Containers hold other elements and optionally apply shared transforms or styles. The most common ones:

- **`Svg`** &mdash; the root document element
- **`G`** &mdash; a generic group
- **`Defs`** &mdash; houses reusable definitions (gradients, clip paths, symbols, &hellip;)
- **`Symbol`** / **`Use`** &mdash; define an element once, stamp it multiple times

### Text

Text in SVG is rendered through the `Text` element. Child `Tspan` elements allow styling individual runs of text:

```python
from svglab import Text, Tspan, RawText, Color, Length

text = Text(x=Length(10), y=Length(50), font_size=Length(24))
text.add_child(RawText("Hello, "))

span = Tspan(fill=Color("red"))
span.add_child(RawText("World!"))
text.add_child(span)
```

## Character data

Not everything in an SVG document is an element. <span style="font-variant: small-caps;">svglab</span> also represents the textual content that lives *inside* elements:

| Class | Represents | Typical use |
|-------|-----------|-------------|
| `RawText` | Plain text nodes | Text content in `<text>` |
| `CData` | `<![CDATA[...]]>` sections | Inline CSS in `<style>` |
| `Comment` | `<!-- ... -->` comments | Annotations |

```python
from svglab import Style, CData

style = Style()
style.add_child(CData(".highlight { fill: yellow; }"))
```

## Unknown elements

If <span style="font-variant: small-caps;">svglab</span> encounters an element it doesn't recognize (custom namespaces, non-standard extensions, &hellip;), it wraps it in an `UnknownElement` so nothing is lost during round-tripping:

```python
from svglab import parse_svg, UnknownElement

svg = parse_svg('<svg><custom-widget data-v="3"/></svg>')
elem = svg.find(UnknownElement)
elem.element_name   # "custom-widget"
elem.extra_attrs    # {"data-v": "3"}
```

## Next steps

- [Attributes](attributes.md) &mdash; types, validation, and the full attribute catalogue
- [Traits](traits.md) &mdash; discover what operations are available on each element
- [Serialization](serialization.md) &mdash; convert your tree back to XML
- [API Reference: Elements](../api-reference/elements.md) &mdash; complete class listing
