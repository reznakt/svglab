import pytest
from typing_extensions import Literal

import svglab
from svglab.attrparse import path_data


@pytest.mark.parametrize(
    "d",
    ["M 0,0 M 5,5", "M 0,0 M 5,5 L 10,10", "M 0,0 L 5,5 M 10,10 M 20,20"],
)
@pytest.mark.parametrize("coordinates", ["absolute", "relative"])
def test_consecutive_movetos_survive_a_roundtrip(
    d: str, coordinates: Literal["absolute", "relative"]
) -> None:
    original = path_data.PathData.from_str(d)

    with svglab.Formatter(path_data_coordinates=coordinates):
        serialized = original.serialize()

    assert path_data.PathData.from_str(serialized) == original
