import keyword
from typing import Final

import bidict

from svglab import constants, types


def is_valid_identifier(name: str) -> bool:
    return name.isidentifier() and not keyword.iskeyword(name)


def normalize_attr_name(name: types.AttributeName) -> str:
    normalized = name.replace("-", "_")

    if not is_valid_identifier(normalized):
        normalized = f"{normalized}_"

    if not is_valid_identifier(normalized):
        msg = f"Cannot normalize attribute name: {name!r}"
        raise ValueError(msg)

    return normalized


ATTR_TO_NORMALIZED: Final = bidict.frozenbidict(
    {attr: normalize_attr_name(attr) for attr in constants.ATTRIBUTE_NAMES}
)
