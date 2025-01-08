import lark
import lark.visitors
from typing_extensions import Annotated, TypeAlias

from svglab import attrparse
from svglab.attrparse import utils


Points: TypeAlias = list[attrparse.Point]


@lark.v_args(inline=True)
class _Transformer(lark.Transformer[object, Points]):
    number = float
    point = attrparse.Point

    points = utils.v_args_to_list


PointsType: TypeAlias = Annotated[
    Points,
    utils.get_validator(grammar="points.lark", transformer=_Transformer()),
]
