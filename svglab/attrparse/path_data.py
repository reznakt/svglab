"""Definition of the SVG `<path-data>` type.

Use `PathData` to represent path data in SVG. Use `PathDataType` in Pydantic
fields.
"""

from __future__ import annotations

import abc
import contextlib
from collections.abc import Generator, Iterable, MutableSequence

import lark
import pydantic
import pydantic_core
from typing_extensions import (
    Annotated,
    Final,
    Literal,
    Protocol,
    Self,
    SupportsIndex,
    TypeAlias,
    final,
    overload,
    override,
    runtime_checkable,
)

from svglab import errors, mixins, protocols, serialize
from svglab.attrparse import parse, point, transform
from svglab.utils import iterutils, miscutils


_Flag: TypeAlias = Literal["0", "1"]


@pydantic.dataclasses.dataclass
class _PathCommandBase:
    pass


@runtime_checkable
class _HasEnd(Protocol):
    end: point.Point


class _PhysicalPathCommand(
    _PathCommandBase,
    transform.PointAddSubWithTranslateRMatmul,
    metaclass=abc.ABCMeta,
):
    pass


@final
@pydantic.dataclasses.dataclass
class ClosePath(_PathCommandBase):
    """Close the current subpath (Z).

    The subpath is closed by drawing a straight line from the current
    point to current subpath's initial point.

    """


@pydantic.dataclasses.dataclass
class LineTo(_HasEnd, _PhysicalPathCommand):
    """Draw a line from the current point to the given end point (L)."""

    end: point.Point

    def __rmatmul__(self, other: transform.TransformFunction) -> Self:
        return type(self)(end=other @ self.end)


@final
@pydantic.dataclasses.dataclass
class HorizontalLineTo(_PhysicalPathCommand):
    """Draw a horizontal line from the current point (H)."""

    x: float

    def to_line(self) -> LineTo:
        """Convert to a `LineTo` instance."""
        return LineTo(end=point.Point(self.x, 0))

    @overload
    def __rmatmul__(
        self, other: transform.Translate | transform.Scale
    ) -> Self: ...

    @overload
    def __rmatmul__(self, other: transform.TransformFunction) -> Self: ...

    @override
    def __rmatmul__(
        self, other: transform.TransformFunction
    ) -> Self | LineTo:
        if isinstance(other, transform.Translate | transform.Scale):
            x, _ = other @ point.Point(self.x, 0)

            return type(self)(x=x)

        return other @ self.to_line()


@final
@pydantic.dataclasses.dataclass
class VerticalLineTo(_PhysicalPathCommand):
    """Draw a vertical line from the current point (V)."""

    y: float

    def to_line(self) -> LineTo:
        """Convert to a `LineTo` instance."""
        return LineTo(end=point.Point(0, self.y))

    @overload
    def __rmatmul__(
        self, other: transform.Translate | transform.Scale
    ) -> Self: ...

    @overload
    def __rmatmul__(self, other: transform.TransformFunction) -> Self: ...

    @override
    def __rmatmul__(
        self, other: transform.TransformFunction
    ) -> Self | LineTo:
        if isinstance(other, transform.Translate | transform.Scale):
            _, y = other @ point.Point(0, self.y)

            return type(self)(y=y)

        return other @ self.to_line()


@final
@pydantic.dataclasses.dataclass
class SmoothQuadraticBezierTo(_HasEnd, _PhysicalPathCommand):
    """Draw a smooth/shorthand quadratic Bézier curve (T).

    The curve is drawn from the current point to the end point. The control
    point is calculated based on the previous command as a reflection of the
    previous control point across the end point of the previous command.
    """

    end: point.Point

    def __rmatmul__(self, other: transform.TransformFunction) -> Self:
        return type(self)(end=other @ self.end)


@final
@pydantic.dataclasses.dataclass
class SmoothCubicBezierTo(_HasEnd, _PhysicalPathCommand):
    """Draw a smooth/shorthand cubic Bézier curve (S).

    The curve is drawn from the current point to the end point. The first
    control point is calculated based on the previous command as a reflection
    of the second control point of the previous command across the end point
    of the previous command. The second control point is given as an argument.
    """

    control2: point.Point
    end: point.Point

    def __rmatmul__(self, other: transform.TransformFunction) -> Self:
        return type(self)(
            control2=other @ self.control2, end=other @ self.end
        )


@final
@pydantic.dataclasses.dataclass
class MoveTo(_HasEnd, _PhysicalPathCommand):
    """Move the current point to the end point and start a new subpath (M)."""

    end: point.Point

    def __rmatmul__(self, other: transform.TransformFunction) -> Self:
        return type(self)(end=other @ self.end)


@final
@pydantic.dataclasses.dataclass
class QuadraticBezierTo(_HasEnd, _PhysicalPathCommand):
    """Draw a quadratic Bézier curve (Q).

    The curve is drawn from the current point to the end point using `control`
    as the control point.
    """

    control: point.Point
    end: point.Point

    def __rmatmul__(self, other: transform.TransformFunction) -> Self:
        return type(self)(
            control=other @ self.control, end=other @ self.end
        )


@final
@pydantic.dataclasses.dataclass
class CubicBezierTo(_HasEnd, _PhysicalPathCommand):
    """Draw a cubic Bézier curve (C).

    The curve is drawn from the current point to the end point using
    `control1` and `control2` as the control points.
    """

    control1: point.Point
    control2: point.Point
    end: point.Point

    def __rmatmul__(self, other: transform.TransformFunction) -> Self:
        return type(self)(
            control1=other @ self.control1,
            control2=other @ self.control2,
            end=other @ self.end,
        )


@final
@pydantic.dataclasses.dataclass
class ArcTo(_HasEnd, _PhysicalPathCommand):
    """Draw an elliptical arc (A).

    The arc is drawn from the current point to the end point using the
    following parameters:
    - `radii`: The radii of the arc.
    - `angle`: The x-axis rotation angle in degrees.
    - `large`: A flag indicating whether the arc is large or small.
    - `sweep`: A flag indicating whether the arc is drawn in a positive or
    negative angle direction.
    """

    radii: point.Point
    angle: float
    large: bool
    sweep: bool
    end: point.Point

    def __rmatmul__(self, other: transform.TransformFunction) -> Self:
        radii = self.radii
        angle = self.angle
        end = self.end

        match other:
            case transform.Translate():
                end = other @ end
            case transform.Scale():
                radii = other @ radii
                end = other @ end
            case transform.Rotate(a):
                angle += a
            case _:
                msg = f"Unsupported transform: {other}"
                raise NotImplementedError(msg)

        return type(self)(
            radii=radii,
            angle=angle,
            large=self.large,
            sweep=self.sweep,
            end=end,
        )


PathCommand: TypeAlias = (
    ArcTo
    | ClosePath
    | CubicBezierTo
    | HorizontalLineTo
    | LineTo
    | MoveTo
    | QuadraticBezierTo
    | SmoothCubicBezierTo
    | SmoothQuadraticBezierTo
    | VerticalLineTo
)


def _get_current_subpath(
    path_data: PathData, command: PathCommand
) -> PathData:
    """Get the subpath that contains the given command.

    The command is searched for by reference, not by value.

    Args:
        path_data: The path containing the command.
        command: The command to find the subpath of.

    Returns:
        The subpath that contains the command.

    Raises:
        ValueError: If the command is not found in any subpath.

    Examples:
    >>> pd = PathData.from_str("M 0,0 L 1,1")
    >>> cmd = pd[0]
    >>> _get_current_subpath(pd, cmd)
    PathData(MoveTo(end=Point(x=0.0, y=0.0)), LineTo(end=Point(x=1.0, y=1.0)))
    >>> pd = PathData()
    >>> cmd = ClosePath()
    >>> _get_current_subpath(pd, cmd)
    Traceback (most recent call last):
        ...
    ValueError: Command not found in any subpath

    """
    for subpath in path_data.subpaths():
        for cmd in subpath:
            if cmd is command:
                return subpath

    raise ValueError("Command not found in any subpath")


def _get_end(path_data: PathData, command: PathCommand) -> point.Point:
    """Get the end point of a path command.

    For commands that have a set end point, this function returns the end
    point. For commands that do not have a set end point, this function
    calculates the end point based on command-specific logic.

    Args:
        path_data: The path containing the command.
        command: The command to get the end point of.

    Returns:
        The end point of the command.

    Examples:
    >>> path_data = PathData.from_str("M 10,10 H 100 V 100 Z")
    >>> _get_end(path_data, path_data[0])
    Point(x=10.0, y=10.0)
    >>> _get_end(path_data, path_data[1])
    Point(x=100.0, y=10.0)

    """
    match command:
        case ClosePath():
            current_subpath = _get_current_subpath(path_data, command)
            return _get_end(path_data, current_subpath[0])
        case HorizontalLineTo(x=x):
            end = _get_end(path_data, iterutils.prev(path_data, command))
            return point.Point(x, end.y)
        case VerticalLineTo(y=y):
            end = _get_end(path_data, iterutils.prev(path_data, command))
            return point.Point(end.x, y)
        case _:
            return command.end


def _quadratic_control(
    path_data: PathData, command: SmoothQuadraticBezierTo
) -> point.Point:
    """Compute the control point for a smooth quadratic Bézier command (`T`).

    The control point is calculated based on the previous command. If the
    previous command is a quadratic Bézier command (`Q`), the control point
    is the reflection of the previous control point across the end point of
    the previous command. If the previous command is of any other type, the
    control point is coincident with the end point of the previous command.

    Args:
        path_data: The path containing the command.
        command: The smooth quadratic Bézier command.

    Returns:
        The control point for the command.

    Examples:
    >>> path_data = PathData.from_str("M 0,0 Q 20,0 20,20 T 40,40")
    >>> _quadratic_control(path_data, path_data[2])
    Point(x=20.0, y=40.0)

    """
    prev = iterutils.prev(path_data, command)
    end = _get_end(path_data, prev)

    match prev:
        case QuadraticBezierTo(control=control):
            pass
        case SmoothQuadraticBezierTo():
            control = _quadratic_control(path_data, prev)
        case _:
            return end

    return control.line_reflect(end)


def _cubic_control(
    path_data: PathData, command: SmoothCubicBezierTo
) -> point.Point:
    """Compute the first control point for a smooth cubic Bézier command (`S`).

    The control point is calculated based on the previous command. If the
    previous command is a cubic Bézier command (`C`), the control point is the
    reflection of the second control point of the previous command across the
    end point of the previous command. If the previous command is of any other
    type, the control point is coincident with the end point of the previous
    command.

    Args:
        path_data: The path containing the command.
        command: The smooth cubic Bézier command.

    Returns:
        The first control point for the command.

    Examples:
    >>> path_data = PathData.from_str(
    ...     "M 0,0 C 20,0 20,20 40,40 S 100,100 50,50"
    ... )
    >>> _cubic_control(path_data, path_data[2])
    Point(x=60.0, y=60.0)

    """
    prev = iterutils.prev(path_data, command)
    end = _get_end(path_data, prev)

    if isinstance(prev, CubicBezierTo | SmoothCubicBezierTo):
        return prev.control2.line_reflect(end)

    return end


def _relativize(path_data: PathData) -> PathData:
    """Recompute the coordinates of path commands as if they were relative.

    This function takes a path and recomputes the coordinates of the path
    commands as if they were relative. This is done by subtracting the
    current position from the coordinates of each command. The resuting path
    may be used for serialization with relative coordinates.

    Args:
        path_data: The path to relativize.

    Returns:
        A new `PathData` instance with the coordinates of the path commands
        recomputed as if they were relative.

    Examples:
    >>> path_data = PathData.from_str("M 10,10")
    >>> _relativize(path_data)
    PathData(MoveTo(end=Point(x=10.0, y=10.0)))

    """
    result = PathData()
    pos = point.Point.zero()

    for command in path_data:
        if isinstance(command, _PhysicalPathCommand):
            result.append(command - pos)
        else:
            result.append(command)

        pos = _get_end(path_data, command)

    return result


def _can_use_implicit_command(
    current: PathCommand, /, *, prev: PathCommand | None
) -> bool:
    """Determine whether a command can be serialized implicitly.

    A command can be serialized implicitly if the previous command is of the
    same type as the current command, or if the previous command is a `MoveTo`
    command and the current command is a `LineTo` command.

    Args:
        prev: The previous command.
        current: The current command.

    Returns:
        `True` if the command can be serialized implicitly, `False` otherwise.

    Examples:
    >>> _can_use_implicit_command(MoveTo(point.Point(10, 10)), prev=None)
    False
    >>> _can_use_implicit_command(
    ...     LineTo(point.Point(100, 100)), prev=MoveTo(point.Point(10, 10))
    ... )
    True
    >>> _can_use_implicit_command(
    ...     LineTo(point.Point(100, 100)), prev=LineTo(point.Point(10, 10))
    ... )
    True

    """
    return type(prev) is type(current) or (
        isinstance(prev, MoveTo) and isinstance(current, LineTo)
    )


def _add_command(
    path_data: PathData, command: PathCommand, *, relative: bool = False
) -> None:
    if relative and isinstance(command, _PhysicalPathCommand):
        # if there is no previous command, just do nothing
        with contextlib.suppress(IndexError):
            command += _get_end(path_data, path_data[-1])

    path_data.append(command)


@final
class PathData(
    MutableSequence[PathCommand],
    mixins.CustomModel,
    transform.PointAddSubWithTranslateRMatmul,
    protocols.CustomSerializable,
):
    """A class representing the `d` attribute of a path element.

    The `d` attribute is used to define a path in SVG. This class provides
    methods for building a path by adding commands. `PathData` is also
    a `MutableSequence` of `PathCommand` instances.

    Args:
        iterable: An iterable of `PathCommand` instances (for example,
        another `PathData` instance).
        start: The starting point of the path. If `start` is not `None`, a
        `MoveTo` command is automatically added to the path, moving the "pen"
        to the starting point.

    Examples:
    >>> path_data = (
    ...     PathData()
    ...     .move_to(point.Point(10, 10))
    ...     .line_to(point.Point(100, 100), relative=True)
    ... )
    >>> len(path_data)
    2
    >>> bool(path_data)
    True
    >>> path_data[0]
    MoveTo(end=Point(x=10.0, y=10.0))
    >>> path_data.pop()
    LineTo(end=Point(x=110.0, y=110.0))
    >>> path_data.close()
    PathData(MoveTo(end=Point(x=10.0, y=10.0)), ClosePath())

    """

    def __add(
        self, command: PathCommand, /, *, relative: bool = False
    ) -> Self:
        _add_command(self, command, relative=relative)

        return self

    def __init__(
        self,
        iterable: Iterable[PathCommand] = (),
        /,
        *,
        start: point.Point | None = None,
    ) -> None:
        """Initialize a new `PathData` instance.

        Args:
            iterable: An iterable of `PathCommand` instances (for example,
            another `PathData` instance).
            start: The starting point of the path. If `start` is not `None`,
            a `MoveTo` command is automatically added to the path, moving the
            "pen" to the starting point.

        """
        self.__commands: Final[list[PathCommand]] = []

        if start is not None:
            self.move_to(start)

        for command in iterable:
            self.__add(command)

    @override
    def insert(self, index: SupportsIndex, value: PathCommand) -> None:
        if iterutils.is_first_index(self, index) and not isinstance(
            value, MoveTo
        ):
            raise errors.SvgPathMissingMoveToError

        self.__commands.insert(index, value)

    def move_to(
        self, end: point.Point, /, *, relative: bool = False
    ) -> Self:
        """Move the current point to the end point and start a new subpath (M).

        Args:
            end: The end point of the move command.
            relative: Whether the coordinates are relative to the current
            point.

        Returns:
            A reference to the current `PathData` instance.

        """
        return self.__add(MoveTo(end=end), relative=relative)

    def line_to(
        self, end: point.Point, /, *, relative: bool = False
    ) -> Self:
        """Draw a line from the current point to the end point (L).

        Args:
            end: The end point of the line command.
            relative: Whether the coordinates are relative to the current
            point.

        Returns:
            A reference to the current `PathData` instance.

        """
        return self.__add(LineTo(end=end), relative=relative)

    def horizontal_line_to(
        self,
        x: protocols.SupportsFloatOrIndex,
        /,
        *,
        relative: bool = False,
    ) -> Self:
        """Draw a horizontal line from the current point (H).

        Args:
            x: The x-coordinate of the end point of the line command.
            relative: Whether the coordinates are relative to the current
            point.

        Returns:
            A reference to the current `PathData` instance.

        """
        return self.__add(HorizontalLineTo(x=float(x)), relative=relative)

    def vertical_line_to(
        self,
        y: protocols.SupportsFloatOrIndex,
        /,
        *,
        relative: bool = False,
    ) -> Self:
        """Draw a vertical line from the current point (V).

        Args:
            y: The y-coordinate of the end point of the line command.
            relative: Whether the coordinates are relative to the current
            point.

        Returns:
            A reference to the current `PathData` instance.

        """
        return self.__add(VerticalLineTo(y=float(y)), relative=relative)

    def quadratic_bezier_to(
        self,
        control: point.Point,
        end: point.Point,
        /,
        *,
        relative: bool = False,
    ) -> Self:
        """Draw a quadratic Bézier curve (Q).

        The curve is drawn from the current point to the end point using
        `control` as the control point.

        Args:
            control: The control point of the curve.
            end: The end point of the curve.
            relative: Whether the coordinates are relative to the current
            point.

        Returns:
            A reference to the current `PathData` instance.

        """
        return self.__add(
            QuadraticBezierTo(control=control, end=end), relative=relative
        )

    def cubic_bezier_to(
        self,
        control1: point.Point,
        control2: point.Point,
        end: point.Point,
        *,
        relative: bool = False,
    ) -> Self:
        """Draw a cubic Bézier curve (C).

        The curve is drawn from the current point to the end point using
        `control1` and `control2` as the control points.

        Args:
            control1: The first control point of the curve.
            control2: The second control point of the curve.
            end: The end point of the curve.
            relative: Whether the coordinates are relative to the current
            point.

        Returns:
            A reference to the current `PathData` instance.

        """
        return self.__add(
            CubicBezierTo(control1=control1, control2=control2, end=end),
            relative=relative,
        )

    def arc_to(
        self,
        radii: point.Point,
        angle: float,
        end: point.Point,
        *,
        large: bool,
        sweep: bool,
        relative: bool = False,
    ) -> Self:
        """Draw an elliptical arc (A).

        The arc is drawn from the current point to the end point.

        Args:
            radii: The radii of the arc.
            angle: The x-axis rotation angle in degrees.
            end: The end point of the arc.
            large: A flag indicating whether the arc is large or small.
            sweep: A flag indicating whether the arc is drawn in a positive or
            negative angle direction.
            relative: Whether the coordinates are relative to the current
            point.

        Returns:
            A reference to the current `PathData` instance.

        """
        return self.__add(
            ArcTo(
                radii=radii, angle=angle, large=large, sweep=sweep, end=end
            ),
            relative=relative,
        )

    def smooth_quadratic_bezier_to(
        self, end: point.Point, /, *, relative: bool = False
    ) -> Self:
        """Draw a smooth/shorthand quadratic Bézier curve (T).

        The curve is drawn from the current point to the end point. The
        control point is calculated based on the previous command as a
        reflection of the previous control point across the end point of the
        previous command.

        Args:
            end: The end point of the curve.
            relative: Whether the coordinates are relative to the current
            point.

        Returns:
            A reference to the current `PathData` instance.

        """
        return self.__add(
            SmoothQuadraticBezierTo(end=end), relative=relative
        )

    def subpaths(self) -> Generator[Self]:
        r"""Get all subpaths in the path.

        A subpath is a sequence of path commands that starts with a `MoveTo`
        command.

        Yields:
            Subpaths of the path as `PathData` instances. Each subpath is
            yielded as a separate instance.

        Examples:
        >>> pd = PathData()
        >>> list(pd.subpaths())
        []
        >>> _ = pd.move_to(point.Point(0, 0))
        >>> list(pd.subpaths())
        [PathData(MoveTo(end=Point(x=0.0, y=0.0)))]
        >>> _ = pd.move_to(point.Point(10, 10))
        >>> print(*pd.subpaths(), sep="\n")
        PathData(MoveTo(end=Point(x=0.0, y=0.0)))
        PathData(MoveTo(end=Point(x=10.0, y=10.0)))

        """
        subpath = type(self)()

        for command in self:
            if not subpath:
                subpath.append(command)
                continue

            match command:
                case MoveTo():
                    yield subpath
                    subpath = type(self)()
                    subpath.append(command)
                case ClosePath():
                    subpath.append(command)
                    yield subpath
                    subpath = type(self)()
                case _:
                    subpath.append(command)

        if subpath:
            yield subpath

    def smooth_cubic_bezier_to(
        self,
        control2: point.Point,
        end: point.Point,
        /,
        *,
        relative: bool = False,
    ) -> Self:
        """Draw a smooth/shorthand cubic Bézier curve (S).

        The curve is drawn from the current point to the end point. The first
        control point is calculated based on the previous command as a
        reflection of the second control point of the previous command across
        the end point of the previous command. The second control point is
        given as an argument.

        Args:
            control2: The second control point of the curve.
            end: The end point of the curve.
            relative: Whether the coordinates are relative to the current
            point.

        Returns:
            A reference to the current `PathData` instance.

        """
        return self.__add(
            SmoothCubicBezierTo(control2=control2, end=end),
            relative=relative,
        )

    def close(self) -> Self:
        """Close the current subpath (Z).

        The subpath is closed by drawing a straight line from the current
        point to the current subpath's initial point.

        Returns:
            A reference to the current `PathData` instance.

        """
        return self.__add(ClosePath())

    @classmethod
    def from_str(cls, text: str) -> Self:
        """Parse a string into a `PathData` instance.

        Args:
            text: The string to parse.

        Returns:
            A new `PathData` instance created from the parsed string.

        Raises:
            ValueError: If the string cannot be parsed into a valid `PathData`
            instance.

        Examples:
            >>> path_data = PathData.from_str("M 10,10 Z")
            >>> path_data
            PathData(MoveTo(end=Point(x=10.0, y=10.0)), ClosePath())

        """
        path_data = parse.parse(
            text, grammar="path_data.lark", transformer=_Transformer()
        )

        assert isinstance(path_data, cls), (
            f"Expected {cls}, got {type(path_data)}"
        )
        return path_data

    @classmethod
    def _validate(
        cls, value: object, info: pydantic_core.core_schema.ValidationInfo
    ) -> PathData:
        del info

        match value:
            case str():
                return cls.from_str(value)
            case PathData():
                return value
            case _:
                msg = f"Expected str or D, got {type(value)}"
                raise TypeError(msg)

    def __apply_shorthand_formatting(self) -> PathData:
        """Apply shorthand formatting based on the formatter settings."""
        formatter = serialize.get_current_formatter()
        line = formatter.path_data_shorthand_line_commands
        curve = formatter.path_data_shorthand_curve_commands

        path_data = self

        if "never" in (line, curve):
            path_data = path_data.resolve_shorthands(
                lines=line == "never", curves=curve == "never"
            )

        if "always" in (line, curve):
            path_data = path_data.apply_shorthands(
                lines=line == "always", curves=curve == "always"
            )

        return path_data

    def __serialize_commands(self) -> Generator[str]:
        formatter = serialize.get_current_formatter()
        path_data = self.__apply_shorthand_formatting()

        if formatter.path_data_coordinates == "relative":
            path_data = _relativize(path_data)

        for prev, command in iterutils.pairwise(path_data):
            implicit = (
                formatter.path_data_commands == "implicit"
                and _can_use_implicit_command(command, prev=prev)
            )

            match command:
                case MoveTo(end):
                    yield serialize.serialize_path_command(
                        end, char="M", implicit=implicit
                    )
                case LineTo(end):
                    yield serialize.serialize_path_command(
                        end, char="L", implicit=implicit
                    )
                case HorizontalLineTo(x):
                    yield serialize.serialize_path_command(
                        x, char="H", implicit=implicit
                    )
                case VerticalLineTo(y):
                    yield serialize.serialize_path_command(
                        y, char="V", implicit=implicit
                    )
                case QuadraticBezierTo(control, end):
                    yield serialize.serialize_path_command(
                        control, end, char="Q", implicit=implicit
                    )
                case SmoothQuadraticBezierTo(end):
                    yield serialize.serialize_path_command(
                        end, char="T", implicit=implicit
                    )
                case CubicBezierTo(control1, control2, end):
                    yield serialize.serialize_path_command(
                        control1,
                        control2,
                        end,
                        char="C",
                        implicit=implicit,
                    )
                case SmoothCubicBezierTo(control2, end):
                    yield serialize.serialize_path_command(
                        control2, end, char="S", implicit=implicit
                    )
                case ArcTo(radii, angle, large, sweep, end):
                    yield serialize.serialize_path_command(
                        radii,
                        angle,
                        large,
                        sweep,
                        end,
                        char="A",
                        implicit=implicit,
                    )
                case ClosePath():
                    yield serialize.serialize_path_command(
                        char="Z", implicit=implicit
                    )

    @override
    def serialize(self) -> str:
        return " ".join(self.__serialize_commands())

    def resolve_shorthands(
        self, *, lines: bool = True, curves: bool = True
    ) -> Self:
        """Resolve shorthand commands into their full-length equivalents.

        Args:
            lines: Whether to resolve shorthand line commands (`H`, `V`) into
            the full-length equivalent (`L`).
            curves: Whether to resolve shorthand curve commands (`S`, `T`) into
            the full-length equivalent (`C`, `Q`).

        Returns:
            A new `PathData` instance with the shorthand commands
            (`H`, `V`, `S`, `T`) replaced by their full-length equivalents
            (`L`, `C`, `Q`).

        Examples:
        >>> path_data = PathData.from_str("M 0,0")
        >>> path_data.resolve_shorthands()
        PathData(MoveTo(end=Point(x=0.0, y=0.0)))

        """
        path_data = type(self)()

        for command in self:
            match command:
                case SmoothQuadraticBezierTo(end=end) if curves:
                    control = _quadratic_control(self, command)
                    path_data.quadratic_bezier_to(control, end)
                case SmoothCubicBezierTo(control2=control2, end=end) if (
                    curves
                ):
                    control1 = _cubic_control(self, command)
                    path_data.cubic_bezier_to(control1, control2, end)
                case HorizontalLineTo(x=x) if lines:
                    end = _get_end(path_data, path_data[-1])
                    path_data.line_to(point.Point(x, end.y))
                case VerticalLineTo(y=y) if lines:
                    end = _get_end(path_data, path_data[-1])
                    path_data.line_to(point.Point(end.x, y))
                case _:
                    path_data.append(command)
        return path_data

    def apply_shorthands(
        self, *, lines: bool = True, curves: bool = True
    ) -> Self:
        """Convert full-length commands into shorthand commands where possible.

        Args:
            lines: Whether to convert line commands (`L`) to shorthand
            (`H`, `V`) where possible.
            curves: Whether to convert curve commands (`Q`, `C`) to shorthand
            (`T`, `S`) where possible.

        Returns:
            A new `PathData` instance with the full-length commands
            (`L`, `C`, `Q`) replaced by their shorthand equivalents
            (`H`, `V`, `S`, `T`).

        Examples:
        >>> path_data = PathData.from_str("M 10,10 L 100,10")
        >>> path_data.apply_shorthands()
        PathData(MoveTo(end=Point(x=10.0, y=10.0)), HorizontalLineTo(x=100.0))

        """
        path_data = type(self)()

        for command in self:
            match command:
                case LineTo(end=end) if lines and end.x == (
                    _get_end(path_data, path_data[-1]).x
                ):
                    path_data.vertical_line_to(end.y)
                case LineTo(end=end) if lines and end.y == (
                    _get_end(path_data, path_data[-1]).y
                ):
                    path_data.horizontal_line_to(end.x)
                case QuadraticBezierTo(control=control, end=end) if curves:
                    path_data.smooth_quadratic_bezier_to(end)

                    shorthand = path_data[-1]
                    assert isinstance(shorthand, SmoothQuadraticBezierTo)

                    # try to replace the command with a shorthand
                    auto_control = _quadratic_control(path_data, shorthand)

                    # if the shorthand turns out not to be compatible, revert
                    # to the original command
                    if control != auto_control:
                        path_data[-1] = command

                case CubicBezierTo(
                    control1=control1, control2=control2, end=end
                ) if curves:
                    path_data.smooth_cubic_bezier_to(control2, end)

                    shorthand = path_data[-1]
                    assert isinstance(shorthand, SmoothCubicBezierTo)

                    auto_control = _cubic_control(path_data, shorthand)

                    if control1 != auto_control:
                        path_data[-1] = command

                case _:
                    path_data.append(command)

        return path_data

    @overload
    def __getitem__(self, index: SupportsIndex) -> PathCommand: ...

    @overload
    def __getitem__(self, index: slice) -> Self: ...

    @override
    def __getitem__(
        self, index: SupportsIndex | slice
    ) -> PathCommand | Self:
        if isinstance(index, SupportsIndex):
            return self.__commands[index]

        return type(self)(self.__commands[index])

    @overload
    def __setitem__(
        self, index: SupportsIndex, values: PathCommand
    ) -> None: ...

    @overload
    def __setitem__(
        self, index: slice, values: Iterable[PathCommand]
    ) -> None: ...

    @override
    def __setitem__(
        self,
        index: SupportsIndex | slice,
        values: PathCommand | Iterable[PathCommand],
    ) -> None:
        if isinstance(index, slice):
            raise NotImplementedError(
                "__setitem__ with a slice is not supported"
            )

        assert isinstance(values, PathCommand)

        if iterutils.is_first_index(self, index) and not isinstance(
            values, MoveTo
        ):
            raise errors.SvgPathMissingMoveToError

        self.__commands[index] = values

    @overload
    def __delitem__(self, index: SupportsIndex) -> None: ...

    @overload
    def __delitem__(self, index: slice) -> None: ...

    @override
    def __delitem__(self, index: SupportsIndex | slice) -> None:
        if isinstance(index, slice):
            raise NotImplementedError(
                "__delitem__ with a slice is not supported"
            )

        if (
            iterutils.is_first_index(self, index)
            and len(self) > 1
            and not isinstance(self[int(index) + 1], MoveTo)
        ):
            raise errors.SvgPathMissingMoveToError

        del self.__commands[index]

    @override
    def __len__(self) -> int:
        return len(self.__commands)

    @override
    def __rmatmul__(self, other: transform.TransformFunction) -> Self:
        return type(self)(
            other @ command
            if isinstance(command, _PhysicalPathCommand)
            else command
            for command in self
        )

    @override
    def __eq__(self, other: object) -> bool:
        if not miscutils.basic_compare(other, self=self):
            return False

        if len(self) != len(other):
            return False

        return all(c1 == c2 for c1, c2 in zip(self, other, strict=True))

    @override
    def __repr__(self) -> str:
        name = type(self).__name__
        commands = ", ".join(repr(command) for command in self)
        return f"{name}({commands})"


@lark.v_args(inline=True)
@parse.visit_tokens  # there are a few terminals we want to parse
class _Transformer(lark.Transformer[object, PathData]):
    point = point.Point
    NUMBER = parse.FiniteFloat

    cubic_bezier = CubicBezierTo
    horizontal_line = HorizontalLineTo
    line = LineTo
    move = MoveTo
    quadratic_bezier = QuadraticBezierTo
    smooth_cubic_bezier = SmoothCubicBezierTo
    smooth_quadratic_bezier = SmoothQuadraticBezierTo
    vertical_line = VerticalLineTo
    z = ClosePath

    def FLAG(self, value: _Flag) -> bool:  # noqa: N802
        return value == "1"

    def arc(
        self,
        radii: point.Point,
        angle: float,
        large: bool,  # noqa: FBT001
        sweep: bool,  # noqa: FBT001
        end: point.Point,
    ) -> ArcTo:
        return ArcTo(
            radii=radii, angle=angle, large=large, sweep=sweep, end=end
        )

    @lark.v_args(inline=False)
    def path(
        self, args: list[PathCommand | lark.Tree[PathCommand | lark.Token]]
    ) -> PathData:
        path_data = PathData()

        for item in args:
            match item:
                # simple commands like `Z` require no further processing
                case _PathCommandBase() as command:
                    _add_command(path_data, command)
                # commands that are part of a group need to be extracted;
                # the relative flag is applied if the group is relative
                case lark.Tree(data=name, children=commands):
                    # sanity check for when the grammar changes
                    assert "relative" in name or "absolute" in name
                    relative = "relative" in name

                    for command in commands:
                        assert isinstance(command, PathCommand)
                        _add_command(path_data, command, relative=relative)

        return path_data


PathDataType: TypeAlias = Annotated[
    PathData,
    parse.get_validator(
        grammar="path_data.lark", transformer=_Transformer()
    ),
]
