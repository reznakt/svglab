---
hide:
  - toc
---

# Playground

Try <span class="svglab">svglab</span> without installing anything. The editor below runs real CPython in your browser through [Pyodide](https://pyodide.org/), with <span class="svglab">svglab</span> installed from PyPI &mdash; the same wheel you would get from `pip install svglab`.

Edit the code, press **Run** (or ++ctrl+enter++), and the output appears on the right. The editor is [Monaco](https://microsoft.github.io/monaco-editor/) &mdash; the one from VS Code &mdash; so you get syntax highlighting and completions. Completions come from the running interpreter, so they know about the objects your code just created, not only about the library.

Nothing is imported for you &mdash; write the same `from svglab import ...` you would write locally, so what you try here transfers unchanged. Press ++ctrl+space++ to ask for completions explicitly.

By default it runs **`main`**, built from the same commit as these pages, so what the documentation describes is what you get. The second dropdown switches to any published release instead; changing it restarts the interpreter on the next run.

Every release back to 0.1.0 loads, but only the recent ones behave like the documentation: rendering arrived in a usable form in 0.13.0, and the examples here are written against `main`.

!!! tip "Completions know what you have run"
    They are served by the live interpreter, so they cover the objects your code created, not just the library. Run the code once and `circle.` will complete against that actual `Circle`.

<div id="svglab-playground" class="playground">
  <div class="playground__bar">
    <span class="playground__status" data-playground-status>Python starts on first run</span>

    <span class="playground__progress" data-playground-progress hidden
          role="progressbar" aria-valuemin="0" aria-valuemax="100"
          aria-valuenow="0" aria-label="Loading Python">
      <span class="playground__progress-bar" data-playground-bar></span>
    </span>

    <span class="playground__spacer"></span>

    <select class="playground__picker" data-playground-picker
            aria-label="Example"></select>

    <select class="playground__picker" data-playground-versions
            aria-label="svglab version">
      <option value="main" selected>main (development)</option>
    </select>

    <button type="button" class="md-button playground__reset"
            data-playground-reset>Reset</button>

    <button type="button" class="md-button md-button--primary playground__run"
            data-playground-run>Run</button>
  </div>

  <div class="playground__panes">
    <div class="playground__editor-pane">
      <div class="playground__monaco" data-playground-monaco hidden></div>
      <textarea class="playground__editor" data-playground-editor
                spellcheck="false" autocomplete="off" autocapitalize="off"
                autocorrect="off" wrap="off" aria-label="Python code"></textarea>
    </div>

    <div class="playground__output" data-playground-output></div>
  </div>
</div>

!!! svglab "Rendering is the real resvg"
    `render()`, `get_bbox()` and `get_mask()` work here exactly as they do
    locally, synchronously and through the library's own code. The
    `resvg-py` wheel cannot be installed &mdash; it is a compiled extension
    with no WebAssembly build &mdash; but resvg itself is Rust, and
    [`@resvg/resvg-wasm`](https://github.com/thx/resvg-js) is the same
    renderer compiled to WebAssembly. That is dropped in underneath, so
    pixels here match pixels locally.

    If the last expression of your code is an image, it is displayed below
    the output.

    Two things do differ. Text does not render, because the WebAssembly
    build has no access to system fonts, and the renderer runs in this tab
    rather than in a separate process as it does locally.

The examples under **From the web** fetch real files off a CDN, so they need a network connection.

Python is not downloaded until you press **Run** for the first time &mdash; reading the page costs nothing. That first run fetches a few megabytes of runtime and packages, tracked by the progress bar; later runs are instant, and interpreter state persists between them, so you can build on what the previous run left behind.

Everything downloaded is served with year-long immutable cache headers, so the second visit starts from the browser cache rather than the network. Your code, the selected example and the selected version are kept in local storage and restored when you come back; **Reset** puts the original example back.

Completions are served by that interpreter, so they only become available after the first run.
