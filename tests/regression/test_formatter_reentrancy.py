import threading

import pytest

from svglab import Rect
from svglab.serialize import Formatter, get_current_formatter


@pytest.fixture
def formatter() -> Formatter:
    return Formatter(indent=9)


def test_nested_with_blocks_restore_the_original_formatter(
    formatter: Formatter,
) -> None:
    original = get_current_formatter()

    with formatter:
        with formatter:
            assert get_current_formatter() is formatter

        assert get_current_formatter() is formatter

    assert get_current_formatter() is original


def test_to_xml_does_not_leak_the_current_formatter(
    formatter: Formatter,
) -> None:
    original = get_current_formatter()

    # `to_xml()` enters the current formatter, which re-enters `formatter`
    with formatter:
        Rect().to_xml()

    assert get_current_formatter() is original


def test_exception_restores_the_original_formatter(
    formatter: Formatter,
) -> None:
    original = get_current_formatter()

    with pytest.raises(RuntimeError), formatter:
        raise RuntimeError

    assert get_current_formatter() is original


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
            with Formatter(indent=3):
                first_entered.set()
                second_entered.wait(timeout=10)
                seen[3] = get_current_formatter().indent
        except BaseException as error:  # ruff: ignore[BLE001]
            errors.append(error)
        finally:
            first_left.set()

    def second() -> None:
        try:
            first_entered.wait(timeout=10)

            with Formatter(indent=7):
                second_entered.set()
                first_left.wait(timeout=10)
                seen[7] = get_current_formatter().indent
        except BaseException as error:  # ruff: ignore[BLE001]
            errors.append(error)

    threads = [
        threading.Thread(target=first),
        threading.Thread(target=second),
    ]

    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    if errors:
        raise BaseExceptionGroup("a formatter thread failed", errors)

    assert seen == {3: 3, 7: 7}
