"""Parse a document, change an attribute and add an element.

Nothing is imported for you: write the imports you would write in a script.
"""

from svglab import Circle, Color, Length, Rect, parse_svg


svg = parse_svg("""
<svg width="100" height="100" xmlns="http://www.w3.org/2000/svg">
    <circle cx="50" cy="50" r="40" stroke="black" stroke-width="2"/>
</svg>
""")

circle = svg.find(Circle)
circle.fill = Color("red")

svg.add_child(
    Rect(x=Length(10), y=Length(10), width=Length(30), height=Length(30))
)

print(svg.to_xml())
