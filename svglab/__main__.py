# ruff: noqa: T201

from .elements import CData, Comment, G, Rect, Svg, Text
from .io import parse_svg


def main() -> None:
    soup = parse_svg("<foo></foo>")
    print(soup.prettify())

    group = Svg(
        G()
        .add_child(Rect())
        .add_child(Comment("This is an example comment"))
        .add_child(CData("foo { background-color: red; }"))
        .add_child(Text("baz"))
        .add_child(G().add_child(Rect()).add_child(Rect()))
    )
    print(group)

    group2 = Svg(
        G(
            Rect(),
            Comment("This is an example comment"),
            CData("foo { background-color: red; }"),
            Text("baz"),
            G(Rect(), Rect()),
        )
    )
    print(group2)
    print(group == group2)
    print(len(group.children))


if __name__ == "__main__":
    main()
