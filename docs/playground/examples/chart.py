"""Draw a bar chart from data, out of typed elements and nothing parsed."""

from svglab import Color, G, Length, Line, Rect, Svg, Translate


DATA = {"mon": 12, "tue": 19, "wed": 7, "thu": 22, "fri": 16, "sat": 3}

BAR = 28
GAP = 10
HEIGHT = 120
PADDING = 16

width = PADDING * 2 + len(DATA) * BAR + (len(DATA) - 1) * GAP
scale = (HEIGHT - PADDING * 2) / max(DATA.values())

chart = Svg(width=Length(width), height=Length(HEIGHT))
chart.add_child(
    Rect(width=Length(width), height=Length(HEIGHT), fill=Color("#fafafa"))
)

bars = G(transform=[Translate(PADDING, HEIGHT - PADDING)])

for index, value in enumerate(DATA.values()):
    bars.add_child(
        Rect(
            x=Length(index * (BAR + GAP)),
            y=Length(-value * scale),
            width=Length(BAR),
            height=Length(value * scale),
            rx=Length(3),
            fill=Color("#3f51b5"),
        )
    )

chart.add_child(bars)
chart.add_child(
    Line(
        x1=Length(PADDING),
        y1=Length(HEIGHT - PADDING),
        x2=Length(width - PADDING),
        y2=Length(HEIGHT - PADDING),
        stroke=Color("#9e9e9e"),
    )
)

# an image on the last line is displayed below the output
chart.render(zoom=3)
