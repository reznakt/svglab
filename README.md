<div align="center">
  <img width="200" src="https://raw.githubusercontent.com/reznakt/svglab/refs/heads/main/assets/logo.svg" />

  <h1 align="center">
    <picture>
      <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/reznakt/svglab/refs/heads/main/assets/wordmark-dark.svg" />
      <img alt="svglab" width="260" src="https://raw.githubusercontent.com/reznakt/svglab/refs/heads/main/assets/wordmark-light.svg" />
    </picture>
  </h1>

  <p align="center">
    <em>The Python library for parsing, manipulating, and optimizing SVG files</em>
  </p>

  <p align="center">
    <a href="https://pypi.org/project/svglab/"><img alt="PyPI - Version" src="https://img.shields.io/pypi/v/svglab" /></a>
    <a href="https://pypi.org/project/svglab/"><img alt="PyPI - Python Version" src="https://img.shields.io/pypi/pyversions/svglab" /></a>
    <a href="https://pypi.org/project/svglab/"><img alt="PyPI - Types" src="https://img.shields.io/pypi/types/svglab" /></a>
    <a href="https://codecov.io/github/reznakt/svglab"><img alt="Test coverage" src="https://codecov.io/github/reznakt/svglab/graph/badge.svg" /></a>
    <br />
    <a href="https://svglab.rocks/"><img alt="Documentation" src="https://img.shields.io/badge/docs-svglab.rocks-blue" /></a>
    <a href="https://pepy.tech/project/svglab"><img alt="PyPI - Downloads" src="https://img.shields.io/pepy/dt/svglab" /></a>
    <a href="https://github.com/reznakt/svglab/blob/main/LICENSE"><img alt="License" src="https://img.shields.io/pypi/l/svglab" /></a>
  </p>
</div>

<br />

## About the project

### Features

- SVG parsing, manipulation, and writing
- Support for all SVG 1.1 elements and attributes
- Partial support for SVG 2
- Support for special XML entities (`CDATA`, comments, text)
- Attributes are parsed into native Python types for easy manipulation
- Highly configurable formatting options:
  - indentation level
  - maximum precision for floating-point numbers
  - color mode (`rgb`, `rgba`, `hsl`, `hex`, `named`)
  - relative/absolute path commands
  - scientific notation for small/large numbers
  - and many more...
- Strong type safety:
  - one class per distinct SVG element
  - typed attributes
  - runtime validation thanks to [pydantic](https://pypi.org/project/pydantic/)
- Support for all [beautifulsoup4](https://pypi.org/project/beautifulsoup4/) parsers (e.g., `html.parser`, `lxml`, `html5lib` via the `html5lib` extra)
- SVG can be rendered into a raster image using [resvg](https://lib.rs/crates/resvg), through bindings that ship with the library
- Support for calculating the bounding box and mask of an element
- Support for applying transformations in the `transform` attribute ("reification")

```mermaid
---
title: Entity hierarchy
---

graph TD
  Entity:::abc --> CharacterData
  Entity --> Element

  Element:::abc --> G
  Element --> Svg
  Element --> Rect
  Element --> Circle
  Element --> etc1[...]

  CharacterData:::abc --> RawText
  CharacterData --> Comment
  CharacterData --> CData

  etc1:::etc

  classDef abc stroke-dasharray:5 5,stroke-width:2px;
  classDef etc stroke:gray,stroke-width:2px;
  classDef default stroke:orange,stroke-width:2px;
```

## Getting started

### Prerequisites

- [CPython](https://www.python.org/) 3.10+
- [uv](https://docs.astral.sh/uv/) (development only)
- [just](https://just.systems/) (development only; optional)

### Installation

**From PyPI**:

```sh
pip install svglab
```

**From source**:

```sh
# Via HTTPS
pip install git+https://github.com/reznakt/svglab.git

# Via SSH
pip install git+ssh://git@github.com/reznakt/svglab.git
```

## Usage

### Parsing

```python
svg = parse_svg(
    """
    <svg xmlns="http://www.w3.org/2000/svg" width="100" height="100">
      <g>
          <rect
            id="background"
            width="100cm"
            height="100%"
            transform="rotate(45)"
            stroke="red"
          />
          <rect color="hsl(0, 100%, 100%)"/>
          <!-- This is a comment -->
          <![CDATA[.background { fill: blue; }]]>
          Hello SVG!
          <path d="M 10,10 H 10 L 100,100 Q 100,100 50,50 v 100 Z"/>
          <path d="M0,0 10,10 20,20 S 100,100 50,50 t 100,100 M 50,50 z"/>
          <path d="M0,0A50,50 90 1 0 100,100v100h-10z"/>
          <polygon points="0,0 100,0 100,100 0,100"/>
      </g>
    </svg>
"""
)

print(svg)
```

### Building elements

```python
group = G().add_children(
    Rect(
        width=Length(15, "px"),
        height=Length(20),
        transform=[SkewX(45.123), Translate(10, 20)],
        color=Color("#ff0000"),
    ),
    Comment("This is a comment"),
    CData(".background { fill: blue; }"),
    RawText("Hello SVG!"),
    Path(
        d=PathData()
        .move_to(Point(10, 10))
        .line_to(Point(100, 100))
        .quadratic_bezier_to(Point(100, 100), Point(50, 50))
        .smooth_quadratic_bezier_to(Point(100, 100))
        .move_to(Point(50, 50))
        .cubic_bezier_to(Point(100, 100), Point(100, 100), Point(10, 10))
        .smooth_cubic_bezier_to(Point(100, 100), Point(50, 50))
        .arc_to(
            Point(50, 50), 90, Point(100, 100), large=True, sweep=False
        )
        .vertical_line_to(100)
        .horizontal_line_to(-10, relative=True)
        .close()
    ),
    Polyline(
        points=[
            Point(0, 0),
            Point(100, 0),
            Point(100, 100),
            Point(0, 100),
        ],
        stroke_linecap="square",
        opacity=0.5,
    ),
)

# Add the element to the SVG
svg.add_child(group)
```

### Attributes and output

```python
print(svg.xmlns)  # http://www.w3.org/2000/svg
svg.x = Length(10, "px")

# Save to a file
svg.save(sys.stdout)
```

### Searching the tree

```python
print(*svg.find_all(Rect), sep="\n")
rect = svg.find(G).find(Rect)
```

### Geometry and rendering

```python
print(rect.get_bbox())
print(rect.get_mask())

# Render the SVG to an image
image = svg.render()
print(image)
```

### Transformations

```python
svg.reify()
print(svg.to_xml())

# Change the view box
svg.set_viewbox((0, 0, 50, 50))
print(svg.to_xml())
```

## Development

### Setup

```sh
# Install dependencies
uv sync

# Activate the virtual environment
source .venv/bin/activate

# Optional: Install pre-commit hooks
pre-commit install
```

### Common tasks

```sh
# Run tests
just test

# Run type checker
just typecheck

# Run linter
just lint

# Fix linting errors
just lint-fix

# Run formatter
just format

# Fix formatting errors
just format-fix
```

## License

This software is distributed under the MIT License. See [`LICENSE`](LICENSE) for more information.
