import os
import pathlib
import subprocess
import sys

import pytest

from svglab import parse_svg


@pytest.mark.parametrize("encoding", ["iso-8859-1", "utf-16"])
def test_parse_path_honors_the_declared_encoding(
    tmp_path: pathlib.Path, encoding: str
) -> None:
    path = tmp_path / "drawing.svg"
    markup = (
        f'<?xml version="1.0" encoding="{encoding}"?>'
        "<svg><title>čéü</title></svg>"
    )
    path.write_bytes(markup.encode(encoding, errors="replace"))

    expected = "čéü".encode(encoding, errors="replace").decode(encoding)

    assert expected in parse_svg(path).to_xml()


def test_save_writes_utf8_regardless_of_the_locale(
    tmp_path: pathlib.Path,
) -> None:
    path = tmp_path / "drawing.svg"
    script = (
        "import sys; from svglab import parse_svg; "
        "parse_svg('<svg><title>\\u010d\\u00e9\\u00fc</title></svg>')"
        ".save(sys.argv[1])"
    )
    env = os.environ | {
        "LC_ALL": "C",
        "PYTHONUTF8": "0",
        "PYTHONCOERCECLOCALE": "0",
    }

    subprocess.run(  # ruff: ignore[S603]
        [sys.executable, "-c", script, str(path)], check=True, env=env
    )

    assert "čéü" in path.read_text(encoding="utf-8")
