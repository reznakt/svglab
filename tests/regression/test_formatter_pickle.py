import pickle

from svglab import Length, serialize


def _formatter() -> serialize.Formatter:
    return serialize.Formatter(
        general_precision=serialize.FloatPrecisionSettings(
            precision_table={
                serialize.PrecisionInterval(0, 1, 2),
                serialize.PrecisionInterval(1, 10, 3),
            }
        ),
        length_unit=["px"],
    )


def test_formatter_round_trips_through_pickle() -> None:
    formatter = _formatter()

    assert pickle.loads(pickle.dumps(formatter)) == formatter  # noqa: S301


def test_formatter_repr_shows_the_values() -> None:
    assert "ValidatorIterator" not in repr(_formatter())


def test_length_units_apply_to_every_length() -> None:
    with _formatter():
        first = serialize.serialize(Length(12, "pt"))
        second = serialize.serialize(Length(12, "pt"))

    assert first == second
    assert first.endswith("px")
