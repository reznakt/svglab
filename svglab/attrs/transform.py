from typing import Annotated, Generic, TypeAlias, TypeVar, cast, final

import lark
import pydantic
from typing_extensions import Self, override

from svglab import serialize
from svglab.attrs import utils

__all__ = [
    "Matrix",
    "Rotate",
    "RotateWithCenter",
    "RotateWithoutCenter",
    "Scale",
    "SkewX",
    "SkewY",
    "Transform",
    "TransformAction",
    "TransformType",
    "Translate",
]

_T_opt_float = TypeVar("_T_opt_float", float, None)


@final
@pydantic.dataclasses.dataclass
class Translate(serialize.Serializable):
    x: float
    y: float | None = None

    @override
    def serialize(self) -> str:
        x = serialize.format_number(self.x)

        if self.y is None:
            return f"translate({x})"

        y = serialize.format_number(self.y)

        return f"translate({x}, {y})"


@final
@pydantic.dataclasses.dataclass
class Scale(serialize.Serializable):
    x: float
    y: float | None = None

    @override
    def serialize(self) -> str:
        x = serialize.format_number(self.x)

        if self.y is None:
            return f"scale({x})"

        y = serialize.format_number(self.y)

        return f"scale({x}, {y})"


@pydantic.dataclasses.dataclass
class Rotate(serialize.Serializable, Generic[_T_opt_float]):
    angle: float
    cx: _T_opt_float = cast(_T_opt_float, None)
    cy: _T_opt_float = cast(_T_opt_float, None)

    @pydantic.model_validator(mode="after")
    def __check_cx_cy(self) -> Self:
        cx_is_none = self.cx is None
        cy_is_none = self.cy is None

        if cx_is_none != cy_is_none:
            raise ValueError("Both cx and cy must either be provided or omitted")

        return self

    @override
    def serialize(self) -> str:
        angle = serialize.format_number(self.angle)

        if self.cx is None:
            return f"rotate({angle})"

        cx, cy = serialize.format_number(self.cx, self.cy)

        return f"rotate({angle} {cx} {cy})"


@final
@pydantic.dataclasses.dataclass
class SkewX(serialize.Serializable):
    angle: float

    @override
    def serialize(self) -> str:
        angle = serialize.format_number(self.angle)

        return f"skewX({angle})"


@final
@pydantic.dataclasses.dataclass
class SkewY(serialize.Serializable):
    angle: float

    @override
    def serialize(self) -> str:
        angle = serialize.format_number(self.angle)

        return f"skewY({angle})"


@final
@pydantic.dataclasses.dataclass
class Matrix(serialize.Serializable):
    a: float
    b: float
    c: float
    d: float
    e: float
    f: float

    @override
    def serialize(self) -> str:
        a, b, c, d, e, f = map(
            serialize.format_number, (self.a, self.b, self.c, self.d, self.e, self.f)
        )

        return f"matrix({a} {b} {c} {d} {e} {f})"


RotateWithoutCenter: TypeAlias = Rotate[None]
RotateWithCenter: TypeAlias = Rotate[float]

TransformAction: TypeAlias = (
    Translate | Scale | RotateWithoutCenter | RotateWithCenter | SkewX | SkewY | Matrix
)

Transform: TypeAlias = list[TransformAction]


@lark.v_args(inline=True)
class Transformer(lark.Transformer[object, Transform]):
    number = float

    translate = Translate
    scale = Scale
    rotate = Rotate
    skew_x = SkewX
    skew_y = SkewY
    matrix = Matrix

    def start(self, *actions: TransformAction) -> Transform:
        return list(actions)


TransformType: TypeAlias = Annotated[
    Transform,
    utils.get_validator(grammar="transform", transformer=Transformer()),
]
