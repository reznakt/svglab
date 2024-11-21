from collections.abc import Iterable, Iterator, Sized
from functools import reduce
from typing import Final

__all__ = ["SizedIterable", "Repr"]


class SizedIterable[T](Sized, Iterable[T]):
    """An iterable with a length.

    Example:
    >>> iterable = SizedIterable([1, 2, 3])
    >>> len(iterable)
    3
    >>> bool(iterable)
    True
    >>> for item in iterable:
    ...     print(item)
    1
    2
    3
    >>> len(iterable)
    3

    """

    def __init__(self, source: Iterable[T]) -> None:
        self.__source: Final = source

    def __iter__(self) -> Iterator[T]:
        return iter(self.__source)

    def __len__(self) -> int:
        _iter = iter(self.__source)
        return reduce(lambda acc, _: acc + 1, _iter, 0)

    def __bool__(self) -> bool:
        return len(self) > 0


class Repr:
    """Mixin to provide a sensible __repr__ implementation.

    Example:
    >>> class Foo(Repr):
    ...     def __init__(self, bar: str) -> None:
    ...         self.bar = bar
    >>> foo = Foo("baz")
    >>> repr(foo)
    "Foo(bar='baz')"

    """

    def __repr__(self) -> str:
        name = self.__class__.__name__
        attrs = ", ".join(f"{key}={value!r}" for key, value in self.__dict__.items())

        return f"{name}({attrs})"
