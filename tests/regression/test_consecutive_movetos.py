import pytest
from typing_extensions import Literal

import svglab


@pytest.mark.parametrize(
    "d",
    ["M 0,0 M 5,5", "M 0,0 M 5,5 L 10,10", "M 0,0 L 5,5 M 10,10 M 20,20"],
)
@pytest.mark.parametrize("coordinates", ["absolute", "relative"])
def test_consecutive_movetos_survive_a_roundtrip(
    d: str, coordinates: Literal["absolute", "relative"]
) -> None:
    original = svglab.PathData.from_str(d)

    with svglab.Formatter(path_data_coordinates=coordinates):
        serialized = original.serialize()

    assert svglab.PathData.from_str(serialized) == original
