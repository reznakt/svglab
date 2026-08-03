import pytest

import svglab
from svglab import serialize


@pytest.fixture
def formatter() -> serialize.Formatter:
    return serialize.Formatter(indent=9)


def test_nested_with_blocks_restore_the_original_formatter(
    formatter: serialize.Formatter,
) -> None:
    original = serialize.get_current_formatter()

    with formatter:
        with formatter:
            assert serialize.get_current_formatter() is formatter

        assert serialize.get_current_formatter() is formatter

    assert serialize.get_current_formatter() is original


def test_to_xml_does_not_leak_the_current_formatter(
    formatter: serialize.Formatter,
) -> None:
    original = serialize.get_current_formatter()

    # `to_xml()` enters the current formatter, which re-enters `formatter`
    with formatter:
        svglab.Rect().to_xml()

    assert serialize.get_current_formatter() is original


def test_exception_restores_the_original_formatter(
    formatter: serialize.Formatter,
) -> None:
    original = serialize.get_current_formatter()

    with pytest.raises(RuntimeError), formatter:
        raise RuntimeError

    assert serialize.get_current_formatter() is original
