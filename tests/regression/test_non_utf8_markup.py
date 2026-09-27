import pytest

import svglab


def test_non_utf8_markup_that_is_not_svg_raises_value_error() -> None:
    with pytest.raises(ValueError, match="Expected one <svg> element"):
        svglab.parse_svg("<html/>".encode("utf-16"))
