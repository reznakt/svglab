from typing_extensions import override


class SvgError(Exception):
    """Base class for exceptions in this package."""


class SvgElementNotFoundError(SvgError):
    """Exception raised by methods that search the element tree."""


class SvgPathError(SvgError):
    """Exception raised by methods that manipulate paths."""


class SvgPathMissingMoveToError(SvgPathError):
    """Exception raised when a path does not start with a MoveTo command."""

    @override
    def __init__(self) -> None:
        super().__init__("Path must start with a MoveTo command")


class SvgUnitConversionError(SvgError):
    """Exception raised when a unit conversion fails."""

    @override
    def __init__(
        self, *, original_unit: object, target_unit: object
    ) -> None:
        super().__init__(
            f"Unable to convert {original_unit!r} to {target_unit!r}"
        )
