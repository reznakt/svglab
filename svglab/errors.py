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
