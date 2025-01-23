import lark
import pydantic
from typing_extensions import (
    Annotated,
    Literal,
    Self,
    TypeAlias,
    final,
    overload,
    override,
)

from svglab import serialize
from svglab.attrparse import utils


_TransformFunctionName: TypeAlias = Literal[
    "translate", "scale", "rotate", "skewX", "skewY", "matrix"
]


def _serialize_transform_function(
    name: _TransformFunctionName, *args: serialize.Serializable | None
) -> str:
    args_str = serialize.serialize(arg for arg in args if arg is not None)

    return f"{name}({args_str})"


@final
@pydantic.dataclasses.dataclass
class Translate(serialize.CustomSerializable):
    x: float
    y: float | None = None

    @override
    def serialize(self) -> str:
        return _serialize_transform_function("translate", self.x, self.y)


@final
@pydantic.dataclasses.dataclass
class Scale(serialize.CustomSerializable):
    x: float
    y: float | None = None

    @override
    def serialize(self) -> str:
        return _serialize_transform_function("scale", self.x, self.y)


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
        return _serialize_transform_function(
            "rotate", self.angle, self.cx, self.cy
        )


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
        return _serialize_transform_function("skewX", self.angle)


@final
@pydantic.dataclasses.dataclass
class SkewY(serialize.CustomSerializable):
    angle: float

    @override
    def serialize(self) -> str:
        return _serialize_transform_function("skewY", self.angle)


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
        return _serialize_transform_function(
            "matrix", self.a, self.b, self.c, self.d, self.e, self.f
        )


TransformFunction: TypeAlias = (
    Translate | Scale | Rotate | SkewX | SkewY | Matrix
)

Transform: TypeAlias = list[TransformFunction]


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
