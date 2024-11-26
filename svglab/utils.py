from collections.abc import Callable, Iterable, Iterator, MutableMapping, Sized
from functools import reduce
from typing import Final, final


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


class SizedIterable[T](Sized, Iterable[T], Repr):
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

    def __str__(self) -> str:
        name = self.__class__.__name__
        contents = ", ".join(repr(item) for item in self)
        return f"{name}({contents})"


@final
class MappingFilterWrapper[K, V](MutableMapping[K, V]):
    def __init__(
        self, attr_dict: MutableMapping[K, V], /, *, key_filter: Callable[[K], bool]
    ) -> None:
        self.__attr_dict: Final = attr_dict
        self.__key_filter: Final = key_filter

    def __check_key(self, key: K) -> None:
        if not self.__key_filter(key):
            raise KeyError(key)

    def __getitem__(self, key: K) -> V:
        self.__check_key(key)
        return self.__attr_dict[key]

    def __setitem__(self, key: K, value: V) -> None:
        self.__check_key(key)
        self.__attr_dict[key] = value

    def __delitem__(self, key: K) -> None:
        self.__check_key(key)
        del self.__attr_dict[key]

    def __iter__(self) -> Iterator[K]:
        return filter(self.__key_filter, self.__attr_dict)

    def __len__(self) -> int:
        return reduce(lambda acc, _: acc + 1, self, 0)

    def __repr__(self) -> str:
        return repr(dict(self))
