/* An editable svglab playground: the VS Code editor (Monaco) in front of
 * CPython in the browser (Pyodide).
 *
 * svglab itself is pure Python, so everything except rasterization works:
 * rendering, bounding boxes and masks need resvg, a native library that has
 * no WebAssembly build. Those entry points are replaced with a clear error.
 */

const PYODIDE_VERSION = "0.28.3";
const INDEX_URL = `https://cdn.jsdelivr.net/pyodide/v${PYODIDE_VERSION}/full/`;

const MONACO_VERSION = "0.52.2";
const MONACO_BASE = `https://cdn.jsdelivr.net/npm/monaco-editor@${MONACO_VERSION}/min/vs`;

/* Give up rather than leaving the page saying "Downloading…" forever. */
const LOAD_TIMEOUT_MS = 60000;

/* Prebuilt by Pyodide. */
const PYODIDE_PACKAGES = [
  "micropip", "lxml", "pydantic", "beautifulsoup4", "html5lib",
  "numpy", "pillow", "more-itertools", "typing-extensions", "pygments",
];

/* Pure-Python dependencies Pyodide does not prebuild. The list covers every
 * published version, not just the current one: `affine`, `typeguard`,
 * `readable-number`, `rfc3987` and `svgpathtools` were requirements of
 * earlier releases, which the version picker can still select. */
const PYPI_PACKAGES = [
  "bidict", "lark", "pydantic-extra-types", "useful-types",
  "rfc3986", "uritools",
  "affine>=3.0,<4", "typeguard", "readable-number", "rfc3987", "svgpathtools",
];

const BOOTSTRAP = `
import sys
import types

import micropip

await micropip.install(${JSON.stringify(PYPI_PACKAGES)})

# svglab imports resvg_py at import time, and there is no wheel of it for
# WebAssembly; the module is created here and filled in afterwards with the
# WebAssembly build of resvg itself
_stub = types.ModuleType("resvg_py")


def _not_wired(*args, **kwargs):
    raise RuntimeError("the renderer is not wired up yet")


_stub.svg_to_bytes = _not_wired
sys.modules["resvg_py"] = _stub

await micropip.install(_svglab_requirement, deps=False)

import svglab

# nothing is imported into the namespace on the user's behalf; importing
# svglab here only installs the patches below and warms the module cache
import __main__

# completions are served straight out of the live namespace
import rlcompleter

__main__._completer = rlcompleter.Completer(__main__.__dict__)


def _complete(prefix):
    matches = []
    state = 0

    while True:
        match = __main__._completer.complete(prefix, state)

        if match is None:
            return matches

        matches.append(match)
        state += 1


__main__._complete = _complete

svglab.__version__
`;

/* Python tracebacks from here start with a few frames inside Pyodide's own
 * code runner, which say nothing about the user's mistake. Those are cut,
 * the placeholder filename the runner uses is given a real name, and the
 * site-packages prefix is trimmed off the library's own frames. */
function cleanTraceback(text) {
  const lines = String(text).split("\n");
  const kept = [];

  let skipping = false;

  for (const line of lines) {
    const frame = /^\s{2}File "([^"]+)", line (\d+)(.*)$/.exec(line);

    if (frame) {
      const [, file, lineNumber, rest] = frame;

      skipping = file.includes("_pyodide") || /^\/lib\/python\d+\.zip/.test(file);

      if (skipping) {
        continue;
      }

      const name = file
        .replace(/^\/lib\/python[\d.]+\/site-packages\//, "")
        .replace(/^<exec>$/, "your code");

      kept.push(`  File "${name}", line ${lineNumber}${rest}`);

      continue;
    }

    // the source excerpt belonging to a frame is indented further
    if (skipping && /^\s{3,}/.test(line)) {
      continue;
    }

    skipping = false;

    // the message itself often quotes a module path too
    kept.push(line.replace(/\/lib\/python[\d.]+\/site-packages\//g, ""));
  }

  return kept.join("\n");
}

/* resvg has no Python wheel for WebAssembly, but the same Rust renderer is
 * published as a WebAssembly module. Loading that gives the real renderer,
 * synchronously, so the library's own rendering code can run unchanged. */
const RESVG_VERSION = "2.6.2";
const RESVG_BASE = `https://cdn.jsdelivr.net/npm/@resvg/resvg-wasm@${RESVG_VERSION}`;

/* initWasm() may only ever be called once per page, so the loader is shared
 * across restarts (switching versions rebuilds the interpreter). */
let resvgLoader = null;

function loadResvg() {
  if (!resvgLoader) {
    resvgLoader = (async () => {
      const module = await import(`${RESVG_BASE}/index.mjs`);

      await module.initWasm(fetch(`${RESVG_BASE}/index_bg.wasm`));

      /* Synchronous, which is the point: Python calls straight into it. */
      return (xml, background) => {
        const options = background ? { background } : {};

        return new module.Resvg(xml, options).render().asPng();
      };
    })().catch((error) => {
      resvgLoader = null;  // let a later attempt retry

      throw error;
    });
  }

  return resvgLoader;
}

/* Puts the WebAssembly renderer where the library expects resvg, and routes
 * around the two places that need a process pool. */
const RENDER_PATCH = `
import base64 as _base64
import concurrent.futures as _futures
import io as _io
import re as _re
import sys as _sys

import numpy as _np
import PIL.Image as _Image
import pygments as _pygments
from pygments.formatters import HtmlFormatter as _HtmlFormatter
from pygments.lexers import XmlLexer as _XmlLexer

try:
    from svglab import graphics as _graphics
except ImportError:  # svglab < 0.5 has no rendering at all
    _graphics = None


def _svg_to_bytes(xml, *, background=None, **kwargs):
    """Stand in for resvg_py.svg_to_bytes, backed by resvg compiled to WebAssembly.

    The font and rendering options the native binding accepts are ignored;
    the WebAssembly build has no access to system fonts.
    """
    return bytes(_js_resvg(xml, background).to_py())


_sys.modules["resvg_py"].svg_to_bytes = _svg_to_bytes


def _run_here(func, *, timeout=None):
    """Replace the process pool: there is no multiprocessing in the browser."""
    return func


if _graphics is not None and hasattr(_graphics, "_run_sandboxed"):
    _graphics._run_sandboxed = _run_here


def _visible_mask(element, *, width=None, height=None):
    """The library renders these two in parallel; here they run in sequence."""
    without = _graphics._render_tree(
        element,
        render_this=False,
        render_other=True,
        make_element_visible=False,
        width=width,
        height=height,
    )
    with_it = _graphics._render_tree(
        element,
        render_this=True,
        render_other=True,
        make_element_visible=False,
        width=width,
        height=height,
    )

    return _np.any(_np.array(without) != _np.array(with_it), axis=2)


if _graphics is not None and hasattr(_graphics, "_render_tree"):
    _graphics.visible_mask = _visible_mask


_MARKUP = _re.compile(r"</?[A-Za-z]")


def _highlight(text):
    """Highlight printed output, using the same token classes as the site.

    Anything without a tag in it returns nothing, so ordinary printed text
    is left alone. Text around the markup, such as a label printed before
    it, is left as plain text by the lexer.
    """
    if not _MARKUP.search(text):
        return None

    return _pygments.highlight(text, _XmlLexer(), _HtmlFormatter(nowrap=True))


def _image_data_url(value):
    """Render a PIL image as a data URL, so the page can display it."""
    if not isinstance(value, _Image.Image):
        return None

    buffer = _io.BytesIO()
    value.save(buffer, format="PNG")

    return "data:image/png;base64," + _base64.b64encode(buffer.getvalue()).decode()


import __main__

# the page itself needs these two
__main__._image_data_url = _image_data_url
__main__._highlight = _highlight
`;

const EXAMPLES = {
  "parse-and-edit": {
    group: "Basics",
    label: "Parse and edit",
    code: `# Import what you need, exactly as you would in a script.

from svglab import Circle, Color, Length, Rect, parse_svg

svg = parse_svg("""
<svg width="100" height="100" xmlns="http://www.w3.org/2000/svg">
    <circle cx="50" cy="50" r="40" stroke="black" stroke-width="2"/>
</svg>
""")

circle = svg.find(Circle)
circle.fill = Color("red")

svg.add_child(
    Rect(x=Length(10), y=Length(10), width=Length(30), height=Length(30))
)

print(svg.to_xml())
`,
  },

  formatter: {
    group: "Basics",
    label: "The formatter",
    code: `# The formatter controls how a document is written down, without
# changing what it draws.

from svglab import Formatter, parse_svg

svg = parse_svg(
    '<svg width="100" height="100">'
    '<path d="M 20 20 L 80 20 L 80 80 Z" fill="#ff0000"/>'
    "</svg>"
)

styles = {
    "default": Formatter(),
    "compact": Formatter(indent=0, color_mode="hex-short",
                         path_data_coordinates="relative"),
    "explicit": Formatter(path_data_commands="explicit",
                          path_data_shorthand_line_commands="never",
                          color_mode="rgb"),
}

for name, formatter in styles.items():
    print(f"--- {name} ---")
    print(svg.to_xml(formatter=formatter))
    print()
`,
  },

  reify: {
    group: "Basics",
    label: "Bake in transforms",
    code: `# Reification applies the transform attribute to the geometry itself,
# so the element looks identical but carries no transform.

from svglab import Length, Rect, Scale, Translate

rect = Rect(
    x=Length(10),
    y=Length(20),
    width=Length(100),
    height=Length(50),
    transform=[Translate(5, 5), Scale(2)],
)

print("before:", rect.to_xml())

rect.reify()

print("after: ", rect.to_xml())
`,
  },

  transforms: {
    group: "Basics",
    label: "Transforms",
    code: `# Transforms compose in the order you would write them in an SVG
# transform attribute: the rightmost one reaches the coordinates first.

from svglab import Point, Rotate, Scale, SkewX, Translate, compose

combined = compose([Translate(10, 20), Scale(2)])

print(combined)
print(combined @ Point(1, 1))
print()

print(Rotate(45, cx=50, cy=50).to_matrix())
print(SkewX(15).to_matrix())
`,
  },

  "shapes-to-paths": {
    group: "Recipes",
    label: "Normalize every shape to a path",
    code: `# Many optimizations are easier once everything is a <path>. Basic
# shapes know how to rewrite themselves, so the whole document can be
# normalized in a few lines.

from svglab import BasicShape, parse_svg

svg = parse_svg("""
<svg width="200" height="100" xmlns="http://www.w3.org/2000/svg">
    <g id="shapes">
        <rect x="10" y="10" width="60" height="40" fill="teal"/>
        <circle cx="120" cy="30" r="20" fill="orange"/>
        <line x1="10" y1="70" x2="190" y2="70" stroke="black"/>
    </g>
</svg>
""")

# materialize first: the tree is modified while walking it
for shape in list(svg.find_all(BasicShape)):
    parent = shape.parent
    index = parent.get_child_index(shape)

    parent.remove_child(shape)
    parent.add_child(shape.to_path(), index=index)

print(svg.to_xml())
`,
  },

  optimize: {
    group: "Recipes",
    label: "Shrink a document",
    code: `# A realistic optimization pass: bake in the transforms, then write the
# result out as compactly as the format allows.

from svglab import Formatter, parse_svg

source = """
<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100">
  <g transform="translate(5, 5)">
    <rect x="10.000000" y="10.000000" width="80.000000" height="80.000000"
          fill="#ff0000" stroke="#000000" stroke-width="1.000000"/>
    <path d="M 20.000000 20.000000 L 80.000000 20.000000
             L 80.000000 80.000000 L 20.000000 80.000000 Z" fill="#0000ff"/>
  </g>
</svg>
"""

svg = parse_svg(source)
svg.reify()

compact = Formatter(
    indent=0,
    general_precision=2,
    color_mode="hex-short",
    path_data_coordinates="relative",
    xmlns="never",
)

result = svg.to_xml(formatter=compact)

print(result)
print()
print(f"{len(source.strip())} B -> {len(result)} B "
      f"({100 - round(100 * len(result) / len(source.strip()))}% smaller)")
`,
  },

  recolor: {
    group: "Recipes",
    label: "Recolor a drawing",
    code: `# Colors are values, not strings: Color("red") == Color("#ff0000"), so a
# palette can be remapped without caring how the file spelled it.

from svglab import Color, Formatter, parse_svg

svg = parse_svg("""
<svg width="100" height="100" xmlns="http://www.w3.org/2000/svg">
    <rect width="40" height="40" fill="red"/>
    <circle cx="70" cy="20" r="18" fill="#FF0000"/>
    <path d="M10,60 H90 V90 H10 Z" fill="rgb(0, 0, 255)" stroke="red"/>
</svg>
""")

palette = {Color("red"): Color("#e91e63"), Color("blue"): Color("#3f51b5")}

for element in svg.find_all():
    for attribute in ("fill", "stroke"):
        value = getattr(element, attribute, None)

        if isinstance(value, Color) and value in palette:
            setattr(element, attribute, palette[value])

print(svg.to_xml(formatter=Formatter(color_mode="hex-long")))
`,
  },

  "build-from-scratch": {
    group: "Recipes",
    label: "Build a document from scratch",
    code: `# Nothing has to be parsed: a document can be assembled entirely out of
# typed objects.

from svglab import (
    Color,
    G,
    Length,
    Path,
    PathData,
    Point,
    RawText,
    Rect,
    Svg,
    Text,
    Translate,
)

svg = Svg(width=Length(240), height=Length(120), viewBox=(0, 0, 240, 120))

badge = G(id="badge", transform=[Translate(20, 20)])

badge.add_child(
    Rect(
        width=Length(200),
        height=Length(80),
        rx=Length(12),
        ry=Length(12),
        fill=Color("#3f51b5"),
    )
)

label = Text(
    x=[Length(100)],
    y=[Length(48)],
    font_size=Length(18),
    fill=Color("white"),
    text_anchor="middle",
)
label.add_child(RawText("svglab"))
badge.add_child(label)

arrow = Path(
    d=PathData()
    .move_to(Point(70, 60))
    .line_to(Point(130, 60))
    .line_to(Point(120, 52))
    .move_to(Point(130, 60))
    .line_to(Point(120, 68)),
    stroke=Color("white"),
    stroke_width=Length(2),
    fill="none",
)
badge.add_child(arrow)

svg.add_child(badge)

print(svg.to_xml())
`,
  },

  inspect: {
    group: "Recipes",
    label: "Walk and inspect a tree",
    code: `# find_all() yields elements in document order; combine it with the
# traits to ask what each element can do.

from svglab import ContainerElement, Shape, parse_svg

svg = parse_svg("""
<svg width="100" height="100" xmlns="http://www.w3.org/2000/svg">
    <defs>
        <linearGradient id="g"><stop offset="0" stop-color="red"/></linearGradient>
    </defs>
    <g transform="rotate(10)">
        <rect width="40" height="40" fill="url(#g)"/>
        <text x="10" y="80">hello</text>
    </g>
</svg>
""")

header = f"{'element':14} {'shape?':7} {'container?':11} attributes"
print(header)
print("-" * len(header))

for element in svg.find_all():
    name = type(element).__name__
    set_attributes = sorted(
        key
        for key, value in element.standard_attrs().items()
        if value is not None
    )

    print(
        f"{name:14} "
        f"{str(isinstance(element, Shape)):7} "
        f"{str(isinstance(element, ContainerElement)):11} "
        f"{', '.join(set_attributes)}"
    )
`,
  },

  render: {
    group: "Recipes",
    label: "Render to pixels",
    code: `# resvg has no Python wheel for WebAssembly, but the same renderer
# does have a WebAssembly build, so this is the real thing -- and the
# ordinary, synchronous API.

from svglab import Circle, parse_svg

svg = parse_svg("""
<svg width="180" height="120" xmlns="http://www.w3.org/2000/svg">
    <rect width="180" height="120" fill="#eceff1"/>
    <circle cx="70" cy="60" r="42" fill="#3f51b5" opacity="0.75"/>
    <circle cx="110" cy="60" r="42" fill="#e91e63" opacity="0.75"/>
</svg>
""")

circle = svg.find(Circle)

print("bounding box:", circle.get_bbox())
print("pixels covered:", int(circle.get_mask().sum()))
print("pixels visible:", int(circle.get_mask(visible_only=True).sum()))

# the last expression is shown as an image
svg.render()
`,
  },

  "web-optimize": {
    group: "From the web",
    label: "Optimize a real icon",
    code: `# Icons published on npm are usually already small, but rarely
# minimal. This fetches one and squeezes it.

from pyodide.http import pyfetch

from svglab import Formatter, Length, parse_svg

URL = "https://cdn.jsdelivr.net/npm/simple-icons@13/icons/python.svg"

response = await pyfetch(URL)
source = await response.string()

svg = parse_svg(source)

# icons published for the web usually carry a viewBox and no size at all
print("width:", svg.width, " height:", svg.height, " viewBox:", svg.viewBox)

_, _, vb_width, vb_height = svg.viewBox
svg.width = Length(vb_width)
svg.height = Length(vb_height)

svg.reify()

compact = Formatter(
    indent=0,
    general_precision=2,
    color_mode="hex-short",
    path_data_coordinates="relative",
    xmlns="never",
)

result = svg.to_xml(formatter=compact)

print(result[:300], "...")
print()
print(f"{len(source)} B -> {len(result)} B "
      f"({100 - round(100 * len(result) / len(source))}% smaller)")

svg.render(width=96)
`,
  },

  "web-sheet": {
    group: "From the web",
    label: "Build an icon sheet",
    code: `# Pull several icons off a CDN, recolor them, and lay them out in a
# single document.

from pyodide.http import pyfetch

from svglab import Color, G, Length, Svg, Translate, parse_svg

ICONS = {
    "python": "#3776ab",
    "rust": "#000000",
    "typescript": "#3178c6",
    "svelte": "#ff3e00",
}

SIZE = 24
GAP = 8

sheet = Svg(
    width=Length(len(ICONS) * SIZE + (len(ICONS) - 1) * GAP),
    height=Length(SIZE),
)

for index, (name, color) in enumerate(ICONS.items()):
    response = await pyfetch(
        f"https://cdn.jsdelivr.net/npm/simple-icons@13/icons/{name}.svg"
    )
    icon = parse_svg(await response.string())

    group = G(
        transform=[Translate(index * (SIZE + GAP), 0)],
        fill=Color(color),
    )

    # an element cannot have two parents, so detach before re-attaching
    for child in list(icon.find_all(recursive=False)):
        icon.remove_child(child)
        group.add_child(child)

    sheet.add_child(group)

print(sheet.to_xml()[:400], "...")

sheet.render(width=len(ICONS) * 64)
`,
  },

  "web-audit": {
    group: "From the web",
    label: "Audit a document from the web",
    code: `# A quick structural report on a document nobody wrote for us.

import collections

from pyodide.http import pyfetch

from svglab import BasicShape, Length, Path, Shape, UnknownElement, parse_svg

URL = "https://cdn.jsdelivr.net/gh/twitter/twemoji@v14.0.2/assets/svg/1f4a1.svg"

response = await pyfetch(URL)
source = await response.string()
svg = parse_svg(source)

# give it a size, since the file only declares a viewBox
_, _, vb_width, vb_height = svg.viewBox
svg.width = Length(vb_width)
svg.height = Length(vb_height)

counts = collections.Counter(type(element).__name__ for element in svg.find_all())

print(f"{len(source)} bytes, {sum(counts.values())} elements")
print()

for name, count in counts.most_common():
    print(f"  {count:3} x {name}")

unknown = list(svg.find_all(UnknownElement))
print()
print(f"unrecognized elements: {len(unknown)}")

shapes = list(svg.find_all(Shape))
convertible = [shape for shape in shapes if isinstance(shape, BasicShape)]
print(f"shapes: {len(shapes)} ({len(convertible)} convertible to paths, "
      f"{len(list(svg.find_all(Path)))} already paths)")

print()
print("bounding boxes:")

for shape in shapes[:5]:
    print(f"  {type(shape).__name__:10} {shape.get_bbox()}")

svg.render(width=128)
`,
  },

  sanitize: {
    group: "Workflows",
    label: "Sanitize an untrusted SVG",
    code: `# SVG is a document format with scripting, so anything uploaded by a
# user has to be cleaned before it is served back. The typed model makes
# that a matter of walking the tree rather than writing regexes.

from svglab import Script, Style, parse_svg

HOSTILE = """
<svg width="100" height="100" xmlns="http://www.w3.org/2000/svg"
     xmlns:xlink="http://www.w3.org/1999/xlink">
    <script>alert(document.cookie)</script>
    <style>@import url(https://evil.example/x.css);</style>
    <rect width="50" height="50" fill="red" onclick="steal()" onload="steal()"/>
    <image href="https://evil.example/tracker.png" width="10" height="10"/>
    <a xlink:href="javascript:steal()"><circle cx="70" cy="70" r="20"/></a>
</svg>
"""

svg = parse_svg(HOSTILE)
removed = []

# 1. drop scripting and styling elements entirely
for element in list(svg.find_all(Script, Style)):
    element.parent.remove_child(element)
    removed.append(type(element).__name__)

# 2. clear every event handler attribute
for element in svg.find_all():
    for name in type(element).model_fields:
        if name.startswith("on") and getattr(element, name, None) is not None:
            setattr(element, name, None)
            removed.append(f"{type(element).__name__}.{name}")

# 3. drop references that point off-site or at javascript:
for element in svg.find_all():
    for name in ("href", "xlink_href"):
        value = getattr(element, name, None)

        if value is None:
            continue

        target = str(value)

        if not target.startswith("#"):
            setattr(element, name, None)
            removed.append(f"{type(element).__name__}.{name} -> {target[:32]}")

print("removed:")

for item in removed:
    print("  -", item)

print()
print(svg.to_xml())
`,
  },

  "trim-to-content": {
    group: "Workflows",
    label: "Crop a drawing to its content",
    code: `# Exported drawings are usually padded with empty space. The rendered
# bounding box says where the ink actually is, and the viewBox can be
# moved to match.

from svglab import Length, Svg, parse_svg

svg = parse_svg("""
<svg width="200" height="200" viewBox="0 0 200 200"
     xmlns="http://www.w3.org/2000/svg">
    <circle cx="150" cy="60" r="18" fill="#3f51b5"/>
    <rect x="120" y="100" width="50" height="30" fill="#e91e63"/>
</svg>
""")

before = svg.get_bbox()
print("ink occupies:", before, "of a 200x200 canvas")

left, top, right, bottom = before
padding = 4

# assigning viewBox changes what is framed; set_viewbox() is the other
# operation, re-framing while keeping the picture looking the same, which
# is why it insists on the aspect ratio staying put
svg.viewBox = (
    left - padding,
    top - padding,
    right - left + 2 * padding,
    bottom - top + 2 * padding,
)
svg.width = Length(right - left + 2 * padding)
svg.height = Length(bottom - top + 2 * padding)

print("new viewBox:  ", svg.viewBox)
print("new size:     ", (svg.width, svg.height))
print()
print(svg.to_xml())

svg.render()
`,
  },

  "dark-mode": {
    group: "Workflows",
    label: "Generate a dark-mode variant",
    code: `# Shipping a dark variant of an asset means walking every paint
# attribute and flipping its lightness, while leaving hues alone.

import colorsys
import copy

from svglab import Color, parse_svg

svg = parse_svg("""
<svg width="160" height="60" xmlns="http://www.w3.org/2000/svg">
    <rect width="160" height="60" fill="#ffffff"/>
    <rect x="10" y="10" width="60" height="40" fill="#1a237e"/>
    <circle cx="120" cy="30" r="20" fill="#e0e0e0" stroke="#212121"/>
</svg>
""")

dark = copy.deepcopy(svg)

for element in dark.find_all():
    for name in ("fill", "stroke", "stop_color"):
        value = getattr(element, name, None)

        if not isinstance(value, Color):
            continue

        red, green, blue = (channel / 255 for channel in value.as_rgb_tuple()[:3])
        hue, lightness, saturation = colorsys.rgb_to_hls(red, green, blue)
        flipped = colorsys.hls_to_rgb(hue, 1 - lightness, saturation)

        setattr(
            element,
            name,
            Color("#" + "".join(f"{round(c * 255):02x}" for c in flipped)),
        )

print("light:", svg.to_xml()[:120])
print("dark: ", dark.to_xml()[:120])

dark.render()
`,
  },

  "preset-comparison": {
    group: "Workflows",
    label: "Compare optimizer settings",
    code: `# Which formatter settings pay off depends on the document, so measure
# rather than guess. Note the baseline: this file was already minified by
# its publisher, so svglab's readable default output is *larger* than what
# it parsed. Optimization is what you turn on, not what you get.

from pyodide.http import pyfetch

from svglab import Formatter, Length, parse_svg

URL = "https://cdn.jsdelivr.net/npm/simple-icons@13/icons/git.svg"

response = await pyfetch(URL)
source = await response.string()

svg = parse_svg(source)
_, _, vb_width, vb_height = svg.viewBox
svg.width = Length(vb_width)
svg.height = Length(vb_height)

presets = {
    "as parsed": Formatter(),
    "no indent": Formatter(indent=0),
    "+ short colors": Formatter(indent=0, color_mode="hex-short"),
    "+ relative paths": Formatter(
        indent=0, color_mode="hex-short", path_data_coordinates="relative"
    ),
    "+ 2 decimals": Formatter(
        indent=0,
        color_mode="hex-short",
        path_data_coordinates="relative",
        general_precision=2,
    ),
    "+ no xmlns": Formatter(
        indent=0,
        color_mode="hex-short",
        path_data_coordinates="relative",
        general_precision=2,
        xmlns="never",
    ),
}

baseline = len(svg.to_xml())

print(f"file as published: {len(source)} B")
print(f"svglab default:    {baseline} B")
print()
print(f"{'setting':18} {'bytes':>7} {'vs default':>11} {'vs published':>13}")
print("-" * 52)

for label, formatter in presets.items():
    size = len(svg.to_xml(formatter=formatter))
    print(
        f"{label:18} {size:7} "
        f"{100 - round(100 * size / baseline):10}% "
        f"{100 - round(100 * size / len(source)):12}%"
    )
`,
  },

  "chart": {
    group: "Workflows",
    label: "Draw a chart from data",
    code: `# Building a document from data is the other half of the library: no
# parsing at all, just constructing typed elements.

from svglab import Color, G, Length, Line, Rect, Svg, Translate

DATA = {"mon": 12, "tue": 19, "wed": 7, "thu": 22, "fri": 16, "sat": 3}

BAR = 28
GAP = 10
HEIGHT = 120
PADDING = 16

width = PADDING * 2 + len(DATA) * BAR + (len(DATA) - 1) * GAP
scale = (HEIGHT - PADDING * 2) / max(DATA.values())

chart = Svg(width=Length(width), height=Length(HEIGHT))
chart.add_child(Rect(width=Length(width), height=Length(HEIGHT), fill=Color("#fafafa")))

bars = G(transform=[Translate(PADDING, HEIGHT - PADDING)])

for index, value in enumerate(DATA.values()):
    bars.add_child(
        Rect(
            x=Length(index * (BAR + GAP)),
            y=Length(-value * scale),
            width=Length(BAR),
            height=Length(value * scale),
            fill=Color("#3f51b5"),
            rx=Length(3),
        )
    )

chart.add_child(bars)
chart.add_child(
    Line(
        x1=Length(PADDING),
        y1=Length(HEIGHT - PADDING),
        x2=Length(width - PADDING),
        y2=Length(HEIGHT - PADDING),
        stroke=Color("#9e9e9e"),
    )
)

print(chart.to_xml()[:200], "...")
print()
print("tallest bar:", max(DATA, key=DATA.get), max(DATA.values()))

chart.render(width=width * 3)
`,
  },

  "path-surgery": {
    group: "Recipes",
    label: "Take a path apart",
    code: `# Path data is a typed sequence of commands, so it can be built,
# transformed and inspected like any other Python object.

from svglab import Length, Path, PathData, Point, Rect, Scale, Translate

d = (
    PathData()
    .move_to(Point(0, 0))
    .line_to(Point(100, 0))
    .quadratic_bezier_to(Point(150, 50), Point(100, 100))
    .close()
)

print("commands:")

for command in d:
    print(" ", command)

print()
print("as written:   ", Path(d=d).to_xml())
print("scaled by 2:  ", Path(d=Scale(2) @ d).to_xml())
print("moved by 10:  ", Path(d=Translate(10, 10) @ d).to_xml())
print()
print("a rect as path:", Rect(width=Length(30), height=Length(20)).to_path().to_xml())
`,
  },
};

const DEFAULT_EXAMPLE = "parse-and-edit";
const DEV_VERSION = "main";
const STORAGE_KEY = "svglab-playground";

function loadScript(url) {
  return new Promise((resolve, reject) => {
    const script = document.createElement("script");
    const timer = window.setTimeout(
      () => reject(new Error(`timed out loading ${url}`)),
      LOAD_TIMEOUT_MS,
    );

    script.src = url;

    script.onload = () => {
      window.clearTimeout(timer);
      resolve();
    };

    script.onerror = () => {
      window.clearTimeout(timer);
      reject(new Error(`could not load ${url}`));
    };

    document.head.appendChild(script);
  });
}

/* Monaco ships as AMD modules and expects its workers to be same-origin, so
 * the worker is bootstrapped through a blob that imports from the CDN. */
async function loadMonaco() {
  await loadScript(`${MONACO_BASE}/loader.js`);

  window.MonacoEnvironment = {
    getWorkerUrl() {
      const proxy = `
        self.MonacoEnvironment = { baseUrl: "${MONACO_BASE}/.." };
        importScripts("${MONACO_BASE}/base/worker/workerMain.js");
      `;

      return URL.createObjectURL(new Blob([proxy], { type: "text/javascript" }));
    },
  };

  window.require.config({ paths: { vs: MONACO_BASE } });

  return new Promise((resolve, reject) => {
    const timer = window.setTimeout(
      () => reject(new Error("timed out starting the editor")),
      LOAD_TIMEOUT_MS,
    );

    window.require(["vs/editor/editor.main"], () => {
      window.clearTimeout(timer);
      resolve(window.monaco);
    });
  });
}

/* Resolve a CSS custom property to the "rrggbb" Monaco wants. The value may
 * be written as a hex, rgb() or hsl(), so it is resolved by the browser
 * rather than parsed here. */
function cssColor(name, fallback) {
  const probe = document.createElement("span");
  probe.style.display = "none";
  probe.style.color = `var(${name}, ${fallback})`;
  document.body.appendChild(probe);

  const resolved = window.getComputedStyle(probe).color;
  probe.remove();

  const parts = /rgba?\((\d+)[,\s]+(\d+)[,\s]+(\d+)/.exec(resolved);

  if (!parts) {
    return fallback.replace("#", "");
  }

  return parts
    .slice(1, 4)
    .map((part) => Number(part).toString(16).padStart(2, "0"))
    .join("");
}

/* A Monaco theme built from the site's own code colors, so the editor and
 * the surrounding documentation highlight code the same way. */
function applyTheme(monaco) {
  const dark = document.body.getAttribute("data-md-color-scheme") === "slate";

  const token = (name, fallback) => cssColor(`--md-code-hl-${name}-color`, fallback);

  monaco.editor.defineTheme("svglab", {
    base: dark ? "vs-dark" : "vs",
    inherit: true,
    rules: [
      { token: "", foreground: cssColor("--md-code-fg-color", "#36464e") },
      { token: "comment", foreground: token("comment", "#75715e"), fontStyle: "italic" },
      { token: "keyword", foreground: token("keyword", "#a625a4") },
      { token: "keyword.flow", foreground: token("keyword", "#a625a4") },
      { token: "string", foreground: token("string", "#0b8235") },
      { token: "string.escape", foreground: token("special", "#0b8235") },
      { token: "number", foreground: token("number", "#e8590c") },
      { token: "operator", foreground: token("operator", "#a625a4") },
      { token: "operators", foreground: token("operator", "#a625a4") },
      { token: "delimiter", foreground: token("punctuation", "#36464e") },
      { token: "identifier", foreground: token("name", "#36464e") },
      { token: "type", foreground: token("constant", "#0c76c4") },
      { token: "tag", foreground: token("keyword", "#a625a4") },
      { token: "attribute.name", foreground: token("variable", "#e8590c") },
      { token: "attribute.value", foreground: token("string", "#0b8235") },
    ],
    colors: {
      "editor.background": `#${cssColor("--md-code-bg-color", "#f5f5f5")}`,
      "editor.foreground": `#${cssColor("--md-code-fg-color", "#36464e")}`,
      "editorLineNumber.foreground": `#${cssColor("--md-default-fg-color--lighter", "#b3b3b3")}`,
      "editorLineNumber.activeForeground": `#${cssColor("--md-default-fg-color--light", "#666666")}`,
      "editorCursor.foreground": `#${cssColor("--md-primary-fg-color", "#3f51b5")}`,
      "editorIndentGuide.background1": `#${cssColor("--md-default-fg-color--lightest", "#eeeeee")}`,
      "editorWidget.background": `#${cssColor("--md-default-bg-color", "#ffffff")}`,
      "editorWidget.border": `#${cssColor("--md-default-fg-color--lightest", "#eeeeee")}`,
      "editorSuggestWidget.background": `#${cssColor("--md-default-bg-color", "#ffffff")}`,
      "editorSuggestWidget.selectedBackground": `#${cssColor("--md-default-fg-color--lightest", "#eeeeee")}`,
    },
  });

  monaco.editor.setTheme("svglab");
}

/* The development build is published next to the documentation; releases
 * come from PyPI. */
async function resolveRequirement(version) {
  if (version !== DEV_VERSION) {
    return `svglab==${version}`;
  }

  const index = new URL("../wheels/index.json", window.location.href);
  const response = await fetch(index);

  if (!response.ok) {
    return "svglab";  // no wheel was published; fall back to the latest release
  }

  const { wheel } = await response.json();

  return new URL(`../wheels/${wheel}`, window.location.href).href;
}

async function releaseVersions() {
  try {
    const response = await fetch("https://pypi.org/pypi/svglab/json");
    const data = await response.json();

    return Object.keys(data.releases)
      .filter((version) => !/[a-z]/i.test(version))
      .sort((a, b) =>
        b.localeCompare(a, undefined, { numeric: true, sensitivity: "base" }),
      );
  } catch (error) {
    return [];
  }
}

function initPlayground() {
  const root = document.getElementById("svglab-playground");

  if (!root || root.dataset.ready === "1") {
    return;
  }

  root.dataset.ready = "1";

  const host = root.querySelector("[data-playground-monaco]");
  const fallback = root.querySelector("[data-playground-editor]");
  const output = root.querySelector("[data-playground-output]");
  const runButton = root.querySelector("[data-playground-run]");
  const resetButton = root.querySelector("[data-playground-reset]");
  const picker = root.querySelector("[data-playground-picker]");
  const versions = root.querySelector("[data-playground-versions]");
  const status = root.querySelector("[data-playground-status]");
  const bar = root.querySelector("[data-playground-bar]");
  const progress = root.querySelector("[data-playground-progress]");

  const required = {
    host, fallback, output, runButton, resetButton, picker, versions, status,
    bar, progress,
  };

  for (const [name, node] of Object.entries(required)) {
    if (!node) {
      console.error(`svglab playground: missing element for "${name}"`);
      return;
    }
  }

  const pendingHighlights = [];

  let pyodide = null;
  let booting = null;
  let bootedVersion = null;
  let editor = null;
  let current = DEFAULT_EXAMPLE;
  let running = false;

  /* The editor is Monaco when it loads and a plain textarea when it does
   * not, so everything else talks to it through these two. */
  function getCode() {
    return editor ? editor.getValue() : fallback.value;
  }

  function setCode(code) {
    if (editor) {
      editor.setValue(code);
    } else {
      fallback.value = code;
    }
  }

  function setProgress(percent, label) {
    progress.hidden = false;
    bar.style.width = `${percent}%`;
    progress.setAttribute("aria-valuenow", String(Math.round(percent)));
    status.textContent = label;
  }

  function write(text, kind) {
    if (text === undefined || text === null || text === "") {
      return;
    }

    const line = document.createElement("span");
    line.className = `playground__line playground__line--${kind || "out"}`;
    line.textContent = text.endsWith("\n") ? text : `${text}\n`;

    if (kind !== "err") {
      pendingHighlights.push(line);
    }

    output.appendChild(line);
    output.scrollTop = output.scrollHeight;
  }

  /* Highlighting calls back into Python, which must not happen while Python
   * is running: stdout is written from inside the interpreter, and calling
   * in from that callback fails the write with an I/O error. So output is
   * shown as plain text first and colored once the run is over. */
  function highlightOutput() {
    const lines = pendingHighlights.splice(0);

    if (!pyodide || lines.length === 0) {
      return;
    }

    const highlighter = pyodide.globals.get("_highlight");

    if (!highlighter) {
      return;
    }

    try {
      for (const line of lines) {
        try {
          const html = highlighter(line.textContent);

          if (html) {
            line.classList.add("highlight");
            line.innerHTML = html;
          }
        } catch (error) {
          // leave this line as plain text
        }
      }
    } finally {
      highlighter.destroy?.();
    }
  }

  function load(name) {
    current = name;
    setCode(EXAMPLES[name].code);
    output.replaceChildren();
    saveState();
  }

  /* Keep whatever was being worked on across reloads. Storage may be
   * unavailable (private windows, blocked cookies), which is not worth
   * failing over. */
  function saveState() {
    try {
      window.localStorage.setItem(
        STORAGE_KEY,
        JSON.stringify({
          example: current,
          version: versions.value,
          code: getCode(),
        }),
      );
    } catch (error) {
      // not important enough to report
    }
  }

  function savedState() {
    try {
      return JSON.parse(window.localStorage.getItem(STORAGE_KEY) || "null");
    } catch (error) {
      return null;
    }
  }

  async function run() {
    if (running) {
      return;
    }

    running = true;
    runButton.disabled = true;
    runButton.dataset.state = "running";
    output.replaceChildren();
    pendingHighlights.length = 0;

    try {
      await ensureReady();

      const result = await pyodide.runPythonAsync(getCode());

      if (result !== undefined && result !== null) {
        const toDataUrl = pyodide.globals.get("_image_data_url");
        const url = toDataUrl ? toDataUrl(result) : null;

        if (url) {
          const image = document.createElement("img");
          image.src = url;
          image.className = "playground__image";
          image.alt = "Rendered result";
          output.appendChild(image);
        } else {
          write(result.toString(), "out");
        }

        toDataUrl?.destroy?.();
        result.destroy?.();
      }
    } catch (error) {
      write(cleanTraceback(error.message).trimEnd(), "err");
    } finally {
      highlightOutput();

      running = false;
      runButton.disabled = false;
      delete runButton.dataset.state;
    }
  }

  /* Completions come from the live interpreter namespace, so they know
   * about objects the code just created, not only about svglab itself. */
  function complete(prefix) {
    if (!pyodide) {
      return [];
    }

    try {
      const proxy = pyodide.globals.get("_complete")(prefix);
      const matches = proxy.toJs();
      proxy.destroy?.();

      return matches;
    } catch (error) {
      return [];
    }
  }

  function registerCompletions(monaco) {
    monaco.languages.registerCompletionItemProvider("python", {
      triggerCharacters: ["."],

      provideCompletionItems(model, position) {
        const line = model.getValueInRange({
          startLineNumber: position.lineNumber,
          startColumn: 1,
          endLineNumber: position.lineNumber,
          endColumn: position.column,
        });

        const prefix = /[\w.]*$/.exec(line)[0];
        const word = model.getWordUntilPosition(position);
        const dot = prefix.lastIndexOf(".");

        const range = {
          startLineNumber: position.lineNumber,
          endLineNumber: position.lineNumber,
          startColumn: dot === -1 ? word.startColumn : position.column - (prefix.length - dot - 1),
          endColumn: position.column,
        };

        const suggestions = complete(prefix).map((match) => {
          const callable = match.endsWith("(");
          const text = callable ? match.slice(0, -1) : match;
          const label = dot === -1 ? text : text.slice(text.lastIndexOf(".") + 1);

          return {
            label,
            insertText: label,
            range,
            kind: callable
              ? monaco.languages.CompletionItemKind.Function
              : monaco.languages.CompletionItemKind.Variable,
          };
        });

        return { suggestions };
      },
    });
  }

  async function startEditor() {
    try {
      const monaco = await loadMonaco();

      applyTheme(monaco);

      editor = monaco.editor.create(host, {
        // whatever the textarea holds: the example, or restored work
        value: fallback.value,
        language: "python",
        theme: "svglab",
        automaticLayout: true,
        minimap: { enabled: false },
        scrollBeyondLastLine: false,
        fontSize: 13,
        fontFamily: getComputedStyle(document.body)
          .getPropertyValue("--md-code-font-family") || "monospace",
        tabSize: 4,
        insertSpaces: true,
        renderWhitespace: "selection",
        padding: { top: 12, bottom: 12 },
        scrollbar: { alwaysConsumeMouseWheel: false },
      });

      editor.addCommand(
        window.monaco.KeyMod.CtrlCmd | window.monaco.KeyCode.Enter,
        run,
      );

      editor.onDidChangeModelContent(scheduleSave);

      registerCompletions(monaco);

      fallback.hidden = true;
      host.hidden = false;

      // follow the site's light/dark toggle
      new MutationObserver(() => {
        applyTheme(monaco);
      }).observe(document.body, {
        attributes: true,
        attributeFilter: ["data-md-color-scheme"],
      });
    } catch (error) {
      // the textarea stays, so the playground still works
      console.error(`svglab playground: ${error.message}; using a plain editor`);
      host.hidden = true;
      fallback.hidden = false;
    }
  }

  fallback.addEventListener("keydown", (event) => {
    if (event.key === "Tab") {
      event.preventDefault();
      const { selectionStart: start, selectionEnd: end, value } = fallback;
      fallback.value = `${value.slice(0, start)}    ${value.slice(end)}`;
      fallback.selectionStart = start + 4;
      fallback.selectionEnd = start + 4;
    } else if (event.key === "Enter" && (event.ctrlKey || event.metaKey)) {
      event.preventDefault();
      run();
    }
  });

  runButton.addEventListener("click", run);
  resetButton.addEventListener("click", () => load(current));

  // save edits, but not on every keystroke
  let saveTimer = null;

  function scheduleSave() {
    window.clearTimeout(saveTimer);
    saveTimer = window.setTimeout(saveState, 400);
  }

  fallback.addEventListener("input", scheduleSave);

  const groups = new Map();

  for (const [name, example] of Object.entries(EXAMPLES)) {
    if (!groups.has(example.group)) {
      const optgroup = document.createElement("optgroup");
      optgroup.label = example.group;
      picker.appendChild(optgroup);
      groups.set(example.group, optgroup);
    }

    const option = document.createElement("option");
    option.value = name;
    option.textContent = example.label;
    groups.get(example.group).appendChild(option);
  }

  picker.addEventListener("change", () => load(picker.value));
  // pick up where the last visit left off
  const restored = savedState();

  if (restored && EXAMPLES[restored.example]) {
    current = restored.example;
    picker.value = restored.example;

    if (restored.version) {
      const known = [...versions.options].some(
        (option) => option.value === restored.version,
      );

      if (known) {
        versions.value = restored.version;
      } else {
        // releases are added asynchronously; apply it once they arrive
        versions.dataset.pending = restored.version;
      }
    }
  }

  // switching versions means a different svglab, so the interpreter is
  // thrown away and rebuilt on the next run
  versions.addEventListener("change", () => {
    saveState();

    if (versions.value === bootedVersion) {
      return;  // already running this one; nothing to rebuild
    }

    pyodide = null;
    booting = null;
    bootedVersion = null;
    pendingHighlights.length = 0;
    output.replaceChildren();
    delete status.dataset.state;
    status.textContent = `svglab ${versions.value} starts on next run`;
  });

  releaseVersions().then((published) => {
    for (const version of published) {
      const option = document.createElement("option");
      option.value = version;
      option.textContent = version;
      versions.appendChild(option);
    }

    if (versions.dataset.pending) {
      versions.value = versions.dataset.pending;
      delete versions.dataset.pending;
    }
  });

  /* The runtime is several megabytes, so it is only fetched once someone
   * actually runs something. */
  function ensureReady() {
    if (!booting) {
      booting = boot().catch((error) => {
        booting = null;  // let the next run try again
        throw error;
      });
    }

    return booting;
  }

  async function boot() {
    if (typeof WebAssembly === "undefined") {
      status.textContent = "This browser has no WebAssembly support.";
      status.dataset.state = "error";
      progress.hidden = true;

      throw new Error("this browser has no WebAssembly support");
    }

    try {
      setProgress(5, "Downloading Python…");
      await loadScript(`${INDEX_URL}pyodide.js`);

      setProgress(15, "Starting the interpreter…");
      pyodide = await window.loadPyodide({ indexURL: INDEX_URL });

      setProgress(45, "Loading packages…");
      await pyodide.loadPackage(PYODIDE_PACKAGES, {
        messageCallback: (message) => {
          const match = /Loading (.+)/.exec(message);

          if (match) {
            status.textContent = `Loading ${match[1].split(",")[0]}…`;
          }
        },
      });

      setProgress(70, `Installing svglab ${versions.value}…`);
      const requirement = await resolveRequirement(versions.value);

      setProgress(75, `Installing svglab ${versions.value}…`);

      // the setup code runs in its own namespace, so the user's namespace
      // starts empty and they write their own imports
      const setup = pyodide.toPy({});
      setup.set("__name__", "svglab_playground_setup");
      setup.set("_svglab_requirement", requirement);

      let version;

      try {
        version = await pyodide.runPythonAsync(BOOTSTRAP, { globals: setup });
      } finally {
        setup.destroy();
      }

      setProgress(88, "Loading the renderer…");
      const resvgRender = await loadResvg();

      setProgress(95, "Wiring up rendering…");

      // run the patch in its own namespace; without this every name it
      // defines would land in the namespace the user's code runs in
      const runtime = pyodide.toPy({});
      runtime.set("__name__", "svglab_playground_runtime");
      runtime.set("_js_resvg", resvgRender);

      try {
        await pyodide.runPythonAsync(RENDER_PATCH, { globals: runtime });
      } finally {
        runtime.destroy();
      }

      pyodide.setStdout({ batched: (text) => write(text, "out") });
      pyodide.setStderr({ batched: (text) => write(text, "err") });

      bootedVersion = versions.value;

      setProgress(100, `svglab ${version}`);
      status.dataset.state = "ready";

      window.setTimeout(() => {
        progress.hidden = true;
      }, 600);
    } catch (error) {
      progress.hidden = true;
      status.textContent = `Failed to start: ${error.message}`;
      status.dataset.state = "error";

      throw error;
    }
  }

  load(current);

  if (restored && typeof restored.code === "string" && restored.code.trim()) {
    setCode(restored.code);
  }

  startEditor();
}

if (typeof document$ !== "undefined") {
  document$.subscribe(initPlayground);
} else {
  document.addEventListener("DOMContentLoaded", initPlayground);
}
