import importlib
import pkgutil

import pydantic
import pydantic.dataclasses
import pytest

import svglab
from svglab import Circle
from svglab import Element as BaseElement
from svglab.elements.traits import Element as ElementTrait


def _import_all_modules() -> None:
    for module in pkgutil.walk_packages(svglab.__path__, "svglab."):
        importlib.import_module(module.name)


def _subclasses(cls: type) -> set[type]:
    found: set[type] = set()
    stack = [cls]

    while stack:
        for subclass in stack.pop().__subclasses__():
            if subclass not in found:
                found.add(subclass)
                stack.append(subclass)

    return found


def _is_svglab_class(cls: type) -> bool:
    return cls.__module__.startswith("svglab.")


def _qualified_name(cls: type) -> str:
    # bare names collide: `svglab.entities.Element` vs the trait `Element`
    return f"{cls.__module__}.{cls.__qualname__}"


_import_all_modules()

_MODELS = sorted(
    filter(_is_svglab_class, _subclasses(pydantic.BaseModel)),
    key=_qualified_name,
)

_DATACLASSES = sorted(
    {
        obj
        for module in pkgutil.walk_packages(svglab.__path__, "svglab.")
        for obj in vars(importlib.import_module(module.name)).values()
        if isinstance(obj, type)
        and _is_svglab_class(obj)
        and pydantic.dataclasses.is_pydantic_dataclass(obj)
    },
    key=_qualified_name,
)


# Models defer their build to first use, so a broken annotation no longer
# fails at import. Force every build here so it fails in the test suite
# instead of on a user's first use of a class.
@pytest.mark.parametrize("model", _MODELS, ids=_qualified_name)
def test_model_builds(model: type[pydantic.BaseModel]) -> None:
    model.model_rebuild(force=True, raise_errors=True)


@pytest.mark.parametrize("dataclass", _DATACLASSES, ids=_qualified_name)
def test_dataclass_builds(dataclass: type) -> None:
    pydantic.dataclasses.rebuild_dataclass(
        dataclass, force=True, raise_errors=True
    )


def test_all_models_collected() -> None:
    assert Circle in _MODELS
    assert BaseElement in _MODELS
    assert _DATACLASSES


def test_element_subclass_outside_svglab() -> None:
    # `Entity.parent` refers to `Element`, which is not in scope here
    class Custom(ElementTrait):
        pass

    assert Custom().parent is None
