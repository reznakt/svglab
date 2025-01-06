import typing
from typing import Final, Literal, TypeAlias


Xmlns: TypeAlias = Literal["http://www.w3.org/2000/svg"]
"""Type representing valid values for the `xmlns` attribute."""

DEFAULT_XMLNS: Final[Xmlns] = typing.get_args(Xmlns)[0]
"""The default value for the `xmlns` attribute."""
