/* An svglab playground: the VS Code editor (Monaco) in front of CPython in
 * the browser (Pyodide). The Python half lives in playground/bootstrap.py,
 * the examples in playground/examples/. */

const PYODIDE = "https://cdn.jsdelivr.net/pyodide/v314.0.7/full/";
const MONACO = "https://cdn.jsdelivr.net/npm/monaco-editor@0.52.2/min/vs";
const RESVG = "https://cdn.jsdelivr.net/npm/@resvg/resvg-wasm@2.6.2";

const EXAMPLES = {
  "parse-and-edit": "Parse and edit",
  optimize: "Shrink a document",
  "path-surgery": "Take a path apart",
  chart: "Draw a chart from data",
  render: "Render to pixels",
  sanitize: "Sanitize an untrusted SVG",
};

/* Instant navigation swaps the page without reloading this script, so the
 * interpreter and the editor library outlive the page that started them. */
let python = null;
let booting = null;
let monacoLoader = null;
let resvgLoader = null;
let emit = () => {};

function loadScript(url) {
  return new Promise((resolve, reject) => {
    const script = document.createElement("script");
    script.src = url;
    script.onload = resolve;
    script.onerror = () => reject(new Error(`could not load ${url}`));
    document.head.append(script);
  });
}

async function fetchText(url) {
  const response = await fetch(url);

  if (!response.ok) {
    throw new Error(`could not load ${url}`);
  }

  return response.text();
}

/* resvg compiled to WebAssembly, standing in for the library's compiled
 * renderer. initWasm() may only be called once per page. */
function loadResvg() {
  resvgLoader ??= (async () => {
    const resvg = await import(`${RESVG}/index.mjs`);
    await resvg.initWasm(fetch(`${RESVG}/index_bg.wasm`));

    return (svg, background, zoom) => new resvg.Resvg(svg, {
      background,
      fitTo: { mode: "zoom", value: zoom },
    }).render().asPng();
  })();

  return resvgLoader;
}

/* The runtime is around 15 MB, so it is fetched on the first run. */
function startPython(base, setStatus) {
  booting ??= (async () => {
    setStatus("Downloading Python…");
    await loadScript(`${PYODIDE}pyodide.js`);
    const pyodide = await window.loadPyodide({
      indexURL: PYODIDE,
      packages: ["micropip"],
    });

    setStatus("Installing svglab…");
    const { wheel } = JSON.parse(await fetchText(new URL("wheel.json", base)));
    await pyodide.pyimport("micropip").install(new URL(wheel, base).href);

    // only now, so that what the installer prints stays in the console
    pyodide.setStdout({ batched: (text) => emit(text, "out") });
    pyodide.setStderr({ batched: (text) => emit(text, "err") });

    setStatus("Starting svglab…");
    const namespace = pyodide.toPy({ __name__: "playground" });
    pyodide.runPython(await fetchText(new URL("bootstrap.py", base)), {
      globals: namespace,
    });
    namespace.get("setup")(await loadResvg());
    pyodide.pyimport("svglab");

    python = { run: namespace.get("run"), complete: namespace.get("complete") };
  })().catch((error) => {
    booting = null;  // let the next run try again

    throw error;
  });

  return booting;
}

/* Completions come from the live namespace, so they know about the objects
 * the code has created, not only about the library. */
function provideCompletionItems(model, position) {
  if (!python) {
    return { suggestions: [] };
  }

  const line = model.getLineContent(position.lineNumber);
  const prefix = /[\w.]*$/.exec(line.slice(0, position.column - 1))[0];
  const range = {
    startLineNumber: position.lineNumber,
    endLineNumber: position.lineNumber,
    startColumn: model.getWordUntilPosition(position).startColumn,
    endColumn: position.column,
  };
  const kinds = window.monaco.languages.CompletionItemKind;

  const matches = python.complete(prefix);
  const suggestions = matches.toJs().map((match) => {
    // callables come as `name(`, or as `name()` when they take no arguments
    const callable = /\(\)?$/.test(match);
    const label = match.slice(match.lastIndexOf(".") + 1).replace(/\(\)?$/, "");

    return {
      label,
      insertText: label,
      range,
      kind: callable ? kinds.Function : kinds.Variable,
    };
  });
  matches.destroy();

  return { suggestions };
}

function theme() {
  return document.body.dataset.mdColorScheme === "slate" ? "vs-dark" : "vs";
}

/* Monaco ships as AMD modules and wants its worker same-origin, so the
 * worker is bootstrapped through a blob that imports from the CDN. */
function loadMonaco() {
  monacoLoader ??= (async () => {
    await loadScript(`${MONACO}/loader.js`);

    window.MonacoEnvironment = {
      getWorkerUrl: () => URL.createObjectURL(new Blob([`
        self.MonacoEnvironment = { baseUrl: "${MONACO}/.." };
        importScripts("${MONACO}/base/worker/workerMain.js");
      `], { type: "text/javascript" })),
    };
    window.require.config({ paths: { vs: MONACO } });

    const monaco = await new Promise((resolve, reject) => {
      window.require(["vs/editor/editor.main"], () => resolve(window.monaco), reject);
    });

    monaco.languages.registerCompletionItemProvider("python", {
      triggerCharacters: ["."],
      provideCompletionItems,
    });

    // follow the site's light/dark toggle
    new MutationObserver(() => monaco.editor.setTheme(theme())).observe(
      document.body,
      { attributeFilter: ["data-md-color-scheme"] },
    );

    return monaco;
  })();

  return monacoLoader;
}

function initPlayground() {
  const root = document.getElementById("svglab-playground");

  if (!root) {
    return;
  }

  const [status, picker, reset, runButton, host, output] = [
    "status", "picker", "reset", "run", "editor", "output",
  ].map((name) => root.querySelector(`[data-playground-${name}]`));

  // everything the playground fetches sits next to the page
  const base = new URL(".", window.location.href);

  let editor = null;

  function setStatus(text, state = "") {
    status.textContent = text;
    status.dataset.state = state;
  }

  function write(text, kind) {
    const line = document.createElement("span");
    line.className = `playground__line playground__line--${kind}`;
    line.textContent = `${text}\n`;
    output.append(line);
    output.scrollTop = output.scrollHeight;
  }

  emit = write;

  async function load(name) {
    output.replaceChildren();
    editor.setValue(await fetchText(new URL(`examples/${name}.py`, base)));
  }

  async function run() {
    if (!editor || runButton.disabled) {
      return;
    }

    runButton.disabled = true;
    output.replaceChildren();

    try {
      await startPython(base, setStatus);
      setStatus("Ready", "ready");

      const image = await python.run(editor.getValue());

      if (image) {
        const img = document.createElement("img");
        img.className = "playground__image";
        img.alt = "Rendered result";
        img.src = image;
        output.append(img);
      }
    } catch (error) {
      setStatus("Error", "error");
      write(error.message, "err");
    } finally {
      runButton.disabled = false;
    }
  }

  for (const [name, label] of Object.entries(EXAMPLES)) {
    picker.add(new Option(label, name));
  }

  picker.addEventListener("change", () => load(picker.value));
  reset.addEventListener("click", () => load(picker.value));
  runButton.addEventListener("click", run);

  loadMonaco().then((monaco) => {
    // editors of pages that instant navigation has since replaced
    for (const stale of monaco.editor.getEditors()) {
      if (!stale.getContainerDomNode().isConnected) {
        stale.dispose();
      }
    }

    editor = monaco.editor.create(host, {
      language: "python",
      theme: theme(),
      automaticLayout: true,
      minimap: { enabled: false },
      scrollBeyondLastLine: false,
      fontSize: 13,
      tabSize: 4,
      padding: { top: 12, bottom: 12 },
      scrollbar: { alwaysConsumeMouseWheel: false },
    });
    editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.Enter, run);

    return load(picker.value);
  }).catch((error) => setStatus(`Could not load: ${error.message}`, "error"));
}

if (typeof document$ !== "undefined") {
  document$.subscribe(initPlayground);
} else {
  document.addEventListener("DOMContentLoaded", initPlayground);
}
