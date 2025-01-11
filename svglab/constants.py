import typing_extensions
from typing_extensions import Final, Literal, TypeAlias


Xmlns: TypeAlias = Literal["http://www.w3.org/2000/svg"]
"""Type representing valid values for the `xmlns` attribute."""

DEFAULT_XMLNS: Final[Xmlns] = typing_extensions.get_args(Xmlns)[0]
"""The default value for the `xmlns` attribute."""
