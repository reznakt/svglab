import pathlib
import runpy

import pytest
from typing_extensions import Final

from tests.conftest import THIS_DIR


# the documentation's playground runs them in the browser, against the same API
EXAMPLES: Final = sorted(
    (THIS_DIR.parent / "docs" / "playground" / "examples").glob("*.py")
)


def test_examples_are_found() -> None:
    assert EXAMPLES


@pytest.mark.parametrize(
    "example", EXAMPLES, ids=[example.stem for example in EXAMPLES]
)
def test_example_runs(example: pathlib.Path) -> None:
    runpy.run_path(str(example))
