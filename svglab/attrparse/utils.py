import itertools
import pathlib

import lark
import pydantic
from typing_extensions import Final, LiteralString, TypeVar


_T = TypeVar("_T")
_Leaf_T = TypeVar("_Leaf_T")
_Return_T = TypeVar("_Return_T")


_CURRENT_DIR: Final = pathlib.Path(__file__).parent
_GRAMMARS_DIR: Final = _CURRENT_DIR / "grammars"


def _parse(
    text: str,
    /,
    *,
    grammar: LiteralString,
    transformer: lark.Transformer[_Leaf_T, _Return_T],
    **kwargs: object,
) -> lark.ParseTree:
    parser = lark.Lark.open(
        grammar_filename=str(_GRAMMARS_DIR / grammar),
        rel_to=None,
        cache=True,
        maybe_placeholders=False,
        ordered_sets=False,
        parser="lalr",
        propagate_positions=False,
        transformer=transformer,
        **kwargs,
    )

    try:
        return parser.parse(text)
    except lark.LarkError as e:
        msg = f"Failed to parse text with grammar {grammar!r}. Reason: \n\n{e}"
        raise ValueError(msg) from e


def get_validator(
    *,
    grammar: LiteralString,
    transformer: lark.Transformer[_Leaf_T, _Return_T],
    **kwargs: object,
) -> pydantic.BeforeValidator:
    def validator(value: object) -> object:
        if isinstance(value, str):
            return _parse(
                value, grammar=grammar, transformer=transformer, **kwargs
            )

        return value

    return pydantic.BeforeValidator(validator)


def v_args_to_list(*values: _T) -> list[_T]:
    # drop the first value, which is the transformer instance (self)
    return list(itertools.islice(values, 1, None))
