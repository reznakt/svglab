import copy
import uuid
from collections.abc import Iterator

import PIL.Image
import pydantic
import typing_extensions
from typing_extensions import (
    Protocol,
    TypeAlias,
    TypeVar,
    runtime_checkable,
)

from svglab import utils
from svglab.attrparse import point
from svglab.elements import common


_TagT = TypeVar("_TagT", bound=common.Tag)
_SvgTag: TypeAlias = common.PairedTag


@runtime_checkable
class _SupportsRender(Protocol):
    def render(self) -> PIL.Image.Image: ...


@pydantic.dataclasses.dataclass(frozen=True)
class BBox:
    x_min: pydantic.NonNegativeInt
    y_min: pydantic.NonNegativeInt
    x_max: pydantic.NonNegativeInt
    y_max: pydantic.NonNegativeInt

    def as_tuple(self) -> tuple[int, int, int, int]:
        return self.x_min, self.y_min, self.x_max, self.y_max

    def as_rect(self) -> typing_extensions.Tuple[point.Point, point.Point]:
        return point.Point(self.x_min, self.y_min), point.Point(
            self.x_max, self.y_max
        )

    def __iter__(self) -> Iterator[int]:
        return iter(self.as_tuple())


def _copy_tree(tag: _TagT) -> tuple[_TagT, _SvgTag]:
    svg = utils.take_last(tag.parents)

    # type(svg) -> tags.Svg
    assert isinstance(svg, _SvgTag)

    original_id = tag.id
    tag.id = uuid.uuid4().hex

    try:
        svg = copy.deepcopy(svg)

        candidates = svg.find_all(type(tag))

        this = next(tag for tag in candidates if tag.id == tag.id)
    finally:
        tag.id = original_id

    return this, svg


def _bbox_render(tag: common.Tag) -> PIL.Image.Image:
    tag_copy, svg = _copy_tree(tag)

    for t in svg.find_all():
        t.visibility = "hidden"

    tag_copy.visibility = "visible"

    assert isinstance(svg, _SupportsRender)
    return svg.render()


def bbox(tag: common.Tag) -> BBox | None:
    img = _bbox_render(tag)
    bbox = img.getbbox()

    if bbox is None:
        return None

    x_min, y_min, x_max, y_max = bbox

    return BBox(x_min, y_min, x_max, y_max)
