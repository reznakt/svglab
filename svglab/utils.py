from collections.abc import (
    Callable,
    Hashable,
    Iterable,
    Iterator,
    MutableMapping,
    Sized,
)
from functools import cached_property, reduce
from reprlib import recursive_repr
from reprlib import repr as _repr
from typing import Final, Protocol, TypeVar, final, runtime_checkable

_T = TypeVar("_T")
_KT = TypeVar("_KT", bound=Hashable)
_VT = TypeVar("_VT", bound=Hashable)
_AnyStr_contra = TypeVar("_AnyStr_contra", str, bytes, contravariant=True)
_AnyStr_co = TypeVar("_AnyStr_co", str, bytes, covariant=True)


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


class SizedIterable(Sized, Iterable[_T], Repr):
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

    def __init__(self, source: Iterable[_T]) -> None:
        self.__source: Final = source

    def __iter__(self) -> Iterator[_T]:
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
class MappingFilterWrapper(MutableMapping[_KT, _VT]):
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
        self, mapping: MutableMapping[_KT, _VT], /, *, key_filter: Callable[[_KT], bool]
    ) -> None:
        """Initialize the wrapper.

        Args:
            mapping: The mapping to wrap.
            key_filter: A predicate that determines whether a key should be allowed.

        """
        self.__mapping: Final = mapping
        self.__key_filter: Final = key_filter

    def __check_key(self, key: _KT) -> None:
        if not self.__key_filter(key):
            raise KeyError(key)

    def __getitem__(self, key: _KT) -> _VT:
        self.__check_key(key)
        return self.__mapping[key]

    def __setitem__(self, key: _KT, value: _VT) -> None:
        self.__check_key(key)
        self.__mapping[key] = value

    def __delitem__(self, key: _KT) -> None:
        self.__check_key(key)
        del self.__mapping[key]

    def __iter__(self) -> Iterator[_KT]:
        return filter(self.__key_filter, self.__mapping)

    def __len__(self) -> int:
        return reduce(lambda acc, _: acc + 1, self, 0)

    def __repr__(self) -> str:
        return repr(dict(self))


@runtime_checkable
class SupportsRead(Protocol[_AnyStr_co]):
    """Protocol for objects that support reading.

    This exists because using `SupportsRead` from `typeshed` causes problems.

    Example:
    >>> from io import StringIO
    >>> buf = StringIO()
    >>> isinstance(buf, SupportsRead)
    True

    """

    def read(self, size: int | None = None, /) -> _AnyStr_co: ...


@runtime_checkable
class SupportsWrite(Protocol[_AnyStr_contra]):
    """Protocol for objects that support writing.

    This exists because using `SupportsWrite` from `typeshed` causes problems.

    Example:
    >>> from io import StringIO
    >>> buf = StringIO()
    >>> isinstance(buf, SupportsWrite)
    True

    """

    def write(self, data: _AnyStr_contra, /) -> int: ...
