from typing import TypeAlias

import pydantic_extra_types.color

from svglab import serialize

__all__ = ["Color", "ColorType"]


class Color(pydantic_extra_types.color.Color):
    def __str__(self) -> str:
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
                result = self.as_rgb()
            case "hsl":
                result = self.as_hsl()

        return result

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.original()!r})"


ColorType: TypeAlias = Color
