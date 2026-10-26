"""Build path data, transform it, and turn a shape into a path.

Path data is a typed sequence of commands, so it can be inspected and
transformed like any other Python object.
"""

from svglab import Length, Path, PathData, Point, Rect, Scale, Translate


d = (
    PathData()
    .move_to(Point(0, 0))
    .line_to(Point(100, 0))
    .quadratic_bezier_to(Point(150, 50), Point(100, 100))
    .close()
)

for command in d:
    print(command)

print()
print("as written: ", Path(d=d).to_xml())
print("scaled by 2:", Path(d=Scale(2) @ d).to_xml())
print("moved by 10:", Path(d=Translate(10, 10) @ d).to_xml())

rect = Rect(width=Length(30), height=Length(20))
print("rect:       ", rect.to_path().to_xml())
