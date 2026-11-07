# pyright: reportPrivateUsage=false

import functools
from collections.abc import Callable

from griffe._internal import models
from griffe_fieldz import FieldzExtension
from properdocs.config.defaults import ProperDocsConfig
from typing_extensions import ParamSpec, TypeVar


_P = ParamSpec("_P")
_R = TypeVar("_R")

_CACHE_MARKER = "__svglab_cached__"


def on_config(
    config: ProperDocsConfig, **_kwargs: object
) -> ProperDocsConfig:
    original = models.Class._mro  # ruff: ignore[SLF001]

    if getattr(original, _CACHE_MARKER, False):
        return config

    cache: dict[int, list[models.Class]] | None = None

    def cached_mro(
        self: models.Class, seen: tuple[str, ...] = ()
    ) -> list[models.Class]:
        if cache is None:
            return original(self, seen)

        key = id(self)
        result = cache.get(key)

        if result is None:
            result = cache[key] = original(self, seen)

        return result

    def with_cache(hook: Callable[_P, _R]) -> Callable[_P, _R]:
        @functools.wraps(hook)
        def wrapper(*args: _P.args, **kwargs: _P.kwargs) -> _R:
            nonlocal cache
            cache = {}

            try:
                return hook(*args, **kwargs)
            finally:
                cache = None

        return wrapper

    setattr(cached_mro, _CACHE_MARKER, True)
    models.Class._mro = cached_mro  # ruff: ignore[SLF001]
    FieldzExtension.on_class_members = with_cache(
        FieldzExtension.on_class_members
    )
    FieldzExtension.on_class = with_cache(FieldzExtension.on_class)

    return config
