"""Definition of the SVG `<points>` type.

Use `Points` to represent points in SVG. Use `PointsType` in Pydantic fields.
"""

import lark
import lark.visitors
from typing_extensions import Annotated, TypeAlias

from svglab.attrparse import parse, point


Points: TypeAlias = list[point.Point]


@lark.v_args(inline=True)
class _Transformer(lark.Transformer[object, Points]):
    number = float
    point = point.Point

    points = parse.v_args_to_list


PointsType: TypeAlias = Annotated[
    Points,
    parse.get_validator(grammar="points.lark", transformer=_Transformer()),
]
