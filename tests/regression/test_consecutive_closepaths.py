from svglab import PathData


def test_consecutive_closepaths_are_all_written() -> None:
    path_data = PathData.from_str("M 0,0 H 10 Z Z")

    assert path_data.serialize() == "M0,0 H10 Z Z"
