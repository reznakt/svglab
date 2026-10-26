---
hide:
  - toc
---

# Playground

Try <span class="svglab">svglab</span> without installing anything. The editor below runs real CPython in your browser through [Pyodide](https://pyodide.org/), with <span class="svglab">svglab</span> built from the same commit as these pages, so what the documentation describes is what you get.

Edit the code, press **Run** (or ++ctrl+enter++), and the output appears on the right. Nothing is imported for you &mdash; write the same `from svglab import ...` you would write locally. The editor is [Monaco](https://microsoft.github.io/monaco-editor/), the one from VS Code. Its completions come from the running interpreter, so after a run they know about the objects your code created; press ++ctrl+space++ to ask for them.

<div id="svglab-playground" class="playground">
  <div class="playground__bar">
    <span class="playground__status" data-playground-status>Python starts on first run</span>
    <span class="playground__spacer"></span>
    <select class="playground__picker" data-playground-picker aria-label="Example"></select>
    <button type="button" class="md-button playground__button" data-playground-reset>Reset</button>
    <button type="button" class="md-button md-button--primary playground__button" data-playground-run>Run</button>
  </div>

  <div class="playground__panes">
    <div class="playground__editor" data-playground-editor></div>
    <div class="playground__output" data-playground-output></div>
  </div>
</div>

!!! svglab "Rendering uses resvg compiled to WebAssembly"
    `render()`, `get_bbox()` and `get_mask()` work here, synchronously and
    through the library's own code. The library's renderer is a compiled
    extension with no WebAssembly build, so
    [`@resvg/resvg-wasm`](https://github.com/thx/resvg-js) takes its place.
    That is an older release of resvg than the one the library bundles, it
    has no fonts, so text does not render, and it ignores every render
    option except the background and the zoom. Edge cases can therefore
    render differently than they do locally.

    If the last line of your code evaluates to an image, it is displayed
    below the output.

Python is not downloaded until you press **Run** for the first time. That first run fetches the runtime and the packages, around 15 MB; later runs are instant, and the interpreter's state persists between them, so you can build on what the previous run left behind.
