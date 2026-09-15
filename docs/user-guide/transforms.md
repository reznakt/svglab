# Transforms

SVG supports six affine transformations that can reposition, resize, rotate, and skew elements. <span class="svglab">svglab</span> represents each as a typed Python object and provides tools for composing, applying, and "baking in" transforms.

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
r = Rotate(45)  # around the origin
r2 = Rotate(45, cx=50, cy=50)  # around (50, 50)
s = Scale(2, 0.5)
sk = SkewX(angle=15)
```

!!! info "Rotation center"
    In SVG, `rotate(45)` rotates around the origin (top-left corner), which often isn't what you want. `rotate(45, cx, cy)` rotates around the point $(cx, cy)$ instead. <span class="svglab">svglab</span>'s `Rotate` class supports both forms.

## Setting transforms on elements

The `transform` attribute accepts a list of transform objects:

```python
from svglab import Rect, Translate, Rotate, Length

rect = Rect(width=Length(100), height=Length(50))
rect.transform = [Translate(50, 50), Rotate(30)]
```

When serialized, this becomes `transform="translate(50 50) rotate(30)"`. Arguments are joined with the formatter's `list_separator`, which is a space by default.

## Composing transforms

Multiple transforms can be **composed** into a single equivalent `Matrix` using `compose()`:

```python
from svglab import compose, Translate, Scale

combined = compose([Translate(10, 20), Scale(2)])
```

!!! note "Composition order"
    `compose()` takes the transforms in the order you'd write them in an SVG `transform` attribute, and follows the same rule: the **rightmost** transform is the one applied to the coordinates first. `compose([Translate(10, 20), Scale(2)])` scales a point, then translates it, exactly like `transform="translate(10, 20) scale(2)"` would.

    ```python
    compose([Translate(10, 20), Scale(2)]) @ Point(1, 1)  # Point(12.0, 22.0)
    ```

    `compose()` takes a single iterable, not varargs.

## Applying transforms

### To points

Transform a single `Point`:

```python
from svglab import Point, Translate

point = Point(10, 20)
moved = Translate(5, 5) @ point  # Point(15, 25)
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

This is useful for optimization and for ensuring consistent rendering across viewers. See [Graphical Operations: Reification](graphics.md#reification) for the full explanation, including the internal steps, caveats, and limitations.

## The `Matrix` type

Every transform can be expressed as a 2D affine matrix:

$$
\begin{bmatrix} a & c & e \\ b & d & f \\ 0 & 0 & 1 \end{bmatrix}
$$

You can create one directly or convert any other transform:

```python
from svglab import Matrix, Translate

m = Matrix(1, 0, 0, 1, 10, 20)  # same as Translate(10, 20)
m2 = Translate(10, 20).to_matrix()  # convert explicitly
```

Every transform type has a `.to_matrix()` method for when you need to do arithmetic or compose transforms manually.

## Next steps

<div class="grid cards" markdown>

-   __[Path Data](path-data.md)__ &mdash; transforming path coordinates
-   __[Graphical Operations](graphics.md)__ &mdash; reification and geometry manipulation
-   __[Serialization](serialization.md)__ &mdash; controlling transform output format

</div>
