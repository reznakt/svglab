# Graphical Operations

<span style="font-variant: small-caps;">svglab</span> can go beyond manipulating the SVG DOM &mdash; it can **render** elements, compute **bounding boxes**, extract **masks**, and **reify** transforms into geometry. These operations bridge the gap between the vector description and the actual pixels on screen.

!!! note "Requirements"
    Graphical operations rely on an SVG renderer (resvg) and image processing libraries (Pillow, NumPy). These are included as dependencies and work out of the box.

## Rendering

The `.render()` method rasterizes an SVG element into a PIL `Image`:

```python
from pathlib import Path
from svglab import parse_svg

svg = parse_svg(Path("drawing.svg"))
image = svg.render()          # PIL Image (RGBA)
image.save("output.png")
```

!!! info "How rendering works"
    <span style="font-variant: small-caps;">svglab</span> uses [resvg](https://github.com/baseplate-admin/resvg-py) under the hood, a high-quality SVG renderer written in Rust. The result is a pixel-perfect rasterization that matches what you'd see in a modern browser.

!!! tip "Rendering subtrees"
    When you render a single element (rather than the root `Svg`), it's temporarily wrapped in an `<svg>` for rendering. This means inherited styles from parent elements won't apply &mdash; what you see is the element in isolation.

## Bounding boxes

A bounding box is the smallest axis-aligned rectangle that encloses an element's geometry. <span style="font-variant: small-caps;">svglab</span> provides two variants:

### `get_bbox()` &mdash; geometric bounding box

Returns the bounding box based on the element's geometry alone, ignoring visual effects like clipping and masking:

```python
box = svg.get_bbox()
# box is a tuple (x_min, y_min, x_max, y_max) or None
```

### `get_bbox(visible_only=True)` &mdash; rendered bounding box

Returns the bounding box of the element **as it actually appears** after applying clips, masks, opacity, and filters. This is computed by rendering the element and analyzing the visible pixels:

```python
vbox = svg.get_bbox(visible_only=True)
```

!!! tip "When to use which"
    Use `get_bbox()` when you need the theoretical extent of the geometry (e.g. for layout calculations). Use `get_bbox(visible_only=True)` when you need to know what the user actually sees (e.g. for cropping or collision detection).

## Masks

Masks give you a pixel-level view of where an element draws content. They're returned as NumPy arrays where each pixel is either visible or transparent.

### `get_mask()`

The full geometric mask, including parts that might be clipped or hidden:

```python
import numpy as np

m = svg.get_mask()   # NumPy boolean array
```

### `get_mask(visible_only=True)`

The mask of only the **actually visible** pixels, after clips and masks are applied:

```python
vm = svg.get_mask(visible_only=True)
```

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

Under the hood, reification:

1. Decomposes the `transform` into a matrix
2. Applies translations to position attributes (`x`, `y`, `cx`, `cy`, &hellip;)
3. Applies scaling to size attributes (`width`, `height`, `r`, `rx`, `ry`, &hellip;)
4. Transforms path data coordinates directly
5. Adjusts `stroke-width` to compensate for scaling
6. Removes the `transform` attribute

!!! warning "Lossy operation"
    Reification modifies attributes in place and cannot be undone. For complex transforms (rotation, skew), basic shapes may need to be [converted to paths](path-data.md#converting-shapes-to-paths) first to accurately represent the transformed geometry.

!!! note "Silently skipped elements"
    Reification quietly skips elements it can't safely transform, including `<use>`, `<pattern>`, elements that reference paint servers (gradients, clip paths), and gradients using `objectBoundingBox` units. No error is raised &mdash; those elements simply keep their `transform` attribute unchanged.

## Shape-to-path conversion

As described in [Traits](traits.md#shapes-and-basic-shapes), basic shapes can be converted to `Path` elements. This is often a preprocessing step before other graphical operations, since paths are the most general geometry representation:

```python
from svglab import Rect, Length

rect = Rect(x=Length(10), y=Length(20), width=Length(100), height=Length(50))
path = rect.to_path()
```

## Next steps

- [Transforms](transforms.md) &mdash; the transform types that reification consumes
- [Path Data](path-data.md) &mdash; the universal geometry representation
- [Traits](traits.md) &mdash; which elements support graphical operations
- [Serialization](serialization.md) &mdash; writing the optimized result to a file
