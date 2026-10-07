import inspect

from svglab import Length


def test_length_unit_list_is_separated_from_its_introduction() -> None:
    doc = inspect.cleandoc(Length.__doc__ or "")

    # Markdown only starts a list after a blank line
    assert "Available units are:\n\n- `%`" in doc
