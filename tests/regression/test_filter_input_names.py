import pytest
from typing_extensions import Literal

from svglab import FeComposite, Formatter, parse_svg


@pytest.mark.parametrize("name", ["add", "red", "SourceGraphic"])
@pytest.mark.parametrize("color_mode", ["auto", "hex-long", "rgb"])
def test_filter_input_names_are_kept_verbatim(
    name: str, color_mode: Literal["auto", "hex-long", "rgb"]
) -> None:
    svg = parse_svg(f"""
        <svg>
            <filter>
                <feComposite in="{name}" in2="{name}"/>
            </filter>
        </svg>
    """)
    formatter = Formatter(color_mode=color_mode)

    output = svg.find(FeComposite).to_xml(formatter=formatter)

    assert f'in="{name}"' in output
    assert f'in2="{name}"' in output
