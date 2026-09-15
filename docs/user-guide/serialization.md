# Serialization

Once you've built or modified an SVG tree, you'll want to turn it back into XML. <span class="svglab">svglab</span> gives you two levels of control: a simple one-liner for quick output, and a powerful `Formatter` class for fine-grained customization.

## Basic output

### `to_xml()`

Every element has a `.to_xml()` method that returns a string of XML:

```python
from svglab import Svg, Rect, Length

svg = Svg(width=Length(200), height=Length(200))
svg.add_child(Rect(width=Length(100), height=Length(50)))

print(svg.to_xml())
```

### `save()`

To write directly to a file, use `.save()` with a file path or `Path` object:

```python
svg.save("output.svg")
```

Both methods accept an optional `Formatter` to customize the output (see below).

## The `Formatter`

The `Formatter` class controls **how** the XML is produced &mdash; indentation, color format, number precision, path data style, and much more. It has over 20 options organized into logical categories.

### Using a formatter

There are three equivalent ways to apply a formatter:

=== "Pass to `to_xml()`"

    ```python
    from svglab import Formatter

    fmt = Formatter(indent=4, general_precision=2)
    xml = svg.to_xml(formatter=fmt)
    ```

=== "Pass to `save()`"

    ```python
    svg.save("output.svg", formatter=fmt)
    ```

=== "Context manager"

    Apply a formatter to **all** serialization within a block:

    ```python { .annotate }
    with fmt:
        xml = svg.to_xml()  # (1)!
        svg.save("output.svg")  # (2)!
    ```

    1.  No `formatter=` argument, but `fmt` applies anyway.
    2.  And to every other serialization call in the block, at any depth of the call stack.

    Handy in scripts that serialize many elements: set it once and forget about it.

!!! warning "The context reaches further than it looks"
    A `Formatter` context manager affects **every** `.to_xml()` and `.save()` call made while the block is open, including ones inside functions you call. Unexpected output from a bare `.to_xml()` usually means a formatter is active somewhere up the call stack.

    Nesting is safe: the innermost formatter wins, and leaving a block restores the previous one.

## Formatting options

### Indentation and whitespace

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `indent` | `int` | `2` | Spaces per nesting level |
| `spaces_around_attrs` | `bool` | `False` | Add spaces around attribute values |
| `spaces_around_function_args` | `bool` | `False` | Add spaces inside function call parentheses |

### Colors

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `color_mode` | `str` | `"auto"` | Output format: `"auto"`, `"named"`, `"hex-short"`, `"hex-long"`, `"rgb"`, `"hsl"`, or `"original"` |
| `alpha_channel` | `str` | `"float"` | Alpha channel format: `"float"` or `"percentage"` |

!!! example "Color mode comparison"
    The same color serialized with different `color_mode` settings:

    | Mode | Output |
    |------|--------|
    | `hex-short` | `#f00` |
    | `hex-long` | `#ff0000` |
    | `rgb` | `rgb(255 0 0)` |
    | `hsl` | `hsl(0 100% 50%)` |
    | `named` | `red` |

    The components are joined with `list_separator`, so switching that to `", "` gives the more familiar `rgb(255, 0, 0)`.

### Numbers and precision

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `general_precision` | `int \| FloatPrecisionSettings \| None` | `FloatPrecisionSettings()` | Precision settings for general numbers |
| `coordinate_precision` | `int \| FloatPrecisionSettings \| None` | `None` | Override for coordinate values |
| `angle_precision` | `int \| FloatPrecisionSettings \| None` | `None` | Override for angle values |
| `opacity_precision` | `int \| FloatPrecisionSettings \| None` | `None` | Override for opacity values |
| `scale_precision` | `int \| FloatPrecisionSettings \| None` | `None` | Override for scale values |
| `strip_leading_zero` | `bool` | `True` | Omit leading zero for numbers between -1 and 1 (e.g., `.5`) |
| `show_decimal_part_if_int` | `bool` | `False` | Write `1.0` instead of `1` |
| `small_number_scientific_threshold` | `float \| None` | `1e-06` | Below this magnitude, use scientific notation; `None` disables it |
| `large_number_scientific_threshold` | `int \| None` | `1000000` | Above this magnitude, use scientific notation; `None` disables it |

!!! info "Precision hierarchy"
    The type-specific precision settings take precedence over the general `general_precision`. If neither is set, a default fallback precision is used.

### Path data

SVG path data has its own mini-language, and the formatter gives you detailed control over how it's written:

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `path_data_coordinates` | `str` | `"absolute"` | Force coordinates to `"absolute"` or `"relative"` |
| `path_data_commands` | `str` | `"implicit"` | `"implicit"` omits repeated command letters; `"explicit"` always writes them |
| `path_data_shorthand_line_commands` | `str` | `"always"` | Use shorthand line commands (`H`, `V`): `"always"`, `"never"`, or `"original"` |
| `path_data_shorthand_curve_commands` | `str` | `"always"` | Use shorthand curve commands (`S`, `T`): `"always"`, `"never"`, or `"original"` |
| `path_data_space_before_args` | `bool` | `False` | Add space before command arguments (e.g., `M 0 0` vs `M0 0`) |

For more on path data, see [Path Data](path-data.md).

### Lengths and units

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `length_unit` | `str \| Iterable` | `"preserve"` | Convert lengths to a specific unit, or `"preserve"` to keep originals |

### Separators

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `list_separator` | `str` | `" "` | Separator between list values |
| `point_separator` | `str` | `","` | Separator between point coordinates |

### XML structure

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `xmlns` | `str` | `"original"` | SVG namespace handling: `"always"`, `"never"`, or `"original"` |
| `attribute_order` | `dict` | `{}` | Custom attribute ordering per element (or `"*"` for all). Default order is alphabetical |

## Predefined formatters

<span class="svglab">svglab</span> ships with ready-made formatters for common use cases:

| Formatter | Purpose |
|-----------|---------|
| `DEFAULT_FORMATTER` | Sensible defaults for human-readable output |
| `MINIMAL_FORMATTER` | Compatibility-oriented output: original colors and path commands, no scientific notation, no stripped leading zeros, `xmlns` always written, 4-space indent |

```python
from svglab import DEFAULT_FORMATTER, MINIMAL_FORMATTER

svg.save("readable.svg", formatter=DEFAULT_FORMATTER)
svg.save("compatible.svg", formatter=MINIMAL_FORMATTER)
```

## Custom serialization

If you need to control how a particular object is serialized, you can implement the `CustomSerializable` protocol. This is useful when writing your own attribute types or extending the library:

```python
from svglab import get_current_formatter
from svglab.protocols import CustomSerializable


class MyValue(CustomSerializable):
    def serialize(self) -> str:
        return "my-custom-output"
```

`CustomSerializable` lives in `svglab.protocols` rather than the top-level package. It is a `Protocol`, so subclassing is optional &mdash; any object with a `serialize()` method is serialized through it.

The `serialize` method takes no arguments. If your custom type needs to respect the active formatter's settings, use `get_current_formatter()` to retrieve it.

## Next steps

<div class="grid cards" markdown>

-   __[Parsing](parsing.md)__ &mdash; reading SVGs back in
-   __[Path Data](path-data.md)__ &mdash; path-specific serialization options
-   __[Transforms](transforms.md)__ &mdash; transform serialization
-   __[API Reference: Elements](../api-reference/index.md)__ &mdash; `to_xml()` and `save()` on each element class

</div>
