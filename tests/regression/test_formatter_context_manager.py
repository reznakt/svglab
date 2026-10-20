from svglab import Formatter, get_current_formatter


def test_formatter_context_manager_binds_the_formatter() -> None:
    formatter = Formatter(indent=2)

    with formatter as bound:
        assert bound is formatter
        assert get_current_formatter() is formatter
