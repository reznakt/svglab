class SvgError(Exception):
    """Base class for exceptions in this package."""


class SvgElementNotFoundError(SvgError):
    """Exception raised by methods that search the element tree."""
