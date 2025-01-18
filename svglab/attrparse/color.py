import re

import pydantic_extra_types.color
from typing_extensions import TypeAlias, override

from svglab import serialize


def _alpha_channel_as_percentage(original: str) -> str:
    """Convert the alpha channel to a percentage.

    Args:
        original: The original color string. Must be in the format
            `func(r, g, b, a)`, where `a` is a float.

    Returns:
        The color string with the alpha channel as a percentage.

    Examples:
        >>> _alpha_channel_as_percentage("rgba(0, 0, 0, 0.5)")
        'rgba(0, 0, 0, 50%)'
        >>> _alpha_channel_as_percentage("hsla(0, 0%, 0%, 0.75)")
        'hsla(0, 0%, 0%, 75%)'

    """
    func, args, *_ = re.split(r"[\(\)]", original)

    values = args.split(", ")
    values[-1] = f"{float(values[-1]):0.0%}"

    return f"{func}({', '.join(values)})"


class Color(
    pydantic_extra_types.color.Color, serialize.CustomSerializable
):
    @override
    def as_rgb(
        self, *, alpha_channel: serialize.AlphaChannelMode = "float"
    ) -> str:
        result = super().as_rgb()

        if self._rgba.alpha is not None and alpha_channel == "percentage":
            result = _alpha_channel_as_percentage(result)

        return result

    @override
    def as_hsl(
        self, *, alpha_channel: serialize.AlphaChannelMode = "float"
    ) -> str:
        result = super().as_hsl()

        if self._rgba.alpha is not None and alpha_channel == "percentage":
            result = _alpha_channel_as_percentage(result)

        return result

    @override
    def serialize(self) -> str:
        formatter = serialize.get_current_formatter()
        result: str

        match formatter.color_mode:
            case "original":
                original = self.original()

                if isinstance(original, str):
                    result = original
                else:
                    result = self.as_named(fallback=True)
            case "auto":
                result = super().__str__()
            case "named":
                result = self.as_named(fallback=True)
            case "hex-short":
                result = self.as_hex(format="short")
            case "hex-long":
                result = self.as_hex(format="long")
            case "rgb":
                result = self.as_rgb(alpha_channel=formatter.alpha_channel)
            case "hsl":
                result = self.as_hsl(alpha_channel=formatter.alpha_channel)

        return result

    @override
    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.original()!r})"


ColorType: TypeAlias = Color
