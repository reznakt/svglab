import functools
import pathlib
from typing import Final, Literal, TypeAlias, TypeVar

import lark
import pydantic

__all__ = ["get_validator"]

GRAMMARS_DIR: Final = pathlib.Path(__file__).parent / "grammars"
GAMMAR_EXT: Final = ".lark"

GrammarName: TypeAlias = Literal["transform", "length"]


def get_grammar_path(name: GrammarName) -> pathlib.Path:
    return GRAMMARS_DIR / f"{name}{GAMMAR_EXT}"


@functools.cache
def load_grammar(name: GrammarName) -> str:
    path = get_grammar_path(name)

    with path.open("r") as file:
        return file.read()


_Leaf_T = TypeVar("_Leaf_T")
_Return_T = TypeVar("_Return_T")


def parse(
    text: str,
    /,
    *,
    grammar: GrammarName,
    transformer: lark.Transformer[_Leaf_T, _Return_T],
    **kwargs: object,
) -> lark.ParseTree:
    parser = lark.Lark(
        grammar=load_grammar(grammar),
        parser="lalr",
        propagate_positions=False,
        maybe_placeholders=False,
        transformer=transformer,
        cache=True,
        **kwargs,
    )

    try:
        return parser.parse(text)
    except lark.LarkError as e:
        msg = f"Failed to parse text with grammar {grammar!r}. Reason: \n\n{e}"
        raise ValueError(msg) from e


def get_validator(
    *,
    grammar: GrammarName,
    transformer: lark.Transformer[_Leaf_T, _Return_T],
    **kwargs: object,
) -> pydantic.BeforeValidator:
    def validator(value: object) -> object:
        if isinstance(value, str):
            return parse(
                value,
                grammar=grammar,
                transformer=transformer,
                **kwargs,
            )

        return value

    return pydantic.BeforeValidator(validator)
