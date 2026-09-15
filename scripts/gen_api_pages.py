# pyright: reportMissingTypeStubs=false

"""Generate one API reference page per element and per trait.

Rendering all 80 element classes into a single page produces several
megabytes of HTML, which is slow to load and impossible to navigate. This
script writes a stub page per class instead, so every class gets its own URL,
its own table of contents and its own entry in the search index.

The resulting navigation is described by a `SUMMARY.md` file, which is read
by the `literate-nav` plugin.
"""

import inspect
from collections.abc import Iterator

import mkdocs_gen_files
import pydantic

from svglab.elements import elements, traits


_API_DIR = "api-reference"


def _classes(module: object) -> Iterator[str]:
    """Yield the names of the public classes defined in a module.

    Args:
        module: The module to inspect.

    Yields:
        Class names, in alphabetical order.

    """
    for name, obj in sorted(vars(module).items()):
        if (
            not name.startswith("_")
            and inspect.isclass(obj)
            and issubclass(obj, pydantic.BaseModel)
            and obj.__module__ == module.__name__  # type: ignore[attr-defined]
        ):
            yield name


def _write_pages(module: object, directory: str) -> list[str]:
    """Write one stub page per class in a module.

    Args:
        module: The module whose classes to document.
        directory: The directory to write the pages into.

    Returns:
        The names of the documented classes.

    """
    names = list(_classes(module))
    module_name: str = module.__name__  # type: ignore[attr-defined]

    for name in names:
        path = f"{_API_DIR}/{directory}/{name}.md"

        with mkdocs_gen_files.open(path, "w") as page:
            print(f"# `{name}`", file=page)
            print(file=page)
            print(f"::: {module_name}.{name}", file=page)

        mkdocs_gen_files.set_edit_path(path, "scripts/gen_api_pages.py")

    return names


element_names = _write_pages(elements, "elements")
trait_names = _write_pages(traits, "traits")

with mkdocs_gen_files.open(f"{_API_DIR}/SUMMARY.md", "w") as nav:
    print("- [Overview](index.md)", file=nav)
    print("- Elements", file=nav)

    for name in element_names:
        print(f"    - [{name}](elements/{name}.md)", file=nav)

    print("- Traits", file=nav)

    for name in trait_names:
        print(f"    - [{name}](traits/{name}.md)", file=nav)

    print("- [Attributes](attributes.md)", file=nav)
    print("- [Attribute Groups](attribute-groups.md)", file=nav)
