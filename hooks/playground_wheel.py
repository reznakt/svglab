"""Build a wheel of the working tree for the playground to install.

The documentation describes the current state of the repository, so the
playground should run that, not the last release. A wheel is built during the
documentation build and published alongside the site; the playground installs
it by default and falls back to PyPI if it is missing.
"""

import json
import pathlib
import shutil
import subprocess

from mkdocs.config.defaults import MkDocsConfig


_PROJECT_ROOT = pathlib.Path(__file__).parent.parent
_WHEEL_DIR = "wheels"
_INDEX = "index.json"


def on_post_build(config: MkDocsConfig, **_kwargs: object) -> None:
    """Build the wheel and record its name for the playground.

    Args:
        config: The documentation configuration.
        _kwargs: Other arguments passed by the build; unused.

    """
    uv = shutil.which("uv")
    out_dir = pathlib.Path(config.site_dir) / _WHEEL_DIR

    if uv is None:
        print(  # noqa: T201
            "playground: uv not found; the playground will use PyPI"
        )

        return

    out_dir.mkdir(parents=True, exist_ok=True)

    try:
        subprocess.run(  # noqa: S603
            [uv, "build", "--wheel", "--out-dir", str(out_dir)],
            cwd=_PROJECT_ROOT,
            check=True,
            capture_output=True,
        )
    except subprocess.CalledProcessError as error:
        print(  # noqa: T201
            f"playground: could not build a wheel ({error}); "
            f"the playground will use PyPI"
        )

        return

    wheels = sorted(out_dir.glob("svglab-*.whl"))

    if not wheels:
        return

    # keep only the newest, so repeated builds do not pile up
    for stale in wheels[:-1]:
        stale.unlink()

    wheel = wheels[-1]
    version = wheel.name.split("-")[1]

    (out_dir / _INDEX).write_text(
        json.dumps({"wheel": wheel.name, "version": version}),
        encoding="utf-8",
    )
