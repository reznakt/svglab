# Installation

## Requirements

In order to use <span style="font-variant: small-caps;">svglab</span>, **you need to have Python 3.11 or higher installed** on your system. You can download the latest version of Python from the [official website](https://www.python.org/downloads/) or use your system's package manager.

<span style="font-variant: small-caps;">svglab</span> bundles a small Rust extension module that binds [resvg](https://lib.rs/crates/resvg), the renderer behind `Svg.render()`. Prebuilt wheels are published for Linux (glibc and musl) and macOS on x86-64 and ARM64, and for Windows on x86-64, so most users need nothing else.

Anywhere else, and when installing from the GitHub repository, the extension module is compiled during installation. That needs a [Rust toolchain](https://rustup.rs/) of version 1.85 or newer and a linker: a C compiler such as GCC or Clang on Linux, the Xcode Command Line Tools on macOS, or the Visual Studio Build Tools on Windows. If `cargo` is not on the `PATH`, the build downloads Rust into a temporary directory by itself; set `MATURIN_NO_INSTALL_RUST=1` to make it fail instead.

Wheels for the free-threaded builds of CPython 3.14 (`3.14t`) and 3.15 or newer (`3.15t`) are published as well. On those builds the GIL is re-enabled when <span style="font-variant: small-caps;">svglab</span> is imported, because [lxml](https://pypi.org/project/lxml/) does not yet declare support for free-threading, so rendering does not run in parallel by default. Setting `PYTHON_GIL=0` overrides this, but it opts every dependency into free-threading whether or not it is ready for it.

## Install from PyPI

Tagged releases are available on [PyPI](https://pypi.org/project/svglab/) and can be installed using pip, poetry, uv or any other Python package manager.

=== "pip"

    ```bash
    pip install svglab
    ```

=== "poetry"

    ```bash
    poetry add svglab
    ```

=== "uv"

    ```bash
    uv add svglab
    ```

## Optional extras

The `html5lib` extra installs [html5lib](https://pypi.org/project/html5lib/), which
enables `parse_svg(..., parser="html5lib")`. The other parsers (`lxml-xml`, the
default, as well as `lxml` and `html.parser`) need nothing beyond the base
dependencies.

=== "pip"

    ```bash
    pip install "svglab[html5lib]"
    ```

=== "poetry"

    ```bash
    poetry add "svglab[html5lib]"
    ```

=== "uv"

    ```bash
    uv add "svglab[html5lib]"
    ```

## Install from source

Alternatively, the latest development version can be installed directly from the [GitHub repository](https://github.com/reznakt/svglab). This compiles the extension module, so it needs the build [requirements](#requirements) described above.

=== "pip"

    ```bash
    pip install git+https://github.com/reznakt/svglab.git
    ```

=== "poetry"

    ```bash
    poetry add git+https://github.com/reznakt/svglab.git
    ```

=== "uv"

    ```bash
    uv add git+https://github.com/reznakt/svglab.git
    ```
