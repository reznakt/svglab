/* Smoke-tests the documentation's playground in Pyodide, under Node: runs the
 * built site's worker.js, which installs the wheel the build made, and runs
 * every example through it, failing on anything written to stderr. The
 * examples' API is tested natively too; this tests what only the browser has,
 * from Pyodide's packages to the stand-in renderer.
 *
 *   node tests/playground_smoke.mjs site/playground */

import { access, mkdir, readdir, readFile, writeFile } from "node:fs/promises";
import { register } from "node:module";
import { tmpdir } from "node:os";
import { join, resolve } from "node:path";
import { pathToFileURL } from "node:url";

const site = resolve(process.argv[2] ?? "site/playground");

// Pyodide runs from files on disk under Node, though its packages still come
// from the CDN; the worker names the release
const cdn = /https:\/\/cdn\.jsdelivr\.net\/pyodide\/v([^/]+)\/full\//.exec(
  await readFile(join(site, "worker.js"), "utf8"),
);
const local = join(tmpdir(), `svglab-playground-pyodide-${cdn[1]}`);
await mkdir(local, { recursive: true });

for (const file of [
  "pyodide.mjs",
  "pyodide.asm.mjs",
  "pyodide.asm.wasm",
  "python_stdlib.zip",
  "pyodide-lock.json",
]) {
  try {
    await access(join(local, file));
  } catch {
    const response = await fetch(`${cdn[0]}${file}`);

    if (!response.ok) {
      throw new Error(`could not download ${file}`);
    }

    await writeFile(join(local, file), new Uint8Array(await response.arrayBuffer()));
  }
}

// the worker imports Pyodide and resvg from the CDN, which Node cannot by
// itself; Pyodide's import is pointed at the files on disk
register(`data:text/javascript,${encodeURIComponent(`
  let pyodide;

  export function initialize(data) {
    pyodide = data;
  }

  export async function resolve(specifier, context, next) {
    if (/^https?:/.test(specifier)) {
      return { url: specifier, shortCircuit: true };
    }

    if (/^https?:/.test(context.parentURL ?? "") && /^\\.{0,2}\\//.test(specifier)) {
      return { url: new URL(specifier, context.parentURL).href, shortCircuit: true };
    }

    return next(specifier, context);
  }

  export async function load(url, context, next) {
    if (url === pyodide.cdn + "pyodide.mjs") {
      const source = \`
        import { loadPyodide as load } from \${JSON.stringify(pyodide.module)};
        export const loadPyodide = (options) =>
          load({ ...options, indexURL: \${JSON.stringify(pyodide.local)} });
      \`;

      return { format: "module", source, shortCircuit: true };
    }

    if (!/^https?:/.test(url)) {
      return next(url, context);
    }

    const response = await fetch(url);

    if (!response.ok) {
      throw new Error(\`could not load \${url}\`);
    }

    return { format: "module", source: await response.text(), shortCircuit: true };
  }
`)}`, {
  data: {
    cdn: cdn[0],
    local: `${local}/`,
    module: pathToFileURL(join(local, "pyodide.mjs")).href,
  },
});

// and it fetches the files beside it, which here are on disk
const fetchOnline = globalThis.fetch;
globalThis.fetch = async (resource, options) => {
  const url = new URL(resource.url ?? resource);

  return url.protocol === "file:"
    ? new Response(await readFile(url))
    : fetchOnline(resource, options);
};

// the worker's side of the page: it posts here, and listens on `onmessage`
const output = [];
const pending = new Map();
let nextId = 0;
let started;
const ready = new Promise((resolve, reject) => {
  started = { resolve, reject };
});

globalThis.self = globalThis;
globalThis.postMessage = (message) => {
  if ("id" in message) {
    const call = pending.get(message.id);
    pending.delete(message.id);

    if ("error" in message) {
      call.reject(new Error(message.error));
    } else {
      call.resolve(message.result);
    }
  } else if (message.kind) {
    output.push(message);
  } else if (message.status) {
    console.log(message.status);
  } else if (message.ready) {
    started.resolve();
  } else {
    started.reject(new Error(message.failed));
  }
};

function call(method, ...args) {
  return new Promise((resolve, reject) => {
    const id = nextId++;
    pending.set(id, { resolve, reject });
    globalThis.onmessage({ data: { id, method, args } });
  });
}

await import(pathToFileURL(join(site, "worker.js")).href);
await ready;

let failures = 0;

function check(ok, label, details = "") {
  console.log(`${ok ? "ok  " : "FAIL"} ${label}${details ? `: ${details}` : ""}`);
  failures += ok ? 0 : 1;
}

// what the editor asks for, which needs Jedi; first, as under Node Python
// runs on the thread that downloads Jedi in the background
const completions = await call("complete", "from svglab import parse_s", 1, 26);
check(completions.some(({ name }) => name === "parse_svg"), "completions");

const docs = await call("describe", "from svglab import parse_svg", 1, 22);
check(docs?.includes("Parse an SVG document"), "hover docs");

const signatures = await call("signatures", "from svglab import parse_svg\nparse_svg(", 2, 10);
check(signatures?.signatures.length > 0, "signatures");

for (const name of (await readdir(join(site, "examples"))).sort()) {
  output.length = 0;
  const error = await call("run", await readFile(join(site, "examples", name), "utf8"));
  const errors = output.filter(({ kind }) => kind === "err").map(({ text }) => text);
  const images = output.filter(({ kind }) => kind === "image").length;

  check(
    !error && !errors.length,
    name,
    errors.length ? errors.join("\n") : `${output.length - images} lines, ${images} images`,
  );
}

// text renders, with the one font the stand-in renderer has
output.length = 0;
await call("run", `
from svglab import parse_svg
svg = parse_svg('<svg xmlns="http://www.w3.org/2000/svg" width="80" height="30">'
                '<text x="5" y="20">Hello</text></svg>')
print(svg.render().getbbox() is not None)
`);
check(output.map(({ text }) => text).join("") === "True", "text renders");

process.exit(failures ? 1 : 0);
