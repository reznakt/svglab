"""Mathematical utility functions."""

import math

from typing_extensions import Literal, SupportsFloat, SupportsIndex
from useful_types import SupportsRichComparisonT

from svglab import constants


def is_close(
    a: SupportsFloat | SupportsIndex, b: SupportsFloat | SupportsIndex, /
) -> bool:
    """Check if two floating-point numbers are almost equal.

    Args:
        a: The first number to compare.
        b: The second number to compare.

    Returns:
        `True` if the two numbers are almost equal, `False` otherwise.

    Examples:
        import math
        >>> is_close(1.0, 1.0)
        True
        >>> is_close(1.0, 1.0 + 1e-20)
        True
        >>> is_close(1.0, 1.0 + 0.001)
        False
        >>> is_close(0, math.sin(math.pi))
        True

    """
    return math.isclose(
        a,
        b,
        rel_tol=constants.FLOAT_RELATIVE_TOLERANCE,
        abs_tol=constants.FLOAT_ABSOLUTE_TOLERANCE,
    )


def clamp(
    value: SupportsRichComparisonT,
    /,
    *,
    min_value: SupportsRichComparisonT,
    max_value: SupportsRichComparisonT,
) -> SupportsRichComparisonT:
    """Clamp a value between two bounds.

    Args:
        value: The value to clamp.
        min_value: The minimum value.
        max_value: The maximum value.

    Returns:
        The clamped value. If `value` is less than `min_value`, `min_value` is
        returned. If `value` is greater than `max_value`, `max_value` is
        returned. Otherwise, `value` is returned.

    Examples:
        >>> clamp(5, min_value=0, max_value=10)
        5
        >>> clamp(-5, min_value=0, max_value=10)
        0
        >>> clamp(15, min_value=0, max_value=10)
        10

    """
    return max(min(value, max_value), min_value)


def signum(x: float) -> Literal[-1, 0, 1]:
    """Compute the signum function `sgn(x)`.

    Args:
        x: The value to compute the signum of.

    Returns:
        -1 if the value is negative, 0 if the value is zero, and 1 if the value
        is positive.

    Examples:
        >>> signum(-5)
        -1
        >>> signum(0)
        0
        >>> signum(0.5)
        1

    """
    if x < 0:
        return -1

    return 1 if x > 0 else 0


def arccos(value: float) -> float:
    """Compute the arccosine of a value in degrees.

    This function is a wrapper around `math.acos` that returns "nice" values
    for common inputs. The output is in degrees.

    Args:
        value: The value to compute the arccosine of.

    Returns:
        The arccosine of the value in degrees.

    Examples:
        >>> arccos(1)
        0
        >>> arccos(0)
        90

    """
    match value:
        case 1:
            return 0
        case 0:
            return 90
        case _:
            return math.degrees(math.acos(value))


def degrees(radians: float) -> float:
    """Convert radians to degrees, returning a value in the range (-180, 180].

    Args:
        radians: The angle in radians.

    Returns:
        The angle in degrees in the range (-180, 180].

    Examples:
        >>> from math import pi
        >>> degrees(0)
        0.0
        >>> degrees(pi)
        180.0
        >>> degrees(2 * pi)
        0.0
        >>> degrees(-pi / 2)
        -90.0
        >>> degrees(-pi)
        180.0

    """
    deg = math.degrees(radians)
    normalized = ((deg + 180) % 360) - 180

    return 180.0 if is_close(normalized, -180) else normalized


def arctan(value: float) -> float:
    """Compute the arctangent of a value in degrees.

    This function is a wrapper around `math.atan` that returns "nice" values
    for common inputs. The output is in degrees.

    Args:
        value: The value to compute the arctangent of.

    Returns:
        The arctangent of the value in degrees.

    Examples:
        >>> arctan(0)
        0
        >>> arctan(1)
        45

    """
    match value:
        case 0:
            return 0
        case 1:
            return 45
        case -1:
            return -45
        case _:
            return math.degrees(math.atan(value))


def tan(degrees: float) -> float:
    """Compute the tangent of an angle in degrees.

    This function is a wrapper around `math.tan` that takes an angle in degrees
    and returns "nice" values for common angles.

    Args:
        degrees: The angle in degrees.

    Returns:
        The tangent of the angle.

    Examples:
        >>> tan(0)
        0
        >>> tan(45)
        1

    """
    degrees %= 180

    match degrees:
        case 0:
            return 0
        case 45:
            return 1
        case 135:
            return -1
        case _:
            return math.tan(math.radians(degrees))
