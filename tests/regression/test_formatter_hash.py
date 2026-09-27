from collections.abc import Mapping, Sequence

from typing_extensions import Literal

from svglab import serialize
from svglab.elements import names


def _formatter(
    order: Mapping[names.ElementName | Literal["*"], Sequence[str]]
    | None = None,
) -> serialize.Formatter:
    return serialize.Formatter(
        general_precision=serialize.FloatPrecisionSettings(
            precision_table=[serialize.PrecisionInterval(0, 1, 2)]
        ),
        length_unit=["px", "mm"],
        attribute_order=order or {"*": ["id"], "rect": ["x", "y"]},
    )


def test_default_formatter_is_hashable() -> None:
    assert hash(serialize.Formatter()) == hash(serialize.Formatter())


def test_equal_formatters_hash_equal() -> None:
    reordered = _formatter({"rect": ["x", "y"], "*": ["id"]})

    assert _formatter() == reordered
    assert hash(_formatter()) == hash(reordered)
    assert len({_formatter(), reordered}) == 1


def test_different_attribute_orders_hash_differently() -> None:
    swapped = _formatter({"*": ["id"], "rect": ["y", "x"]})

    assert _formatter() != swapped
    assert hash(_formatter()) != hash(swapped)
