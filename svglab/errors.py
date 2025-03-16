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


class SvgReifyError(SvgError):
    """Exception raised when an element cannot be reified."""

    @override
    def __init__(self) -> None:
        super().__init__("Cannot reify transform list")


class SvgTransformSwapError(SvgError):
    """Exception raised when two transformations cannot be swapped."""

    @override
    def __init__(self, transform_a: object, transform_b: object) -> None:
        super().__init__(
            f"Cannot swap {transform_a!r} and {transform_b!r}"
        )
