import pytest

import svglab
from svglab import serialize


# long enough to overflow the interpreter stack under the old recursive
# implementation of `_get_end_at`
_COMMAND_COUNT = 5000


@pytest.fixture
def long_path() -> svglab.PathData:
    commands = " ".join(f"H {i}" for i in range(_COMMAND_COUNT))
    return svglab.PathData.from_str(f"M 0,0 {commands}")


def test_long_shorthand_run_resolves_the_end_point(
    long_path: svglab.PathData,
) -> None:
    assert long_path[-1] == svglab.HorizontalLineTo(_COMMAND_COUNT - 1)


def test_long_shorthand_run_serializes_relative(
    long_path: svglab.PathData,
) -> None:
    with serialize.Formatter(path_data_coordinates="relative"):
        assert long_path.serialize().startswith("m0,0")
