import pytest

from svglab import HorizontalLineTo, PathData
from svglab.serialize import Formatter


# long enough to overflow the interpreter stack under the old recursive
# implementation of `_get_end_at`
_COMMAND_COUNT = 5000


@pytest.fixture
def long_path() -> PathData:
    commands = " ".join(f"H {i}" for i in range(_COMMAND_COUNT))
    return PathData.from_str(f"M 0,0 {commands}")


def test_long_shorthand_run_resolves_the_end_point(
    long_path: PathData,
) -> None:
    assert long_path[-1] == HorizontalLineTo(_COMMAND_COUNT - 1)


def test_long_shorthand_run_serializes_relative(
    long_path: PathData,
) -> None:
    with Formatter(path_data_coordinates="relative"):
        assert long_path.serialize().startswith("m0,0")
