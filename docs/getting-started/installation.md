# Installation

## Requirements

In order to use <span style="font-variant: small-caps;">svglab</span>, **you need to have Python 3.10 or higher installed** on your system. You can download the latest version of Python from the [official website](https://www.python.org/downloads/) or use your system's package manager.

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

Alternatively, the latest development version can be installed directly from the [GitHub repository](https://github.com/reznakt/svglab):

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
