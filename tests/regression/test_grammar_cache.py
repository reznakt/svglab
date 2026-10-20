import pathlib
import tempfile

import pytest

from svglab import parse_svg
from svglab.attrparse import parse


def test_grammars_are_not_cached_in_the_temp_dir(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(tempfile, "tempdir", str(tmp_path))
    parse._get_parser.cache_clear()  # noqa: SLF001  # pyright: ignore[reportPrivateUsage]

    parse_svg('<svg><rect width="1px"/></svg>')

    assert not list(tmp_path.glob(".lark*"))
