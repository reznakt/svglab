# patching a private griffe method is the whole point of this module
# pyright: reportPrivateUsage=false

"""Memoize griffe's C3 linearization of class hierarchies.

`griffe.Class._mro()` recurses into every base class without caching its
result. Because each SVG element inherits from dozens of single-attribute
mixins that in turn share ancestors, the same linearizations get recomputed
over and over: a full documentation build issues about 15,500 `_mro()` calls
for 486 distinct classes and spends roughly 87% of its time in
`griffe._internal.c3linear`.

Caching the result per class brings a local `CI=true properdocs build` down
from about 26 minutes to under 30 seconds, and produces the same
documentation.

Note that the cache ignores griffe's `seen` argument, which exists to detect
inheritance cycles. A cycle is therefore only reported if it is hit while the
linearization of a class is computed for the first time. Nothing in this
project inherits cyclically, so this is not a problem in practice, but it is
the reason this lives here instead of upstream.
"""

from griffe._internal import models
from mkdocs.config.defaults import MkDocsConfig


_CACHE_MARKER = "__svglab_cached__"


def on_config(config: MkDocsConfig, **_kwargs: object) -> MkDocsConfig:
    """Install the cache before any documentation is rendered.

    Args:
        config: The documentation configuration, passed through unchanged.
        _kwargs: Other arguments passed by the build; unused.

    Returns:
        The configuration, unchanged.

    """
    original = models.Class._mro  # noqa: SLF001

    if getattr(original, _CACHE_MARKER, False):
        return config

    # `_mro()` always returns a list whose first item is the class itself,
    # so a cached entry keeps its own key alive and ids are never reused.
    cache: dict[int, list[models.Class]] = {}

    def cached_mro(
        self: models.Class, seen: tuple[str, ...] = ()
    ) -> list[models.Class]:
        key = id(self)
        result = cache.get(key)

        if result is None:
            # errors (such as cycles) are deliberately not cached
            result = cache[key] = original(self, seen)

        return result

    setattr(cached_mro, _CACHE_MARKER, True)
    models.Class._mro = cached_mro  # noqa: SLF001

    return config
