/* The playground's Python, in a worker so that loading and running it never
 * freezes the page: Pyodide, svglab and the session from bootstrap.py. The
 * page sends requests ({id, method, args}) and gets replies ({id, result} or
 * {id, error}); in between come status updates, output and images. */

import { loadPyodide } from "https://cdn.jsdelivr.net/pyodide/v314.0.7/full/pyodide.mjs";

const PYODIDE = "https://cdn.jsdelivr.net/pyodide/v314.0.7/full/";
const RESVG = "https://cdn.jsdelivr.net/npm/@resvg/resvg-wasm@2.6.2";

// the documentation's own font, Inter; every font family falls back to it
const FONT = "https://fonts.gstatic.com/s/inter/v20/UcCO3FwrK3iLTeHuS_nVMrMxCp50SjIw2boKoduKmMEVuLyfMZg.ttf";
const FAMILY = "Inter";

// what micropip resolved on an earlier visit, for one build of svglab
const LOCKS = "svglab-playground-locks";

// the methods that need Jedi, which loads after the rest
const HELP = new Set(["complete", "signatures", "describe"]);

const post = (message) => self.postMessage(message);

// how far along the startup is, for the page's progress bar
let reached = 0;

/* Reports a step of the startup: the share of the startup done by its end,
 * and about how long it takes, as measured on a recent laptop. */
function step(status, until, seconds) {
  post({ status, progress: [reached, until], seconds });
  reached = until;
}

async function fetchText(name) {
  const url = new URL(name, import.meta.url);
  const response = await fetch(url);

  if (!response.ok) {
    throw new Error(`could not load ${url}`);
  }

  return response.text();
}

/* resvg compiled to WebAssembly, standing in for the library's compiled
 * renderer; Python calls it synchronously. It has no system fonts to find, so
 * it gets one, without which only text goes missing. */
async function loadResvg() {
  const [resvg, font] = await Promise.all([
    import(`${RESVG}/index.mjs`),
    fetch(FONT)
      .then((response) => (response.ok ? response.arrayBuffer() : null))
      .catch(() => null),
  ]);
  await resvg.initWasm(fetch(`${RESVG}/index_bg.wasm`));

  const fonts = {
    fontBuffers: font ? [new Uint8Array(font)] : [],
    defaultFontFamily: FAMILY,
    serifFamily: FAMILY,
    sansSerifFamily: FAMILY,
    monospaceFamily: FAMILY,
    cursiveFamily: FAMILY,
    fantasyFamily: FAMILY,
  };

  return (svg, background, zoom) => new resvg.Resvg(svg, {
    background,
    fitTo: { mode: "zoom", value: zoom },
    font: fonts,
  }).render().asPng();
}

/* The browser caches every download, but micropip still resolves svglab's
 * dependencies on each visit, partly on PyPI. What it resolved is kept as a
 * lockfile, so that a later visit to the same build loads it all at once. */
async function readLock(key) {
  try {
    const response = await (await caches.open(LOCKS)).match(key);

    return response ? await response.text() : null;
  } catch {
    return null;  // no Cache Storage outside of a secure context
  }
}

async function keepLock(key, lock) {
  try {
    await caches.delete(LOCKS);  // the locks of other builds
    await (await caches.open(LOCKS)).put(key, new Response(lock));
  } catch {
    // the next visit resolves again
  }
}

/* Pyodide with svglab installed: from the lockfile of an earlier visit, or
 * through micropip, which a stale lockfile falls back to. */
async function loadPython() {
  const { wheel, sha256 } = JSON.parse(await fetchText("wheel.json"));
  const url = new URL(wheel, import.meta.url).href;
  const key = `${url}?sha256=${sha256}&pyodide=${encodeURIComponent(PYODIDE)}`;
  const lock = await readLock(key);

  if (lock) {
    try {
      const pyodide = await loadPyodide({
        indexURL: PYODIDE,
        lockFileContents: lock,
        packageBaseUrl: PYODIDE,
      });
      step("Loading packages…", 0.4, 0.6);
      const loaded = await pyodide.loadPackage("svglab");

      if (loaded.some(({ name }) => name === "svglab")) {
        return pyodide;
      }
    } catch {
      // resolve afresh
    }
  }

  const pyodide = await loadPyodide({ indexURL: PYODIDE, packages: ["micropip"] });
  step("Installing svglab…", 0.5, 2);

  const micropip = pyodide.pyimport("micropip");
  await micropip.install(url);
  await keepLock(key, micropip.freeze());

  return pyodide;
}

async function start() {
  step("Starting Python…", 0.3, 1.7);
  const [pyodide, render] = await Promise.all([loadPython(), loadResvg()]);

  // only now, so that what the installer prints stays in the console
  pyodide.setStdout({ batched: (text) => post({ kind: "out", text }) });
  pyodide.setStderr({ batched: (text) => post({ kind: "err", text }) });

  step("Importing svglab…", 1, 3.5);
  const namespace = pyodide.toPy({ __name__: "playground" });
  pyodide.runPython(await fetchText("bootstrap.py"), { globals: namespace });

  const session = namespace.get("setup")(
    render,
    (url) => post({ kind: "image", text: url }),
  );
  pyodide.pyimport("svglab");

  return { pyodide, session };
}

const started = start();

started.then(
  () => post({ ready: true }),
  (error) => post({ failed: error.message }),
);

// Jedi only helps with the code, so it loads once the code can run, and
// keeps quiet about it, as the console is listening by then; the first help
// imports it, so that the first run does not wait for that
const helping = started.then(({ pyodide }) => pyodide.loadPackage("jedi", {
  messageCallback: () => {},
  errorCallback: (message) => console.warn(message),
}));

self.onmessage = async ({ data: { id, method, args } }) => {
  try {
    const { session } = await started;

    if (HELP.has(method)) {
      await helping;
    }

    let result = await session[method](...args);

    // a Python list or dict comes as a proxy, which cannot cross to the page
    if (result?.toJs) {
      const proxy = result;
      result = proxy.toJs({ dict_converter: Object.fromEntries });
      proxy.destroy();
    }

    post({ id, result });
  } catch (error) {
    post({ id, error: error.message });
  }
};
