import pickle

from svglab import Length
from svglab.serialize import (
    FloatPrecisionSettings,
    Formatter,
    PrecisionInterval,
    serialize,
)


def _formatter() -> Formatter:
    return Formatter(
        general_precision=FloatPrecisionSettings(
            precision_table={
                PrecisionInterval(0, 1, 2),
                PrecisionInterval(1, 10, 3),
            }
        ),
        length_unit=["px"],
    )


def test_formatter_round_trips_through_pickle() -> None:
    formatter = _formatter()

    assert pickle.loads(pickle.dumps(formatter)) == formatter  # ruff: ignore[S301]


def test_formatter_repr_shows_the_values() -> None:
    assert "ValidatorIterator" not in repr(_formatter())


def test_length_units_apply_to_every_length() -> None:
    with _formatter():
        first = serialize(Length(12, "pt"))
        second = serialize(Length(12, "pt"))

    assert first == second
    assert first.endswith("px")
