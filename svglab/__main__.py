from .io import parse_svg


def main() -> None:
    soup = parse_svg("<foo></foo>")
    print(soup.prettify())


if __name__ == "__main__":
    main()
