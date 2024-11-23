# ruff: noqa: T201

from .elements import CData, Comment, G, Rect, Svg, Text
from .parse import parse_svg


def main() -> None:
    svg = parse_svg(
        """
        <svg>
            <g>
                <rect />
                <!-- This is an example comment -->
                <![CDATA[foo { background-color: red; }]]>
                baz
                <g>
                    <rect />
                    <rect />
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


if __name__ == "__main__":
    main()
