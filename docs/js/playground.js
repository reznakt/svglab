/* An svglab playground: the VS Code editor (Monaco) in front of CPython in
 * the browser (Pyodide). Python runs in playground/worker.js, so that loading
 * and running it never freezes the page; its half of the session is in
 * playground/bootstrap.py, and the examples are in playground/examples/. */

const MONACO = "https://cdn.jsdelivr.net/npm/monaco-editor@0.52.2/min/vs";

const EXAMPLES = {
  "parse-and-edit": "Parse and edit",
  optimize: "Shrink a document",
  "path-surgery": "Take a path apart",
  chart: "Draw a chart from data",
  render: "Render to pixels",
  sanitize: "Sanitize an untrusted SVG",
};

// the kinds of Jedi's completions, as Monaco's
const KINDS = {
  module: "Module",
  class: "Class",
  function: "Function",
  property: "Property",
  keyword: "Keyword",
};

/* Instant navigation swaps the page without reloading this script, so the
 * worker and the editor library outlive the page that started them; `emit`
 * and `report` point at whichever page is current. */
let python = null;
let live = false;
let monacoLoader = null;
let emit = () => {};
let report = () => {};
let nextId = 0;

function loadScript(url) {
  return new Promise((resolve, reject) => {
    const script = document.createElement("script");
    script.src = url;
    script.onload = resolve;
    script.onerror = () => reject(new Error(`could not load ${url}`));
    document.head.append(script);
  });
}

// 42 ms, or 1.3 s
function duration(milliseconds) {
  return milliseconds < 1000
    ? `${Math.round(milliseconds)} ms`
    : `${(milliseconds / 1000).toFixed(1)} s`;
}

async function fetchText(url) {
  const response = await fetch(url);

  if (!response.ok) {
    throw new Error(`could not load ${url}`);
  }

  return response.text();
}

/* Starts Python and svglab, around 15 MB, once; every caller shares it. */
function startPython(base) {
  if (python) {
    return python.ready;
  }

  const worker = new Worker(new URL("worker.js", base), { type: "module" });
  const pending = new Map();
  let started;
  let failed;

  const instance = {
    worker,
    pending,
    ready: new Promise((resolve, reject) => {
      started = resolve;
      failed = reject;
    }),
    // fails whatever waits for this Python; the next caller starts another
    stop(error) {
      worker.terminate();

      if (python === instance) {
        python = null;
        live = false;
      }

      failed(error);

      for (const call of pending.values()) {
        call.reject(error);
      }
    },
  };

  worker.onerror = (event) => {
    instance.stop(new Error(event.message || "the worker did not start"));
  };
  worker.onmessage = ({ data }) => {
    if ("id" in data) {
      const call = pending.get(data.id);
      pending.delete(data.id);

      if ("error" in data) {
        call.reject(new Error(data.error));
      } else {
        call.resolve(data.result);
      }
    } else if (data.kind) {
      emit(data.text, data.kind);
    } else if (data.status) {
      report(data.status, data.progress, data.seconds);
    } else if (data.ready) {
      live = true;
      started();
    } else {
      instance.stop(new Error(data.failed));
    }
  };

  python = instance;

  return instance.ready;
}

/* Shuts Python down, whatever it is doing. */
function stopPython() {
  python?.stop(new DOMException("Python was stopped", "AbortError"));
}

/* Calls a method of the session in the worker. */
function call(method, ...args) {
  const { worker, pending } = python;

  return new Promise((resolve, reject) => {
    const id = nextId++;
    pending.set(id, { resolve, reject });
    worker.postMessage({ id, method, args });
  });
}

/* Asks the session for help with the code, which can do without it. */
async function ask(method, ...args) {
  if (!live) {
    return null;
  }

  try {
    return await call(method, ...args);
  } catch {
    return null;
  }
}

/* Completions, signatures and hovers come from Jedi, which reads both the
 * code and the live namespace: names are known before a run, and the objects
 * a run made after it. */
async function provideCompletionItems(model, position) {
  const completions = await ask(
    "complete",
    model.getValue(),
    position.lineNumber,
    position.column - 1,
  );
  const word = model.getWordUntilPosition(position);
  const range = {
    startLineNumber: position.lineNumber,
    endLineNumber: position.lineNumber,
    startColumn: word.startColumn,
    endColumn: position.column,
  };
  const kinds = window.monaco.languages.CompletionItemKind;

  const suggestions = (completions ?? []).map(({ name, kind }, index) => ({
    label: name,
    insertText: name,
    range,
    kind: kinds[KINDS[kind] ?? "Variable"],
    sortText: String(index).padStart(6, "0"),  // Jedi's order, best first
  }));

  return { suggestions };
}

async function provideSignatureHelp(model, position) {
  const help = await ask(
    "signatures",
    model.getValue(),
    position.lineNumber,
    position.column - 1,
  );

  return help && { value: help, dispose() {} };
}

async function provideHover(model, position) {
  const docs = await ask(
    "describe",
    model.getValue(),
    position.lineNumber,
    position.column - 1,
  );

  return docs ? { contents: [{ value: docs }] } : null;
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
    monaco.languages.registerSignatureHelpProvider("python", {
      signatureHelpTriggerCharacters: ["(", ","],
      signatureHelpRetriggerCharacters: [")"],
      provideSignatureHelp,
    });
    monaco.languages.registerHoverProvider("python", { provideHover });

    // follow the site's light/dark toggle
    new MutationObserver(() => monaco.editor.setTheme(theme())).observe(
      document.body,
      { attributeFilter: ["data-md-color-scheme"] },
    );

    return monaco;
  })();

  return monacoLoader;
}

/* Shared code travels in the address, compressed. */
async function pack(text) {
  const stream = new Blob([text]).stream()
    .pipeThrough(new CompressionStream("deflate-raw"));
  const bytes = new Uint8Array(await new Response(stream).arrayBuffer());

  return btoa(Array.from(bytes, (byte) => String.fromCharCode(byte)).join(""))
    .replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
}

async function unpack(packed) {
  const binary = atob(packed.replace(/-/g, "+").replace(/_/g, "/"));
  const bytes = Uint8Array.from(binary, (char) => char.charCodeAt(0));
  const stream = new Blob([bytes]).stream()
    .pipeThrough(new DecompressionStream("deflate-raw"));

  return new Response(stream).text();
}

// the packed code of a link to shared code, if the address is one
function sharedCode() {
  return /^#code=([\w-]+)$/.exec(window.location.hash)?.[1];
}

function initPlayground() {
  const root = document.getElementById("svglab-playground");

  if (!root) {
    return;
  }

  const [
    status, clock, progress, picker, share, clear, reset, runButton, host,
    splitter, output, log, prompt, input,
  ] = [
    "status", "clock", "progress", "picker", "share", "clear", "reset", "run",
    "editor", "splitter", "output", "log", "prompt", "input",
  ].map((name) => root.querySelector(`[data-playground-${name}]`));

  // the words on the buttons that change, beside their icons
  const [runLabel, shareLabel] = [runButton, share].map(
    (button) => button.querySelector("[data-playground-label]"),
  );

  // everything the playground fetches sits next to the page
  const base = new URL(".", window.location.href);

  // code that a link shared, in place of the examples
  let shared = sharedCode();

  let editor = null;
  let busy = false;

  // the code as loaded or last shared, which leaving would not lose
  let saved = "";

  function edited() {
    return editor !== null && editor.getValue() !== saved;
  }

  // what Python is doing, or how the last run went; a busy one spins
  function setStatus(text, state = "busy") {
    status.textContent = text;
    status.dataset.state = state;
  }

  // the bar along the toolbar's edge: Python's startup, a step at a time,
  // or a run that takes a while
  const bar = progress.firstElementChild;
  let creeping;
  let hiding;

  function setProgress(value) {
    clearTimeout(hiding);

    // a new bar starts empty, rather than sliding back from the last one
    if (progress.dataset.mode !== "steps" || !("active" in progress.dataset)) {
      progress.dataset.mode = "steps";
      bar.style.transition = "none";
      progress.style.setProperty("--playground-progress", 0);
      bar.getBoundingClientRect();
      bar.style.transition = "";
    }

    progress.dataset.active = "";
    progress.style.setProperty("--playground-progress", value);
  }

  // a step of the startup creeps on, most of the way in the time it should
  // take, and all the way only once it is done
  function advance([from, to], seconds) {
    const start = performance.now();
    const creep = () => {
      // instant navigation took the page away, and its bar with it
      if (!progress.isConnected) {
        clearInterval(creeping);
      }

      const elapsed = (performance.now() - start) / 1000;
      setProgress(from + (to - from) * (1 - Math.exp((-2 * elapsed) / seconds)));
    };

    clearInterval(creeping);
    creep();
    creeping = setInterval(creep, 100);
  }

  function spinProgress() {
    clearInterval(creeping);
    clearTimeout(hiding);
    progress.dataset.mode = "spin";
    progress.dataset.active = "";
  }

  function hideProgress() {
    clearInterval(creeping);
    delete progress.dataset.active;
  }

  function finishProgress() {
    if ("active" in progress.dataset) {
      clearInterval(creeping);
      setProgress(1);
      hiding = setTimeout(hideProgress, 400);
    }
  }

  // how long a long run has been going, beside the status
  let ticking;

  function startClock(since) {
    const tick = () => {
      clock.textContent = `${((performance.now() - since) / 1000).toFixed(1)} s`;
    };

    tick();
    ticking = setInterval(tick, 100);
  }

  function stopClock() {
    clearInterval(ticking);
    clock.textContent = "";
  }

  function scrollDown() {
    output.scrollTop = output.scrollHeight;
  }

  // a line of a traceback that points into the editor leads there
  function jump(label) {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "playground__jump";
    button.textContent = label;
    button.onclick = (event) => {
      const line = Number(label.slice("line ".length));
      event.stopPropagation();  // the console would take the focus

      if (editor) {
        editor.revealLineInCenter(line);
        editor.setPosition({
          lineNumber: line,
          column: editor.getModel().getLineFirstNonWhitespaceColumn(line) || 1,
        });
        editor.focus();
      }
    };

    return button;
  }

  function write(text, kind) {
    let node;

    if (kind === "image") {
      node = document.createElement("img");
      node.className = "playground__image";
      node.alt = "Rendered result";
      node.onload = scrollDown;
      node.src = text;
    } else {
      node = document.createElement("span");
      node.className = `playground__line playground__line--${kind}`;

      // split around the references, which land at the odd indices
      const parts = kind === "err"
        ? `${text}\n`.split(/(?<=File "<playground>", )(line \d+)/)
        : [`${text}\n`];
      node.append(...parts.map((part, index) => (index % 2 ? jump(part) : part)));
    }

    log.append(node);
    scrollDown();
  }

  emit = write;
  report = (text, span, seconds) => {
    setStatus(text);

    if (span) {
      advance(span, seconds);
    }
  };

  async function load(name) {
    if (name) {
      editor.setValue(await fetchText(new URL(`examples/${name}.py`, base)));
    } else {
      try {
        editor.setValue(await unpack(shared));
      } catch {
        write("The code in this link is damaged, so here is an example.", "err");
        picker.remove(0);  // the shared code
        await load(picker.value);
      }
    }

    saved = editor.getValue();
  }

  // underline where the last run raised, or nothing
  function mark(error) {
    const { editor: editors, MarkerSeverity } = window.monaco;
    const markers = error ? [{ ...error, severity: MarkerSeverity.Error }] : [];
    editors.setModelMarkers(editor.getModel(), "playground", markers);

    if (error) {
      editor.revealLineInCenterIfOutsideViewport(error.startLineNumber);
    }
  }

  // the console is live as soon as Python is
  function ready() {
    if (input.disabled) {
      finishProgress();
      setStatus("Ready", "ready");
      input.disabled = false;
      input.placeholder = "";
    }
  }

  function boot() {
    if (!live) {
      input.disabled = true;
      input.placeholder = "Waiting for Python…";
      setStatus("Starting Python…");
      setProgress(0);
    }

    startPython(base).then(ready, (error) => {
      if (error.name !== "AbortError") {
        hideProgress();
        setStatus("Python did not start", "error");
        write(error.message, "err");
      }
    });
  }

  // one thing at a time: a run of the editor, or a line of the console; a
  // long one turns Run into Stop and shows how long it has taken, a short
  // one does not flash either
  let since = 0;

  async function execute(action) {
    let stoppable;
    busy = true;

    for (const control of [runButton, reset, picker]) {
      control.disabled = true;
    }

    try {
      await startPython(base);
      ready();

      const before = [status.textContent, status.dataset.state];
      since = performance.now();
      stoppable = setTimeout(() => {
        runLabel.textContent = "Stop";
        runButton.dataset.icon = "stop";
        runButton.disabled = false;
        setStatus("Running…");
        startClock(since);
        spinProgress();
      }, 300);
      await action();

      // a line of the console leaves the status of the last run
      if (status.textContent === "Running…") {
        setStatus(...before);
      }
    } catch (error) {
      if (error.name !== "AbortError") {
        setStatus("Error", "error");
        write(error.message, "err");
      }
    } finally {
      clearTimeout(stoppable);
      stopClock();

      // unless Stop has started Python over, with a bar of its own
      if (progress.dataset.mode === "spin") {
        hideProgress();
      }

      runLabel.textContent = "Run";
      runButton.dataset.icon = "run";
      busy = false;

      for (const control of [runButton, reset, picker]) {
        control.disabled = false;
      }
    }
  }

  // a restart of Python drops an unfinished console statement
  function resetPrompt() {
    prompt.textContent = ">>>";
    input.value = "";
  }

  // the transcript stays, with the restart marked, as in IDLE
  function run() {
    if (editor && !busy) {
      resetPrompt();
      mark(null);

      if (log.childElementCount) {
        write("restart", "restart");
      }

      execute(async () => {
        setStatus("Running…");
        const error = await call("run", editor.getValue());
        mark(error);

        if (error) {
          // "ZeroDivisionError: division by zero", by the type's bare name
          const type = error.message.split(":", 1)[0].split(".").at(-1);
          setStatus(`${type} on line ${error.startLineNumber}`, "error");
        } else {
          setStatus(`Done in ${duration(performance.now() - since)}`, "ready");
        }
      });
    }
  }

  // the only way out of an endless loop: a new Python, loaded from the cache
  function stop() {
    const elapsed = performance.now() - since;
    stopPython();
    resetPrompt();
    write(`stopped after ${duration(elapsed)}`, "restart");
    boot();
  }

  // the console: entered lines are echoed with their prompt, and a line that
  // leaves a statement open asks for more, indented to continue the block
  const history = [];
  let recalled = 0;

  function submit() {
    if (busy) {
      return;
    }

    // only blank lines close a block, and the indentation offered is not one
    const line = input.value.trim() ? input.value : "";
    input.value = "";
    write(`${prompt.textContent} ${line}`, "in");

    if (line.trim()) {
      history.push(line);
    }

    recalled = history.length;

    execute(async () => {
      const more = await call("push", line);
      prompt.textContent = more ? "..." : ">>>";

      if (more) {
        const indent = /^\s*/.exec(line)[0];
        input.value = line.trimEnd().endsWith(":") ? `${indent}    ` : indent;
      }
    });
  }

  // Tab completes the name before the cursor as far as it is unambiguous,
  // and lists the candidates past that; in the indentation, it indents
  async function complete() {
    const { value, selectionStart: cursor } = input;
    const before = value.slice(0, cursor);

    if (!before.trim()) {
      input.setRangeText("    ", cursor, input.selectionEnd, "end");
      return;
    }

    const names = ((await ask("complete", before, 1, before.length)) ?? [])
      .map(({ name }) => name);
    const word = /\w*$/.exec(before)[0];
    let common = names[0] ?? "";

    for (const name of names) {
      while (!name.startsWith(common)) {
        common = common.slice(0, -1);
      }
    }

    // typing on while Jedi thought makes its answer stale
    if (input.value !== value || !names.length) {
      return;
    }

    if (common.length > word.length) {
      input.setRangeText(common, cursor - word.length, cursor, "end");
    } else if (names.length > 1) {
      const shown = names.slice(0, 30).join("  ");
      const more = names.length > 30 ? `  (and ${names.length - 30} more)` : "";
      write(`${shown}${more}`, "in");
    }
  }

  input.addEventListener("keydown", (event) => {
    if (event.key === "Enter") {
      event.preventDefault();
      submit();
    } else if (event.key === "Tab" && !event.shiftKey && input.value) {
      // an empty line lets Tab move on, so that the console is no trap
      event.preventDefault();
      complete();
    } else if (event.key === "ArrowUp" || event.key === "ArrowDown") {
      event.preventDefault();
      recalled += event.key === "ArrowUp" ? -1 : 1;
      recalled = Math.min(Math.max(recalled, 0), history.length);
      input.value = history[recalled] ?? "";
    }
  });

  // a click in the pane, unless it selects text, goes to the console
  output.addEventListener("click", () => {
    if (!window.getSelection().toString()) {
      input.focus();
    }
  });

  // the shared code comes first
  function offerShared() {
    if (picker.options[0]?.value !== "") {
      picker.add(new Option("Shared code", ""), 0);
    }
  }

  if (shared) {
    offerShared();
  }

  for (const [name, label] of Object.entries(EXAMPLES)) {
    picker.add(new Option(label, name));
  }

  // the editor's share of the width, set by dragging the divider or by the
  // arrow keys while it has focus
  let split = 2 / 3;

  function setSplit(share) {
    split = Math.min(Math.max(share, 0.2), 0.8);
    splitter.parentElement.style.setProperty("--playground-split", `${split * 100}%`);
    splitter.setAttribute("aria-valuenow", Math.round(split * 100));
  }

  splitter.addEventListener("pointerdown", (event) => {
    event.preventDefault();  // no text selection while dragging
    splitter.setPointerCapture(event.pointerId);
  });
  splitter.addEventListener("pointermove", (event) => {
    if (splitter.hasPointerCapture(event.pointerId)) {
      const box = splitter.parentElement.getBoundingClientRect();
      setSplit((event.clientX - box.left) / box.width);
    }
  });
  splitter.addEventListener("keydown", (event) => {
    const step = { ArrowLeft: -0.05, ArrowRight: 0.05 }[event.key];

    if (step) {
      event.preventDefault();
      setSplit(split + step);
    }
  });

  // switching examples and Reset both start over: the example as written, no
  // state and no transcript
  function startOver() {
    if (live) {
      call("reset");
      setStatus("Ready", "ready");
    }

    log.replaceChildren();
    resetPrompt();
    mark(null);
    load(picker.value);
  }

  // the link to the code as it is: put in the address, and copied
  async function shareCode() {
    const code = editor.getValue();
    const url = new URL(window.location.href);
    shared = await pack(code);
    url.hash = `code=${shared}`;
    window.history.replaceState(window.history.state, "", url);
    saved = code;

    try {
      await navigator.clipboard.writeText(url.href);
      shareLabel.textContent = "Link copied";
      share.dataset.icon = "done";
    } catch {
      shareLabel.textContent = "Link in the address bar";
    }

    setTimeout(() => {
      shareLabel.textContent = "Share";
      share.dataset.icon = "share";
    }, 2000);
  }

  picker.addEventListener("change", startOver);
  reset.addEventListener("click", startOver);
  clear.addEventListener("click", () => log.replaceChildren());
  share.addEventListener("click", () => editor && shareCode());
  runButton.addEventListener("click", () => (busy ? stop() : run()));

  // what the page listens for outside of it ends with the page, which
  // instant navigation swaps without unloading
  function listen(target, type, handler, capture = false) {
    const listener = (event) => {
      if (root.isConnected) {
        handler(event);
      } else {
        target.removeEventListener(type, listener, capture);
      }
    };

    target.addEventListener(type, listener, capture);
  }

  // a link to shared code, opened while here, changes only the address's
  // hash, which reloads nothing; so do Back and Forward between two links
  listen(window, "hashchange", async () => {
    const packed = sharedCode();

    if (!packed) {
      return;
    }

    try {
      await unpack(packed);
    } catch {
      write("The code in this link is damaged.", "err");
      return;
    }

    if (
      edited()
      && !window.confirm("Replace your changes with the code from the link?")
    ) {
      return;
    }

    shared = packed;
    offerShared();
    picker.value = "";

    if (busy) {
      stop();
    }

    // or else the editor loads it once it has loaded
    if (editor) {
      startOver();
    }
  });

  // leaving with changes asks first: the browser asks before the page
  // unloads, and the page asks before instant navigation, which follows a
  // link to another page of the site, or Back or Forward, without unloading
  const leave = "Leave the playground? Your changes to the code will be lost.";
  const here = window.location.pathname;
  let leaving = false;

  listen(window, "beforeunload", (event) => {
    if (edited() && !leaving) {
      event.preventDefault();
    }
  });

  // before instant navigation sees the click
  listen(window, "click", (event) => {
    const link = event.target instanceof Element && event.target.closest("a[href]");

    if (
      !(link instanceof HTMLAnchorElement)
      || event.button !== 0
      || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey
      || (link.target && link.target !== "_self")
      || link.hasAttribute("download")
    ) {
      return;  // not followed in this tab
    }

    const url = new URL(link.href);

    // a link off the site unloads the page, and the browser asks
    if (
      url.origin !== window.location.origin
      || url.pathname === here
      || !edited()
    ) {
      return;
    }

    if (window.confirm(leave)) {
      leaving = true;  // in case it does unload the page after all
    } else {
      event.preventDefault();
      event.stopPropagation();
    }
  }, true);

  // Back and Forward, before they happen: by the time instant navigation
  // hears of them, it is too late; browsers without the Navigation API, or
  // that do not let a page decline them, go without asking
  if (window.navigation) {
    listen(window.navigation, "navigate", (event) => {
      if (
        event.navigationType === "traverse"
        && event.cancelable
        && new URL(event.destination.url).pathname !== here
        && edited()
        && !window.confirm(leave)
      ) {
        event.preventDefault();
      }
    });
  }

  // load Python right away, beside the editor, so that the first run need
  // not wait for it
  boot();

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
      fontFamily: getComputedStyle(output).fontFamily,
      fontSize: 13,
      tabSize: 4,
      padding: { top: 12, bottom: 12 },
      scrollbar: { alwaysConsumeMouseWheel: false },
      // hovers and suggestions may reach past the rounded, clipped box; below
      // the line, a hover stays clear of the page's sticky header
      fixedOverflowWidgets: true,
      hover: { above: false },
    });
    editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.Enter, run);

    return load(picker.value);
  }).catch((error) => {
    setStatus("The editor did not load", "error");
    write(error.message, "err");
  });
}

if (typeof document$ !== "undefined") {
  document$.subscribe(initPlayground);
} else {
  document.addEventListener("DOMContentLoaded", initPlayground);
}
