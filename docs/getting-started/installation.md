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

## Verify installation

Confirm everything is working:

```bash
python -c "import svglab; print(svglab.__version__)"
```

If this prints a version number, you're all set. Head to the [Quickstart](quickstart.md) to start using the library.
