from typing import Annotated, TypeAlias

import lark
import pydantic
from typing_extensions import Self

from svglab.attrparse import utils

__all__ = [
    "Matrix",
    "Rotate",
    "Scale",
    "SkewX",
    "SkewY",
    "Transform",
    "TransformAction",
    "TransformType",
    "Translate",
]


@pydantic.dataclasses.dataclass
class Translate:
    x: float
    y: float | None = None

    def __str__(self) -> str:
        if self.y is None:
            return f"translate({self.x})"

        return f"translate({self.x}, {self.y})"


@pydantic.dataclasses.dataclass
class Scale:
    x: float
    y: float | None = None

    def __str__(self) -> str:
        if self.y is None:
            return f"scale({self.x})"

        return f"scale({self.x}, {self.y})"


@pydantic.dataclasses.dataclass
class Rotate:
    angle: float
    cx: float | None = None
    cy: float | None = None

    @pydantic.model_validator(mode="after")
    def __check_cx_cy(self) -> Self:
        cx_is_none = self.cx is None
        cy_is_none = self.cy is None

        if cx_is_none != cy_is_none:
            raise ValueError("Both cx and cy must either be provided or omitted")

        return self

    def __str__(self) -> str:
        if self.cx is None:
            return f"rotate({self.angle})"

        return f"rotate({self.angle} {self.cx} {self.cy})"


@pydantic.dataclasses.dataclass
class SkewX:
    angle: float

    def __str__(self) -> str:
        return f"skewX({self.angle})"


@pydantic.dataclasses.dataclass
class SkewY:
    angle: float

    def __str__(self) -> str:
        return f"skewY({self.angle})"


@pydantic.dataclasses.dataclass
class Matrix:
    a: float
    b: float
    c: float
    d: float
    e: float
    f: float

    def __str__(self) -> str:
        return f"matrix({self.a}, {self.b}, {self.c}, {self.d}, {self.e}, {self.f})"


TransformAction: TypeAlias = Translate | Scale | Rotate | SkewX | SkewY | Matrix
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
