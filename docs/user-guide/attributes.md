# Attributes

Every SVG element is configured through **attributes** &mdash; the `width`, `fill`, `transform`, and so on that you'd normally write in XML. <span style="font-variant: small-caps;">svglab</span> exposes these as **typed, validated Python properties**, so typos are caught immediately and values are guaranteed to make sense.

The library defines **295 attributes** covering the entire SVG 1.1 specification.

## Attribute types

Unlike raw XML where every attribute is a string, <span style="font-variant: small-caps;">svglab</span> parses attribute values into rich Python objects. Here are the most common types:

### Length

Numeric values with an optional CSS unit. Used for positions, sizes, stroke widths &mdash; practically anything geometric.

```python
from svglab import Length

Length(42)         # unitless (user units)
Length(10, "px")   # pixels
Length(2.5, "em")  # relative to font size
```

Supported units: `%`, `ch`, `cm`, `em`, `ex`, `in`, `mm`, `pc`, `pt`, `px`, `Q`, `rem`, `vh`, `vmax`, `vmin`, `vw`.

!!! tip "Length arithmetic"
    `Length` objects support basic math: addition, subtraction (with compatible units), and multiplication/division by scalars. The result inherits the **left operand's** unit. Relative units like `em` and `%` can't be mixed with absolute units like `px`.

!!! info "User units"
    In SVG, a bare number like `width="100"` is in *user units*, which default to pixels but can be changed by the `viewBox`. <span style="font-variant: small-caps;">svglab</span> represents these as `Length(100)` with no unit.

### Color

CSS-style color values. You can use named colors, hex notation, or the `rgb()` function:

```python
from svglab import Color

Color("red")            # named color
Color("#ff6600")        # hex
Color("rgb(255,0,0)")   # RGB function
```

!!! note "Equality is value-based"
    `Color("red") == Color("#ff0000")` is `True` &mdash; colors are compared by their resolved RGBA values, not by how they were originally written. However, the original string is preserved for serialization, so the output format depends on the [Formatter](serialization.md) settings.

### Angle

Rotation and skew values with a unit:

```python
from svglab import Angle

Angle(45, "deg")     # degrees
Angle(0.785, "rad")  # radians
Angle(50, "grad")    # gradians
Angle(0.25, "turn")  # turns
```

### IRI

An *Internationalized Resource Identifier* &mdash; used for cross-references like clip paths, gradients, and filters:

```python
from svglab import Iri

Iri(fragment="myGradient")   # references id="myGradient"
```

In the serialized output, this becomes `#myGradient`. Use `FuncIri` for the functional notation `url(#myGradient)`.

### Compound types

Some attributes have structured values made up of multiple components:

| Type | Example attribute | Description |
|------|------------------|-------------|
| `PathData` | `d` (on `<path>`) | Sequence of drawing commands &mdash; see [Path Data](path-data.md) |
| `Transform` | `transform` | A chain of affine transformations &mdash; see [Transforms](transforms.md) |
| `Points` | `points` (on `<polygon>`, `<polyline>`) | A list of `Point` objects |

## How attributes map to Python names

SVG attribute names don't always work as Python identifiers, so <span style="font-variant: small-caps;">svglab</span> applies two simple rules:

1. **Hyphens become underscores** &mdash; `stroke-width` → `stroke_width`
2. **Reserved words get a trailing underscore** &mdash; `class` → `class_`, `in` → `in_`

You always use the Python name when reading or writing properties.

## Attribute groups

Not every attribute applies to every element. The SVG spec organizes attributes into logical groups, and <span style="font-variant: small-caps;">svglab</span> does the same with *attribute mixin classes*:

| Group | Examples | What it's for |
|-------|----------|--------------|
| **Core** | `id`, `class_`, `style` | Universal identifiers and styling |
| **Presentation** | `fill`, `stroke`, `opacity`, `font_size` | Visual appearance |
| **Geometry** | `x`, `y`, `width`, `height`, `cx`, `cy`, `r` | Position and size |
| **Animation** | `begin`, `dur`, `repeatCount` | Timing for SMIL animations |

Each element class includes exactly the attribute groups it needs. For instance, `Rect` includes geometry attributes (`x`, `y`, `width`, `height`) plus presentation attributes (`fill`, `stroke`, &hellip;), while `Animate` includes animation timing attributes instead.

!!! tip
    You can explore which attributes an element supports using your IDE's autocompletion, or check the [API Reference: Attribute Groups](../api-reference/attribute-groups.md).

## Validation

Attributes are validated at assignment time. If you pass a value of the wrong type, you'll get an immediate error rather than a silently malformed SVG:

```python
from svglab import Rect, Color, Length

rect = Rect()
rect.fill = Color("blue")   # ✓
rect.fill = Length(10)       # ✗ ValidationError
```

!!! note "Pydantic under the hood"
    Element classes are built on [Pydantic](https://docs.pydantic.dev/) models, which means you benefit from runtime type checking and clear error messages for free.

!!! tip "Use your IDE"
    Because elements are Pydantic models with typed fields, your IDE can autocomplete attribute names, flag type mismatches, and show documentation on hover &mdash; even before you run your code.

## Extra attributes

Real-world SVGs often contain attributes that aren't part of the SVG specification &mdash; `data-*` attributes, framework-specific props, or attributes from other XML namespaces.

<span style="font-variant: small-caps;">svglab</span> preserves these as **extra attributes** so nothing is lost during round-tripping:

```python
from svglab import parse_svg

svg = parse_svg('<svg><rect data-tooltip="hello" custom:foo="bar"/></svg>')
rect = svg.find("rect")

rect.extra_attrs   # {"data-tooltip": "hello", "custom:foo": "bar"}
```

Extra attributes are stored as plain strings (no type conversion) and are written back exactly as they were read.

## Next steps

- [Elements](elements.md) &mdash; creating elements and building SVG trees
- [Traits](traits.md) &mdash; which operations are available on which elements
- [Serialization](serialization.md) &mdash; control how attribute values are formatted in output
- [API Reference: Attributes](../api-reference/attributes.md) &mdash; complete attribute listing
- [API Reference: Attribute Groups](../api-reference/attribute-groups.md) &mdash; which attributes belong to which groups
