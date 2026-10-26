"""Bake the transforms into the geometry, then write the result compactly."""

from svglab import Formatter, parse_svg


source = """
<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100">
  <g transform="translate(5, 5)">
    <rect x="10.000000" y="10.000000" width="80.000000" height="80.000000"
          fill="#ff0000" stroke="#000000" stroke-width="1.000000"/>
    <path d="M 20.000000 20.000000 L 80.000000 20.000000
             L 80.000000 80.000000 L 20.000000 80.000000 Z" fill="#0000ff"/>
  </g>
</svg>
""".strip()

svg = parse_svg(source)
svg.reify()

compact = Formatter(
    indent=0,
    general_precision=2,
    color_mode="hex-short",
    path_data_coordinates="relative",
    xmlns="never",
)
result = svg.to_xml(formatter=compact)

print(result)
print(f"{len(source)} B -> {len(result)} B")
