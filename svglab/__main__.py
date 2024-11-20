from svglab.elements.tag import G, Rect

from .elements import CData, Comment, Text
from .io import parse_svg


def main() -> None:
    soup = parse_svg("<foo></foo>")
    print(soup.prettify())

    group = (
        G()
        .add_child(Rect())
        .add_child(Comment("This is an example comment"))
        .add_child(CData("foo { background-color: red; }"))
        .add_child(Text("baz"))
        .add_child(G().add_child(Rect()).add_child(Rect()))
    )
    print(group)

    group2 = G(
        Rect(),
        Comment("This is an example comment"),
        CData("foo { background-color: red; }"),
        Text("baz"),
        G(Rect(), Rect()),
    )
    print(group2)


if __name__ == "__main__":
    main()
