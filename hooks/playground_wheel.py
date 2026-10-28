"""Build a wheel of the working tree for the playground to install.

The documentation describes the repository as it is, so the playground runs
that rather than a release. It could not install a release anyway: those
wheels carry the compiled renderer, which has no WebAssembly build. This
wheel holds only the Python sources; the playground supplies a renderer.
"""

import hashlib
import importlib.metadata
import json
import pathlib
import zipfile

from mkdocs.config.defaults import MkDocsConfig


_PACKAGE = pathlib.Path(__file__).parent.parent / "src" / "svglab"


def on_post_build(config: MkDocsConfig, **_kwargs: object) -> None:
    """Write the wheel, and a file naming and hashing it, next to the page.

    Args:
        config: The documentation configuration.
        _kwargs: Other arguments passed by the build; unused.

    """
    distribution = importlib.metadata.distribution("svglab")
    metadata = distribution.read_text("METADATA")
    assert metadata is not None, "svglab is installed without metadata"

    name = f"svglab-{distribution.version}"
    wheel = f"{name}-py3-none-any.whl"
    out_dir = pathlib.Path(config.site_dir) / "playground"

    with zipfile.ZipFile(out_dir / wheel, "w", zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(_PACKAGE.rglob("*")):
            # the compiled renderer, its stub, and bytecode stay out
            if (
                path.is_file()
                and "__pycache__" not in path.parts
                and not path.name.startswith("_resvg.")
            ):
                zf.write(
                    path, path.relative_to(_PACKAGE.parent).as_posix()
                )

        zf.writestr(f"{name}.dist-info/METADATA", metadata)
        zf.writestr(
            f"{name}.dist-info/WHEEL",
            "Wheel-Version: 1.0\nRoot-Is-Purelib: true\nTag: py3-none-any\n",
        )
        zf.writestr(f"{name}.dist-info/RECORD", "")

    # names the build, which the playground keeps what it resolved under
    digest = hashlib.sha256((out_dir / wheel).read_bytes()).hexdigest()
    (out_dir / "wheel.json").write_text(
        json.dumps({"wheel": wheel, "sha256": digest}), encoding="utf-8"
    )
