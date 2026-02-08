# Transforms

SVG supports six affine transformations that can reposition, resize, rotate, and skew elements. <span style="font-variant: small-caps;">svglab</span> represents each as a typed Python object and provides tools for composing, applying, and "baking in" transforms.

## Transform types

| Class | SVG syntax | What it does |
|-------|-----------|-------------|
| `Translate` | `translate(tx, ty)` | Move horizontally and/or vertically |
| `Rotate` | `rotate(angle, cx, cy)` | Rotate around a point |
| `Scale` | `scale(sx, sy)` | Scale along one or both axes |
| `SkewX` | `skewX(angle)` | Horizontal shear |
| `SkewY` | `skewY(angle)` | Vertical shear |
| `Matrix` | `matrix(a, b, c, d, e, f)` | Arbitrary 2D affine transform |

### Creating transforms

```python
from svglab import Translate, Rotate, Scale, SkewX

t = Translate(50, 100)
r = Rotate(45)                   # around the origin
r2 = Rotate(45, cx=50, cy=50)    # around (50, 50)
s = Scale(2, 0.5)
sk = SkewX(angle=15)
```

!!! info "Rotation center"
    In SVG, `rotate(45)` rotates around the origin (top-left corner), which often isn't what you want. `rotate(45, cx, cy)` rotates around the point $(cx, cy)$ instead. <span style="font-variant: small-caps;">svglab</span>'s `Rotate` class supports both forms.

## Setting transforms on elements

The `transform` attribute accepts a list of transform objects:

```python
from svglab import Rect, Translate, Rotate, Length

rect = Rect(width=Length(100), height=Length(50))
rect.transform = [Translate(50, 50), Rotate(30)]
```

When serialized, this becomes `transform="translate(50, 50) rotate(30)"`.

## Composing transforms

Multiple transforms can be **composed** into a single equivalent `Matrix` using `compose()`:

```python
from svglab import compose, Translate, Scale

combined = compose([Translate(10, 20), Scale(2)])
```

!!! note "Composition order"
    Transforms compose left to right. `compose([A, B])` means "apply A first, then B" &mdash; matching the order you'd write them in an SVG `transform` attribute.

## Applying transforms

### To points

Transform a single `Point`:

```python
from svglab import Point, Translate

point = Point(10, 20)
moved = Translate(5, 5) @ point   # Point(15, 25)
```

### To path data

Transform every coordinate in a `PathData` sequence:

```python
path_data = Scale(2, 2) @ path_data
```

This is more efficient than nesting the element in a group with a `transform` attribute, because the coordinates are modified directly. See [Path Data: Transforming path data](path-data.md#transforming-path-data) for more.

### To elements (reification)

Transforms on an element are normally stored as an attribute and interpreted by the SVG renderer. **Reification** bakes the transform directly into the element's geometry, removing the `transform` attribute entirely.

```python
svg.reify()
```

This is useful for optimization and for ensuring consistent rendering across viewers. Under the hood, reification:

1. Converts the transform into a `Matrix`
2. Applies it to geometric attributes (positions, sizes, path data)
3. Adjusts stroke widths to compensate for scaling
4. Removes the `transform` attribute

!!! warning
    Reification is a **lossy** operation &mdash; it modifies the element's attributes in place and cannot be undone. It works best on [basic shapes](traits.md#shapes-and-basic-shapes) and paths.

!!! warning "Non-uniform scaling"
    Only **translate** and **scale** transforms can be reified directly. For rotations and skews, the element is first [converted to a path](path-data.md#converting-shapes-to-paths) (if possible) so the transform can be applied to the coordinates. Non-uniform scaling (different `sx` and `sy`) on elements with attributes like `r` (radius) that don't distinguish between axes will raise an error &mdash; convert to a path first.

For more on reification and related operations, see [Graphical Operations](graphics.md).

## The `Matrix` type

Every transform can be expressed as a 2D affine matrix:

$$
\begin{bmatrix} a & c & e \\ b & d & f \\ 0 & 0 & 1 \end{bmatrix}
$$

You can create one directly or convert any other transform:

```python
from svglab import Matrix, Translate

m = Matrix(1, 0, 0, 1, 10, 20)              # same as Translate(10, 20)
m2 = Translate(10, 20).to_matrix()           # convert explicitly
```

Every transform type has a `.to_matrix()` method for when you need to do arithmetic or compose transforms manually.

## Next steps

- [Path Data](path-data.md) &mdash; transforming path coordinates
- [Graphical Operations](graphics.md) &mdash; reification and geometry manipulation
- [Serialization](serialization.md) &mdash; controlling transform output format
