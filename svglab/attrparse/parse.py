"""Utilities for parsing with Lark."""

import functools
import itertools
import pathlib

import lark
import pydantic
from typing_extensions import Any, Final, LiteralString, TypeVar, cast


_T = TypeVar("_T")
_LeafT = TypeVar("_LeafT")
_ReturnT = TypeVar("_ReturnT")
_TransformerT = TypeVar("_TransformerT", bound=lark.Transformer[Any, Any])


_CURRENT_DIR: Final = pathlib.Path(__file__).parent
_GRAMMARS_DIR: Final = _CURRENT_DIR / "grammars"


@functools.cache
def _get_parser(*, grammar: LiteralString) -> lark.Lark:
    return lark.Lark.open(
        grammar_filename=str(_GRAMMARS_DIR / grammar),
        rel_to=None,
        cache=True,
        maybe_placeholders=False,
        ordered_sets=False,
        parser="lalr",
        propagate_positions=False,
    )


def parse(
    text: str,
    /,
    *,
    grammar: LiteralString,
    transformer: lark.Transformer[_LeafT, _ReturnT],
) -> _ReturnT:
    """Parse a string using a Lark grammar.

    Args:
        text: The text to parse.
        grammar: The name of the grammar file (without the `.lark` extension).
        transformer: A Lark transformer to use for transforming the parse tree.
            The transformer must be a subclass of `lark.Transformer`.

    Returns:
        The parsed and transformed result.

    Raises:
        ValueError: If a parsing error occurs.

    """
    parser = _get_parser(grammar=grammar)

    try:
        tree = parser.parse(text)
        return transformer.transform(cast(lark.Tree[_LeafT], tree))
    except lark.LarkError as e:
        msg = f"Failed to parse text with grammar {grammar!r}. Reason: \n\n{e}"
        raise ValueError(msg) from e


def get_validator(
    *,
    grammar: LiteralString,
    transformer: lark.Transformer[_LeafT, _ReturnT],
    **kwargs: object,
) -> pydantic.BeforeValidator:
    """Get a Pydantic BeforeValidator for parsing with Lark.

    Args:
        grammar: The name of the grammar file (without the `.lark` extension).
        transformer: A Lark transformer to use for transforming the parse tree.
            The transformer must be a subclass of `lark.Transformer`.
        **kwargs: Additional keyword arguments to pass to the parser.

    Returns:
        A Pydantic BeforeValidator that can be used to parse strings with the
        specified grammar.

    """

    def validator(value: object) -> object:
        if isinstance(value, str):
            return parse(
                value, grammar=grammar, transformer=transformer, **kwargs
            )

        return value

    return pydantic.BeforeValidator(validator)


def v_args_to_list(*values: _T) -> list[_T]:
    """Convert the arguments to a list, discarding the first one.

    Args:
        *values: The values to convert.

    Returns:
        A list of the values, excluding the first one.

    """
    # drop the first value, which is the transformer instance (self)
    return list(itertools.islice(values, 1, None))


def visit_tokens(cls: type[_TransformerT]) -> type[_TransformerT]:
    """A decorator to make a Lark transformer visit tokens.

    This decorator modifies the `__init__` method of the transformer class
    to set the `visit_tokens` attribute to `True`.

    Args:
        cls: The transformer class to decorate.

    Returns:
        The decorated transformer class.

    """  # noqa: D401
    original_init = cls.__init__

    @functools.wraps(original_init)
    def new_init(
        self: _TransformerT, *args: object, **kwargs: object
    ) -> None:
        del args, kwargs
        original_init(self, visit_tokens=True)

    cls.__init__ = new_init
    return cls
