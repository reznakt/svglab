# Path Data

The `<path>` element is SVG's most versatile drawing tool. Its `d` attribute is a compact string of drawing commands &mdash; move the pen here, draw a line there, trace a cubic Bézier curve &mdash; that can describe any shape. <span style="font-variant: small-caps;">svglab</span> parses this into a `PathData` object: a structured, manipulable sequence of typed commands.

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
    Uppercase letters (`M`, `L`, &hellip;) use **absolute** coordinates; lowercase (`m`, `l`, &hellip;) use coordinates **relative** to the current pen position. <span style="font-variant: small-caps;">svglab</span> preserves the original coordinate mode unless you explicitly convert it.

## Creating path data

### From a path element

When you parse an SVG or create a `Path` element, the `d` attribute is automatically a `PathData` object:

```python
from svglab import parse_svg

svg = parse_svg('<svg><path d="M 10 20 L 50 60 Z"/></svg>')
path = svg.find("path")

path.d   # PathData([MoveTo(...), LineTo(...), ClosePath()])
```

### Programmatically

Build path data by hand with command objects:

```python
from svglab import PathData, MoveTo, LineTo, ClosePath, Point

triangle = PathData([
    MoveTo(end=Point(0, 0)),
    LineTo(end=Point(100, 0)),
    LineTo(end=Point(50, 87)),
    ClosePath(),
])
```

## Working with commands

`PathData` behaves like a **sequence** &mdash; you can iterate, index, slice, and check its length:

```python
len(triangle)     # 4
triangle[0]       # MoveTo(point=Point(x=0, y=0))
triangle[-1]      # ClosePath()

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
    `PathData` is mutable. Methods like `.append()` and `.extend()` modify the path **in place**. Use the builder methods (`.line_to()`, `.move_to()`, etc.) for a fluent chaining style.

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

    rect = Rect(x=Length(10), y=Length(20), width=Length(100), height=Length(50))
    path_data = rect.to_path_data()
    ```

=== "Getting a path element"

    ```python
    path_element = rect.to_path()
    # Path element that draws the same rectangle
    ```

Both methods are available on all `BasicShape` elements: `Rect`, `Circle`, `Ellipse`, `Line`, `Polyline`, and `Polygon`.

## Serialization options

The [Formatter](serialization.md) provides several options specifically for path data output:

| Option | Effect |
|--------|--------|
| `path_data_coordinates` | Force all coordinates to `"absolute"` or `"relative"` |
| `path_data_commands` | `"implicit"` omits repeated command letters; `"explicit"` always writes them |
| `path_data_shorthand_line_commands` | Use shorthand line commands (`H`, `V`): `"always"`, `"never"`, or `"original"` |
| `path_data_shorthand_curve_commands` | Use shorthand curve commands (`S`, `T`): `"always"`, `"never"`, or `"original"` |
| `coordinate_precision` | Control the number of decimal places for coordinates |

```python
from svglab import Formatter

fmt = Formatter(
    path_data_coordinates="relative",
    coordinate_precision=1,
)

print(path.to_xml(formatter=fmt))
```

## Next steps

- [Transforms](transforms.md) &mdash; transformation types in detail
- [Traits](traits.md) &mdash; which elements support path conversion
- [Serialization](serialization.md) &mdash; all formatting options
- [API Reference: Elements](../api-reference/elements.md) &mdash; `Path`, `PathData`, and command classes
