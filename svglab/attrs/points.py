from typing import Annotated, TypeAlias

import lark
import lark.visitors

from svglab import attrs
from svglab.attrs import utils


Points: TypeAlias = list[attrs.Point]


@lark.v_args(inline=True)
class _Transformer(lark.Transformer[object, Points]):
    number = float
    point = attrs.Point

    points = utils.v_args_to_list


PointsType: TypeAlias = Annotated[
    Points,
    utils.get_validator(grammar="points.lark", transformer=_Transformer()),
]
