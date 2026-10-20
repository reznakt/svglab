import pytest

from svglab import parse_svg


@pytest.mark.parametrize("parser", ["html.parser", "lxml", "lxml-xml"])
def test_style_and_script_content_is_kept(parser: str) -> None:
    markup = "<svg><style>.a{fill:red}</style><script>let x</script></svg>"

    output = parse_svg(markup, parser=parser).to_xml(pretty=False)  # pyright: ignore[reportArgumentType]

    assert "<style>.a{fill:red}</style>" in output
    assert "<script>let x</script>" in output
