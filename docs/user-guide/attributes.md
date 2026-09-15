# Attributes

Every SVG element is configured through **attributes** &mdash; the `width`, `fill`, `transform`, and so on that you'd normally write in XML. <span class="svglab">svglab</span> exposes these as **typed, validated Python properties**, so typos are caught immediately and values are guaranteed to make sense.

The library defines **276 attributes** covering the entire SVG 1.1 specification, plus a handful of SVG 2 additions.

## Attribute types

Unlike raw XML where every attribute is a string, <span class="svglab">svglab</span> parses attribute values into rich Python objects. Here are the most common types:

### Length

Numeric values with an optional CSS unit. Used for positions, sizes, stroke widths &mdash; practically anything geometric.

```python { .annotate }
from svglab import Length

Length(42)  # (1)!
Length(10, "px")
Length(2.5, "em")

Length(10, "px") + Length(5, "px")  # (2)!
Length(10, "px") * 2  # (3)!
```

1.  A bare number is in *user units* &mdash; what `width="100"` means in SVG. User units default to pixels, but the `viewBox` can change that.
2.  `Length(15.0, 'px')`. Addition and subtraction convert the right operand into the left one's unit, so the result keeps the **left** unit.
3.  `Length(20.0, 'px')`. Multiplication and division take a plain scalar.

Supported units: `%`, `ch`, `cm`, `em`, `ex`, `in`, `mm`, `pc`, `pt`, `px`, `Q`, `rem`, `vh`, `vmax`, `vmin`, `vw`.

!!! warning "Which units convert into which"
    Conversion only happens inside two separate groups: `px`, `pt`, `pc` and user units convert into one another, and so do `cm`, `mm`, `in` and `Q`. Crossing between the groups would require assuming a DPI, so it raises `SvgUnitConversionError` &mdash; `Length(10, "px") + Length(5, "cm")` fails. Font- and viewport-relative units (`em`, `ex`, `ch`, `rem`, `%`, `vw`, `vh`, `vmin`, `vmax`) depend on context that isn't available at this level and convert to nothing at all.

### Color

CSS-style color values. You can use named colors, hex notation, or the `rgb()` function:

```python { .annotate }
from svglab import Color

Color("red")  # named color
Color("#ff6600")  # hex
Color("rgb(255,0,0)")  # RGB function

Color("red") == Color("#ff0000")  # (1)!
```

1.  `True`. Colors compare by their resolved RGBA values, not by how they were written. The original spelling is still kept for serialization, so what ends up in the file depends on the [`Formatter`](serialization.md#colors).

### Angle

Rotation and skew values with a unit:

```python
from svglab import Angle

Angle(45, "deg")  # degrees
Angle(0.785, "rad")  # radians
Angle(50, "grad")  # gradians
Angle(0.25, "turn")  # turns
```

### IRI

An *Internationalized Resource Identifier* &mdash; used for cross-references like clip paths, gradients, and filters:

```python
from svglab import Iri

Iri(fragment="myGradient")  # references id="myGradient"
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

SVG attribute names don't always work as Python identifiers, so <span class="svglab">svglab</span> applies two simple rules:

1. **Hyphens become underscores** &mdash; `stroke-width` → `stroke_width`
2. **Colons become underscores** &mdash; `xlink:href` → `xlink_href`, `xml:space` → `xml_space`
3. **Reserved words get a trailing underscore** &mdash; `class` → `class_`, `in` → `in_`, `from` → `from_`

Anything that is already a valid Python identifier is left alone &mdash; camel-cased SVG names keep their spelling, so it's `viewBox`, `gradientTransform` and `stdDeviation`, not `view_box` and friends.

You always use the Python name when reading or writing properties.

## Attribute groups

Not every attribute applies to every element. The SVG spec organizes attributes into logical groups, and <span class="svglab">svglab</span> does the same with *attribute mixin classes*:

| Mixin class | Examples | What it's for |
|-------------|----------|--------------|
| [`CoreAttrs`](../api-reference/attribute-groups.md#svglab.attrs.attrgroups.CoreAttrs) | `id`, `lang`, `xml_base`, `xml_lang`, `xml_space` | Universal identification |
| [`PresentationAttrs`](../api-reference/attribute-groups.md#svglab.attrs.attrgroups.PresentationAttrs) | `fill`, `stroke`, `opacity`, `font_size`, `transform` | Visual appearance (68 attributes) |
| [`ConditionalProcessingAttrs`](../api-reference/attribute-groups.md#svglab.attrs.attrgroups.ConditionalProcessingAttrs) | `requiredFeatures`, `systemLanguage` | Conditional rendering |
| [`AnimationTimingAttrs`](../api-reference/attribute-groups.md#svglab.attrs.attrgroups.AnimationTimingAttrs) | `begin`, `dur`, `repeatCount` | Timing for SMIL animations |
| [`XlinkAttrs`](../api-reference/attribute-groups.md#svglab.attrs.attrgroups.XlinkAttrs) | `xlink_href`, `xlink_title` | Cross-document references |
| [`GraphicalEventsAttrs`](../api-reference/attribute-groups.md#svglab.attrs.attrgroups.GraphicalEventsAttrs) | `onclick`, `onload`, `onmouseover` | Event handlers |

There are fourteen such groups in total. `CoreAttrs` and `PresentationAttrs` sit on the base `Element` class, so **every** element has them; the rest are mixed in per element. Attributes that belong to only one or two elements get their own single-attribute mixin instead of a group &mdash; that's where `Rect` picks up `x`, `y`, `width`, `height`, `rx` and `ry`, and `Animate` picks up its timing and value attributes on top of the presentation attributes it inherits.

!!! tip
    You can explore which attributes an element supports using your IDE's autocompletion, or check the [API Reference: Attribute Groups](../api-reference/attribute-groups.md).

## Validation

Attributes are validated at assignment time. If you pass a value of the wrong type, you'll get an immediate error rather than a silently malformed SVG:

```python
from svglab import Rect, Color, Length

rect = Rect()
rect.fill = Color("blue")  # ✓
rect.fill = Length(10)  # ✗ ValidationError
```

!!! svglab "Pydantic under the hood"
    Element classes are built on [Pydantic](https://docs.pydantic.dev/) models. That buys you runtime type checking with clear error messages, and &mdash; because the fields are properly typed &mdash; an editor that can autocomplete attribute names, flag mismatches and show documentation on hover before you run anything.

## Extra attributes

Real-world SVGs often contain attributes that aren't part of the SVG specification &mdash; `data-*` attributes, framework-specific props, or attributes from other XML namespaces.

<span class="svglab">svglab</span> preserves these as **extra attributes** so nothing is lost during round-tripping:

```python
from svglab import parse_svg

svg = parse_svg('<svg><rect data-tooltip="hello" custom:foo="bar"/></svg>')
rect = svg.find("rect")

rect.extra_attrs()  # {"data-tooltip": "hello", "custom:foo": "bar"}
```

`extra_attrs()` is a method, not a property, and the mapping it returns should be treated as read-only. Extra attributes are stored as plain strings (no type conversion) and are written back exactly as they were read.

## Next steps

<div class="grid cards" markdown>

-   __[Elements](elements.md)__ &mdash; creating elements and building SVG trees
-   __[Traits](traits.md)__ &mdash; which operations are available on which elements
-   __[Serialization](serialization.md)__ &mdash; control how attribute values are formatted in output
-   __[API Reference: Attributes](../api-reference/attributes.md)__ &mdash; complete attribute listing
-   __[API Reference: Attribute Groups](../api-reference/attribute-groups.md)__ &mdash; which attributes belong to which groups

</div>
