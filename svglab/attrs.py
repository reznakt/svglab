import keyword
from typing import Final

import bidict

from svglab import constants, types


def is_valid_identifier(name: str) -> bool:
    """Check if a string is a valid Python identifier and not a reserved keyword.

    Args:
        name: The string to check.

    Returns:
        `True` if the string is a valid Python identifier, `False` otherwise.

    Examples:
        >>> is_valid_identifier("foo")
        True
        >>> is_valid_identifier("class")
        False
        >>> is_valid_identifier("123")
        False
        >>> is_valid_identifier("for")
        False

    """
    return name.isidentifier() and not keyword.iskeyword(name)


def normalize_attr_name(name: types.AttributeName) -> str:
    """Convert an SVG attribute name to a valid Python identifier.

    Args:
        name: The attribute name to normalize.

    Returns:
        The normalized attribute name.

    Raises:
        ValueError: If the attribute name cannot be normalized.

    Examples:
        >>> normalize_attr_name("width")
        'width'
        >>> normalize_attr_name("stroke-width")
        'stroke_width'
        >>> normalize_attr_name("xlink:href")
        'xlink_href'
        >>> normalize_attr_name("class")
        'class_'

    """
    normalized: str = name

    substitutions = {
        "-": "_",
        ":": "_",
    }

    for old, new in substitutions.items():
        normalized = normalized.replace(old, new)

    if not is_valid_identifier(normalized):
        normalized = f"{normalized}_"

    if not is_valid_identifier(normalized):
        msg = f"Cannot normalize attribute name: {name!r}"
        raise ValueError(msg)

    return normalized


ATTR_TO_NORMALIZED: Final = bidict.frozenbidict(
    {attr: normalize_attr_name(attr) for attr in constants.ATTRIBUTE_NAMES}
)
"""A bidirectional mapping of SVG attribute names to normalized Python identifiers."""
