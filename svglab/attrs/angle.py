from __future__ import annotations

from typing import Annotated, Literal, TypeAlias

import lark
import pydantic
from typing_extensions import override

from svglab import serialize
from svglab.attrs import utils


AngleUnit: TypeAlias = Literal["deg", "grad", "rad"]


@pydantic.dataclasses.dataclass
class Angle(serialize.CustomSerializable):
    """Represents the SVG `<angle>` type.

    An angle is a number optionally followed by a unit. Available units are:

    - `deg`: degrees
    - `grad`: gradians
    - `rad`: radians
    """

    value: float
    unit: AngleUnit | None = "deg"

    @override
    def serialize(self) -> str:
        value = serialize.serialize(self.value)
        return f"{value}{self.unit or ''}"


@lark.v_args(inline=True)
class _Transformer(lark.Transformer[object, Angle]):
    number = float
    angle = Angle


AngleType: TypeAlias = Annotated[
    Angle,
    utils.get_validator(grammar="angle.lark", transformer=_Transformer()),
]
