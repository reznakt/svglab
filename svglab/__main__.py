from .elements import CData, Comment, Text
from .io import parse_svg


def main() -> None:
    soup = parse_svg("<foo></foo>")
    print(soup.prettify())
    comment = Comment("foo")
    print(comment)
    cdata = CData("bar")
    print(cdata)
    text = Text("baz")
    print(text)


if __name__ == "__main__":
    main()
