import threading

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


def test_threads_do_not_share_the_current_formatter() -> None:
    # the blocks are deliberately not properly nested: the first thread
    # leaves while the second is still inside, so a shared stack would
    # unwind them in the wrong order
    first_entered = threading.Event()
    second_entered = threading.Event()
    first_left = threading.Event()

    seen: dict[int, int] = {}
    errors: list[BaseException] = []

    def first() -> None:
        try:
            with serialize.Formatter(indent=3):
                first_entered.set()
                second_entered.wait(timeout=10)
                seen[3] = serialize.get_current_formatter().indent
        except BaseException as error:  # noqa: BLE001
            errors.append(error)
        finally:
            first_left.set()

    def second() -> None:
        try:
            first_entered.wait(timeout=10)

            with serialize.Formatter(indent=7):
                second_entered.set()
                first_left.wait(timeout=10)
                seen[7] = serialize.get_current_formatter().indent
        except BaseException as error:  # noqa: BLE001
            errors.append(error)

    threads = [
        threading.Thread(target=first),
        threading.Thread(target=second),
    ]

    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    assert not errors
    assert seen == {3: 3, 7: 7}
