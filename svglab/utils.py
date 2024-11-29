from collections.abc import Callable, Iterable, Iterator, MutableMapping, Sized
from functools import cached_property, reduce
from reprlib import recursive_repr
from reprlib import repr as _repr
from typing import Final, Protocol, final, runtime_checkable


class Repr(Protocol):
    """Mixin to provide a sensible __repr__ implementation.

    Example:
    >>> class Foo(Repr):
    ...     def __init__(self, bar: str) -> None:
    ...         self.bar = bar
    >>> foo = Foo("baz")
    >>> repr(foo)
    "Foo(bar='baz')"

    """

    @recursive_repr()
    def __repr__(self) -> str:
        name = type(self).__name__
        attrs = ", ".join(
            f"{key}={_repr(value)}" for key, value in self.__dict__.items()
        )

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

    @cached_property
    def __len(self) -> int:
        return reduce(lambda acc, _: acc + 1, self, 0)

    def __len__(self) -> int:
        return self.__len

    @cached_property
    def __bool(self) -> bool:
        try:
            next(iter(self))
        except StopIteration:
            return False
        else:
            return True

    def __bool__(self) -> bool:
        return self.__bool

    def __str__(self) -> str:
        name = type(self).__name__
        contents = ", ".join(str(item) for item in self)
        return f"{name}({contents})"


@final
class MappingFilterWrapper[K, V](MutableMapping[K, V]):
    """A wrapper around a mutable mapping that filters keys.

    Example:
    >>> mapping = MappingFilterWrapper(
    ...     {"foo": 1, "bar": 2},
    ...     key_filter=lambda key: key == "foo",
    ... )
    >>> mapping["foo"]
    1
    >>> mapping["bar"]
    Traceback (most recent call last):
        ...
    KeyError: 'bar'

    """

    def __init__(
        self, mapping: MutableMapping[K, V], /, *, key_filter: Callable[[K], bool]
    ) -> None:
        """Initialize the wrapper.

        Args:
            mapping: The mapping to wrap.
            key_filter: A predicate that determines whether a key should be allowed.

        """
        self.__mapping: Final = mapping
        self.__key_filter: Final = key_filter

    def __check_key(self, key: K) -> None:
        if not self.__key_filter(key):
            raise KeyError(key)

    def __getitem__(self, key: K) -> V:
        self.__check_key(key)
        return self.__mapping[key]

    def __setitem__(self, key: K, value: V) -> None:
        self.__check_key(key)
        self.__mapping[key] = value

    def __delitem__(self, key: K) -> None:
        self.__check_key(key)
        del self.__mapping[key]

    def __iter__(self) -> Iterator[K]:
        return filter(self.__key_filter, self.__mapping)

    def __len__(self) -> int:
        return reduce(lambda acc, _: acc + 1, self, 0)

    def __repr__(self) -> str:
        return repr(dict(self))


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


@runtime_checkable
class SupportsWrite[T: str | bytes](Protocol):
    """Protocol for objects that support writing.

    This exists because using `SupportsWrite` from `typeshed` causes problems.

    Example:
    >>> from io import StringIO
    >>> buf = StringIO()
    >>> isinstance(buf, SupportsWrite)
    True

    """

    def write(self, data: T, /) -> int: ...
