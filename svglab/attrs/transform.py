from typing import Annotated, TypeAlias, cast, final, overload

import lark
import pydantic
from typing_extensions import Self, override

from svglab import serialize
from svglab.attrs import utils


@final
@pydantic.dataclasses.dataclass
class Translate(serialize.CustomSerializable):
    x: float
    y: float | None = None

    @override
    def serialize(self) -> str:
        x = serialize.serialize(self.x)

        if self.y is None:
            return f"translate({x})"

        y = serialize.serialize(self.y)

        return f"translate({x}, {y})"


@final
@pydantic.dataclasses.dataclass
class Scale(serialize.CustomSerializable):
    x: float
    y: float | None = None

    @override
    def serialize(self) -> str:
        x = serialize.serialize(self.x)

        if self.y is None:
            return f"scale({x})"

        y = serialize.serialize(self.y)

        return f"scale({x}, {y})"


@pydantic.dataclasses.dataclass
class _Rotate(serialize.CustomSerializable):
    angle: float
    cx: float | None
    cy: float | None

    @pydantic.model_validator(mode="after")
    def __check_cx_cy(self) -> Self:  # pyright: ignore[reportUnusedFunction]
        cx_is_none = self.cx is None
        cy_is_none = self.cy is None

        if cx_is_none != cy_is_none:
            raise ValueError(
                "Both cx and cy must either be provided or omitted"
            )

        return self

    @override
    def serialize(self) -> str:
        angle = serialize.serialize(self.angle)

        if self.cx is None:
            return f"rotate({angle})"

        cx, cy = serialize.serialize(self.cx, cast(float, self.cy))

        return f"rotate({angle} {cx} {cy})"


class Rotate(_Rotate):
    @overload
    def __init__(self, angle: float, /) -> None: ...

    @overload
    def __init__(self, angle: float, /, cx: float, cy: float) -> None: ...

    def __init__(
        self,
        angle: float,
        /,
        cx: float | None = None,
        cy: float | None = None,
    ) -> None:
        super().__init__(angle=angle, cx=cx, cy=cy)


@final
@pydantic.dataclasses.dataclass
class SkewX(serialize.CustomSerializable):
    angle: float

    @override
    def serialize(self) -> str:
        angle = serialize.serialize(self.angle)

        return f"skewX({angle})"


@final
@pydantic.dataclasses.dataclass
class SkewY(serialize.CustomSerializable):
    angle: float

    @override
    def serialize(self) -> str:
        angle = serialize.serialize(self.angle)

        return f"skewY({angle})"


@final
@pydantic.dataclasses.dataclass
class Matrix(serialize.CustomSerializable):
    a: float
    b: float
    c: float
    d: float
    e: float
    f: float

    @override
    def serialize(self) -> str:
        a, b, c, d, e, f = serialize.serialize(
            self.a, self.b, self.c, self.d, self.e, self.f
        )

        return f"matrix({a} {b} {c} {d} {e} {f})"


TransformAction: TypeAlias = (
    Translate | Scale | Rotate | SkewX | SkewY | Matrix
)

Transform: TypeAlias = list[TransformAction]


@lark.v_args(inline=True)
class _Transformer(lark.Transformer[object, Transform]):
    number = float

    translate = Translate
    scale = Scale
    rotate = Rotate
    skew_x = SkewX
    skew_y = SkewY
    matrix = Matrix

    transform_ = utils.v_args_to_list


TransformType: TypeAlias = Annotated[
    Transform,
    utils.get_validator(
        grammar="transform.lark", transformer=_Transformer()
    ),
]
