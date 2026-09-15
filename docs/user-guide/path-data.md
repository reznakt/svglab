# Path Data

The `<path>` element is SVG's most versatile drawing tool. Its `d` attribute is a compact string of drawing commands &mdash; move the pen here, draw a line there, trace a cubic Bézier curve &mdash; that can describe any shape. <span class="svglab">svglab</span> parses this into a `PathData` object: a structured, manipulable sequence of typed commands.

## Path commands at a glance

Every SVG path is built from these commands:

| Command | Class | What it does |
|---------|-------|-------------|
| `M` / `m` | `MoveTo` | Move the pen without drawing |
| `L` / `l` | `LineTo` | Draw a straight line |
| `H` / `h` | `HorizontalLineTo` | Horizontal line (shorthand) |
| `V` / `v` | `VerticalLineTo` | Vertical line (shorthand) |
| `C` / `c` | `CubicBezierTo` | Cubic Bézier curve (two control points) |
| `S` / `s` | `SmoothCubicBezierTo` | Smooth cubic Bézier (reflected control point) |
| `Q` / `q` | `QuadraticBezierTo` | Quadratic Bézier curve (one control point) |
| `T` / `t` | `SmoothQuadraticBezierTo` | Smooth quadratic Bézier |
| `A` / `a` | `ArcTo` | Elliptical arc |
| `Z` / `z` | `ClosePath` | Close the current subpath |

!!! info "Absolute vs. relative"
    Uppercase letters (`M`, `L`, &hellip;) use **absolute** coordinates; lowercase (`m`, `l`, &hellip;) use coordinates **relative** to the current pen position. <span class="svglab">svglab</span> stores every command as absolute coordinates and picks the letter case on output, controlled by the formatter's `path_data_coordinates` option (`"absolute"` by default). A path parsed as `m 10 10 l 5 5` therefore serializes as `M10,10 15,15` unless you ask for `"relative"`.

## Creating path data

### From a path element

When you parse an SVG or create a `Path` element, the `d` attribute is automatically a `PathData` object:

```python
from svglab import parse_svg

svg = parse_svg('<svg><path d="M 10 20 L 50 60 Z"/></svg>')
path = svg.find("path")

path.d  # PathData(MoveTo(...), LineTo(...), ClosePath())
```

### Programmatically

Build path data by hand with command objects:

```python
from svglab import PathData, MoveTo, LineTo, ClosePath, Point

triangle = PathData(
    [
        MoveTo(end=Point(0, 0)),
        LineTo(end=Point(100, 0)),
        LineTo(end=Point(50, 87)),
        ClosePath(),
    ]
)
```

## Working with commands

`PathData` behaves like a **sequence** &mdash; you can iterate, index, slice, and check its length:

```python
len(triangle)  # 4
triangle[0]  # MoveTo(end=Point(x=0.0, y=0.0))
triangle[-1]  # ClosePath()

for cmd in triangle:
    print(cmd)
```

### Adding and combining

Append individual commands or extend a path:

```python
path_data = PathData([MoveTo(Point(0, 0))])
path_data.append(LineTo(end=Point(100, 0)))

# Extend with another path's commands
path_data.extend(other_path)
```

!!! note "Mutability"
    `PathData` is mutable. `.append()`, `.extend()` and the builder methods (`.move_to()`, `.line_to()`, &hellip;) all modify the path **in place**; the builders additionally return the same object, which is what makes chaining work.

!!! warning "A path has to start with a move"
    Every `PathData` must begin with a `MoveTo`. Appending to an empty path, or constructing one whose first command is anything else, raises `SvgPathMissingMoveToError`.

## Transforming path data

Path data can be transformed using the same [transform types](transforms.md) that apply to elements:

```python
from svglab import Translate, Scale

translated = Translate(50, 50) @ triangle
scaled = Scale(2) @ triangle
```

This applies the transform **to every coordinate** in the path, which is more efficient than wrapping the element in a `<g>` with a `transform` attribute. See [Transforms](transforms.md) for details on the available transform types.

## Converting shapes to paths

All [basic shapes](traits.md#shapes-and-basic-shapes) can be converted to equivalent path data. This is the foundation of many SVG optimization techniques &mdash; once everything is a path, you have a uniform representation to work with.

=== "Getting the path data"

    ```python
    from svglab import Rect, Length

    rect = Rect(
        x=Length(10), y=Length(20), width=Length(100), height=Length(50)
    )
    path_data = rect.to_path_data()
    ```

=== "Getting a path element"

    ```python
    path_element = rect.to_path()
    # Path element that draws the same rectangle
    ```

Both methods are available on all `BasicShape` elements: `Rect`, `Circle`, `Ellipse`, `Line`, `Polyline`, and `Polygon`.

## Serialization options

The [Formatter](serialization.md) provides several options specifically for path data output, including coordinate mode (absolute/relative), implicit vs. explicit command letters, shorthand commands, and coordinate precision. See [Serialization: Path data](serialization.md#path-data) for the full list of options.

```python
from svglab import Formatter

fmt = Formatter(path_data_coordinates="relative", coordinate_precision=1)

print(path.to_xml(formatter=fmt))
```

## Next steps

<div class="grid cards" markdown>

-   __[Transforms](transforms.md)__ &mdash; transformation types in detail
-   __[Traits](traits.md)__ &mdash; which elements support path conversion
-   __[Serialization](serialization.md)__ &mdash; all formatting options
-   __[API Reference: Elements](../api-reference/index.md)__ &mdash; the `Path` element class

</div>
