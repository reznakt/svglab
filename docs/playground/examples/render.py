"""Measure an element and render the document to pixels."""

from svglab import Circle, parse_svg


svg = parse_svg("""
<svg width="180" height="120" xmlns="http://www.w3.org/2000/svg">
    <rect width="180" height="120" fill="#eceff1"/>
    <circle cx="70" cy="60" r="42" fill="#3f51b5" opacity="0.75"/>
    <circle cx="110" cy="60" r="42" fill="#e91e63" opacity="0.75"/>
</svg>
""")

circle = svg.find(Circle)

print("bounding box:  ", circle.get_bbox())
print("pixels covered:", circle.get_mask().sum())
print("pixels visible:", circle.get_mask(visible_only=True).sum())

# an image on the last line is displayed below the output
svg.render()
