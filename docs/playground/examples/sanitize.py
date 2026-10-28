"""Strip scripts, event handlers and outside references from a document.

SVG can carry scripts, so anything a user uploads has to be cleaned before
it is served back. The typed model makes that a walk over the tree rather
than a job for regular expressions.
"""

from svglab import Iri, Script, Style, parse_svg


svg = parse_svg("""
<svg width="100" height="100" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">
    <script>alert(document.cookie)</script>
    <style>@import url(https://evil.example/x.css);</style>
    <rect id="box" width="50" height="50" fill="red" onclick="steal()"/>
    <image href="https://evil.example/tracker.png" width="10" height="10"/>
    <a xlink:href="javascript:steal()"><circle cx="70" cy="70" r="20"/></a>
    <use href="#box" x="50"/>
</svg>
""")

# materialize first: the tree is modified while walking it
for element in list(svg.find_all(Script, Style)):
    if element.parent is not None:
        element.parent.remove_child(element)
        print("removed", type(element).__name__)

for element in svg.find_all():
    for name in type(element).model_fields:
        value = getattr(element, name, None)

        if value is None:
            continue

        # event handlers run script; references may leave the document
        if name.startswith("on") or (
            isinstance(value, Iri) and not value.is_local
        ):
            setattr(element, name, None)
            print("removed", f"{type(element).__name__}.{name}")

print()
print(svg.to_xml())
