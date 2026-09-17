"""`version` is a number, not a choice between the versions that exist."""

import pytest

import svglab


def _svg(version: str) -> str:
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" '
        f'version="{version}" width="10" height="10"/>'
    )


@pytest.mark.parametrize(
    "version", ["1", "1.0", "1.1", "1.2", "2", "0.9", "1.10"]
)
def test_any_number_is_accepted_as_a_version(version: str) -> None:
    # the specification defines the attribute as `<number>`; `version="1"`
    # is the same version as `version="1.0"` and appears in the wild far
    # more often than the enumeration allowed for
    svg = svglab.parse_svg(_svg(version))

    assert svg.version == pytest.approx(float(version))


@pytest.mark.parametrize("version", ["one", "1.1.1", "", "1,1"])
def test_something_that_is_not_a_number_is_still_refused(
    version: str,
) -> None:
    with pytest.raises(Exception, match=r"."):
        svglab.parse_svg(_svg(version))
