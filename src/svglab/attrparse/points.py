"""Definition of the SVG `<points>` type.

Use `Points` to represent points in SVG. Use `PointsType` in Pydantic fields.
"""

import lark
from typing_extensions import Annotated, TypeAlias

from svglab.attrparse.parse import (
    FiniteFloat,
    get_validator,
    inline_args,
    v_args_to_list,
)
from svglab.attrparse.point import Point


Points: TypeAlias = list[Point]


@inline_args
class _Transformer(lark.Transformer[lark.Token, Points]):
    number = FiniteFloat
    point = Point

    points = v_args_to_list


PointsType: TypeAlias = Annotated[
    Points,
    get_validator(grammar="points.lark", transformer=_Transformer()),
]
