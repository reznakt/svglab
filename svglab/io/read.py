from typing import Protocol, runtime_checkable

from bs4 import BeautifulSoup as _BeautifulSoup

__all__ = ["parse_svg"]


@runtime_checkable
class SupportsRead[T: str | bytes](Protocol):
    """Protocol for objects that support reading.

    This exists because using `SupportsRead` from `typeshed` causes problems.

    Example:
    >>> from io import StringIO
    >>> buf = StringIO()
    >>> isinstance(buf, SupportsRead)
    True

    """

    def read(self, size: int | None = None, /) -> T: ...


class BeautifulSoup(_BeautifulSoup):
    def __init__(
        self, markup: str | bytes | SupportsRead[str] | SupportsRead[bytes] = ""
    ) -> None:
        super().__init__(markup=markup, features="lxml-xml")


def parse_svg(
    markup: str | bytes | SupportsRead[str] | SupportsRead[bytes],
) -> BeautifulSoup:
    return BeautifulSoup(markup)
