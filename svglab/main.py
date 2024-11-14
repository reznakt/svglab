def add(a: int, b: int) -> int:
    """Add two numbers together.

    >>> add(2, 3)
    5
    >>> add(-1, 1)
    0
    """
    return a + b


def main() -> None:
    result = add(1, 2)
    print(result)  # noqa: T201


if __name__ == "__main__":
    main()
