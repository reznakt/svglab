---
hide:
  - navigation
  - toc
---

# Playground

Try <span class="svglab">svglab</span> without installing anything. The editor below runs real CPython in your browser through [Pyodide](https://pyodide.org/), with <span class="svglab">svglab</span> built from the same commit as these pages, so what the documentation describes is what you get.

Edit the code, press **Run** (or ++ctrl+enter++), and the output appears on the right. Nothing is imported for you &mdash; write the same `from svglab import ...` you would write locally. The editor is [Monaco](https://microsoft.github.io/monaco-editor/), the one from VS Code. Completions, parameter hints and the docs shown when you hover a name come from [Jedi](https://jedi.readthedocs.io/), which reads your code and the running interpreter, so after a run they also know about the objects your code created. A run that raises underlines where. **Share** puts your code into a link.

The right pane is also a Python console, live as soon as Python has loaded, with ++tab++ to complete names. After a run it works on whatever your code left behind, like `python -i` after a script, so you can inspect and poke at the objects it created. Every run restarts Python from an empty namespace and marks the restart in the transcript; **Reset** and switching examples start over completely, with the example as written. While code runs, **Run** turns into **Stop**, which restarts Python. Drag the divider between the panes to resize them.

<!-- Markdown reads this, for the icons in the buttons, so nothing in it is
indented: an indented line would be a code block. -->
<div id="svglab-playground" class="playground" markdown>
<div class="playground__bar" markdown>
<span class="playground__status" data-playground-status data-state="busy" role="status">Loading…</span>
<span class="playground__clock" data-playground-clock aria-hidden="true"></span>
<span class="playground__spacer"></span>
<select class="playground__picker" data-playground-picker aria-label="Example"></select>
<button type="button" class="md-button playground__button" data-playground-share data-icon="share"><span data-icon-for="share">:material-share-variant:</span><span data-icon-for="done">:material-check:</span><span data-playground-label>Share</span></button>
<button type="button" class="md-button playground__button" data-playground-clear><span data-icon-for="clear">:material-notification-clear-all:</span><span>Clear console</span></button>
<button type="button" class="md-button playground__button" data-playground-reset><span data-icon-for="reset">:material-restore:</span><span>Reset</span></button>
<button type="button" class="md-button md-button--primary playground__button" data-playground-run data-icon="run"><span data-icon-for="run">:material-play:</span><span data-icon-for="stop">:material-stop:</span><span data-playground-label>Run</span></button>
<span class="playground__progress" data-playground-progress aria-hidden="true"><span></span></span>
</div>
<div class="playground__panes">
<div class="playground__editor" data-playground-editor></div>
<div class="playground__splitter" data-playground-splitter role="separator"
aria-orientation="vertical" aria-label="Resize the editor"
aria-valuemin="20" aria-valuemax="80" aria-valuenow="67" tabindex="0"></div>
<div class="playground__output" data-playground-output>
<div data-playground-log></div>
<label class="playground__prompt">
<span data-playground-prompt>&gt;&gt;&gt;</span>
<input class="playground__input" data-playground-input spellcheck="false"
autocomplete="off" autocapitalize="off" aria-label="Python console"
placeholder="Waiting for Python…" disabled>
</label>
</div>
</div>
</div>

!!! svglab "Rendering uses resvg compiled to WebAssembly"
    `render()`, `get_bbox()` and `get_mask()` work here, synchronously and
    through the library's own code. The library's renderer is a compiled
    extension with no WebAssembly build, so
    [`@resvg/resvg-wasm`](https://github.com/thx/resvg-js) takes its place.
    That is an older release of resvg than the one the library bundles, it
    has a single font, Inter, that every font family falls back to, and it
    ignores every render option except the background and the zoom. Edge cases can therefore
    render differently than they do locally.

    An image on the last line of your code, or entered in the console, is
    displayed in the output.

Python and <span class="svglab">svglab</span> load in the background as soon as the page opens: around 15 MB on the first visit, and from the browser's cache after that, so that later visits only wait for Python to start up and import the library.
