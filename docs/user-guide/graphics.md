# Graphical Operations

<span class="svglab">svglab</span> can go beyond manipulating the SVG DOM &mdash; it can **render** elements, compute **bounding boxes**, extract **masks**, and **reify** transforms into geometry. These operations bridge the gap between the vector description and the actual pixels on screen.

!!! note "Requirements"
    Graphical operations rely on an SVG renderer (resvg) and image processing libraries (Pillow, NumPy). These are included as dependencies and work out of the box.

## Rendering

The `.render()` method rasterizes an SVG document into a PIL `Image`. It is defined on `Svg` only &mdash; rasterizing needs a complete document with its own dimensions:

```python { .annotate }
from pathlib import Path
from svglab import parse_svg

svg = parse_svg(Path("drawing.svg"))
image = svg.render()  # (1)!
image.save("output.png")
```

1.  An RGBA `PIL.Image`, rasterized by [resvg](https://github.com/baseplate-admin/resvg-py) &mdash; a renderer written in Rust that tracks what a modern browser would draw.

`render()` takes `width` and `height` to override the document's own dimensions (the aspect ratio is preserved either way), plus resvg's font and rendering options &mdash; `background`, `dpi`, `font_family`, `shape_rendering`, `zoom` and friends.

!!! tip "Rendering a single element"
    There is no `.render()` on `Rect` or `G`. To rasterize part of a document, copy the subtree into an `Svg` of its own &mdash; or use [`get_mask()`](#masks), which renders just that element for you.

## Bounding boxes

A bounding box is the smallest axis-aligned rectangle that encloses an element. `get_bbox()` is available on graphics elements and containers alike, and comes in two variants. Both are computed by **rendering**, so the result is a tuple of integer pixel coordinates `(x_min, y_min, x_max, y_max)` in the rendered document's pixel space &mdash; or `None` if nothing was drawn.

### `get_bbox()` &mdash; the element on its own

Renders the document with every other element hidden and this one forced to be visible, then measures the drawn pixels:

```python { .annotate }
box = rect.get_bbox()  # (1)!
```

1.  `(9, 9, 41, 41)` for a 30&times;30 rect at (10, 10) &mdash; or `None` if nothing was drawn.

    The box runs a little wide because making the element visible means giving it a solid black fill *and* stroke, so an unstroked shape gains about half a stroke on each side.

Fill, stroke and opacity settings on the element are overridden, so a transparent or `display: none` element still gets a box. A clip path or mask applied to the element is *not* removed, so a clipped element is measured clipped &mdash; and if its clip path is defined elsewhere in the document, the result can even be `None`.

### `get_bbox(visible_only=True)` &mdash; what the element contributes

Renders the whole document twice, with and without this element, and measures the pixels that differ:

```python
vbox = rect.get_bbox(visible_only=True)
```

This is the element **as it actually appears**: clips, masks, opacity and filters all apply, and any part covered by an element painted on top of it is excluded.

!!! tip "When to use which"
    Use `get_bbox()` for the extent of the element considered by itself (e.g. for layout calculations). Use `get_bbox(visible_only=True)` when you need to know what the user actually sees (e.g. for cropping or collision detection). The second variant renders twice, in a process pool, so it is markedly slower.

## Masks

Masks give you a pixel-level view of where an element draws content. They are 2D NumPy boolean arrays the size of the rendered document, `True` where the element is present. The two variants match the two bounding boxes above &mdash; in fact `get_bbox()` is just the box around the corresponding mask.

### `get_mask()`

The element rendered on its own, forced visible:

```python
m = rect.get_mask()  # NumPy bool array, shape (height, width)
```

### `get_mask(visible_only=True)`

Only the pixels the element actually contributes to the rendered document, after clips, masks, opacity and overlapping elements:

```python
vm = rect.get_mask(visible_only=True)
```

Both accept `width` and `height` to render at a size other than the document's own.

## Reification

**Reification** is the process of *baking* an element's `transform` attribute into its geometry, so the visual result stays the same but the transform is removed. This is one of the key optimization techniques in SVG processing.

### Why reify?

Consider a rectangle with a translation:

```xml
<rect x="0" y="0" width="100" height="50" transform="translate(10, 20)"/>
```

After reification, the transform is gone and the coordinates reflect the final position:

```xml
<rect x="10" y="20" width="100" height="50"/>
```

The rendered output is identical, but the SVG is simpler. This matters for:

- **File size** &mdash; fewer attributes
- **Interoperability** &mdash; some tools handle transforms inconsistently
- **Downstream processing** &mdash; coordinates reflect actual positions

### Using reification

Call `.reify()` on any element to recursively reify it and all its descendants:

```python
svg.reify()
```

Under the hood, reification works through the `transform` list left to right and, for each entry:

1. Decomposes a `Matrix` into simpler transforms, and adjusts the parameters of a `Rotate` or a skew so a translation or scale can be pulled out of it
2. Applies translations to position attributes (`x`, `y`, `cx`, `cy`, &hellip;)
3. Applies scaling to size attributes (`width`, `height`, `r`, `rx`, `ry`, &hellip;)
4. Transforms path data coordinates directly
5. Adjusts `stroke-width`, dash patterns and `pathLength` to compensate for scaling

Only translation and scaling can actually be baked into an element. Reification **stops at the first transform it can't apply** &mdash; a non-uniform scale on a circle, say &mdash; and leaves that transform and everything before it in the attribute. The `transform` attribute is removed only when the whole list was consumed.

!!! warning "Lossy operation"
    Reification modifies attributes in place and cannot be undone. For complex transforms (rotation, skew), basic shapes may need to be [converted to paths](path-data.md#converting-shapes-to-paths) first to accurately represent the transformed geometry. Every length involved must be convertible to user units, or `SvgUnitConversionError` is raised.

!!! svglab "Silently skipped elements"
    Reification quietly skips elements it can't safely transform: `<use>`, `<pattern>`, elements that reference other elements (paint servers, clip paths), and gradients using `objectBoundingBox` units. No error is raised &mdash; the element keeps its `transform` attribute unchanged, and because the recursion stops there, **so does its whole subtree**.

## Shape-to-path conversion

Basic shapes can be converted to `Path` elements via `.to_path()` and `.to_path_data()`. This is often a preprocessing step before other graphical operations, since paths are the most general geometry representation. See [Traits: Shapes and basic shapes](traits.md#shapes-and-basic-shapes) for details and examples.

## Next steps

<div class="grid cards" markdown>

-   __[Transforms](transforms.md)__ &mdash; the transform types that reification consumes
-   __[Path Data](path-data.md)__ &mdash; the universal geometry representation
-   __[Traits](traits.md)__ &mdash; which elements support graphical operations
-   __[Serialization](serialization.md)__ &mdash; writing the optimized result to a file

</div>
