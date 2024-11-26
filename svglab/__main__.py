#!/usr/bin/env python3

# ruff: noqa: T201

from sys import stdout

from svglab import CData, Comment, G, Rect, Svg, Text, parse_svg


def main() -> None:
    svg = parse_svg(
        """
        <svg xmlns="http://www.w3.org/2000/svg" foo="bar" viewBox="0 0 100 100">
            <g>
                <rect x="0" y="0" width="100" height="100"/>
                <!-- This is an example comment -->
                <![CDATA[foo { background-color: red; }]]>
                baz
                <g>
                    <rect id="foo"/>
                    <rect class="bar" />
                </g>
            </g>
        </svg>
    """
    )
    print(svg)

    svg2 = Svg(
        G()
        .add_child(Rect())
        .add_child(Comment("This is an example comment"))
        .add_child(CData("foo { background-color: red; }"))
        .add_child(Text("baz"))
        .add_child(G().add_child(Rect()).add_child(Rect()))
    )
    print(svg2)

    svg3 = Svg(
        G(
            Rect(),
            Comment("This is an example comment"),
            CData("foo { background-color: red; }"),
            Text("baz"),
            G(Rect(), Rect()),
        )
    )
    print(svg3)

    print(svg2 == svg3)
    print(len(svg.children))

    print(svg["g>g>rect"])
    print(svg["rect#foo"])
    print(svg["rect.bar"])

    svg.save(stdout, indent=4)

    print(svg.xmlns)
    svg.xmlns = "http://example.com"
    print(svg.xmlns)

    print(svg.attrs)
    print(svg.extra_attrs)

    print(svg.find_all("rect"))


if __name__ == "__main__":
    main()
