default:
    @just --list

docs *args:
    uv run properdocs build {{args}}

docs-serve *args:
    uv run properdocs serve {{args}}

format *args:
    uv run ruff format --diff {{args}}

format-fix *args:
    uv run ruff format {{args}}

licensecheck *args:
    uv run licensecheck {{args}}

lint *args:
    uv run ruff check {{args}}

lint-fix *args:
    uv run ruff check --fix {{args}}

test *args:
    uv run pytest {{args}}

typecheck *args:
    uv run pyright --warnings {{args}}

versioncheck *args:
    uv run vermin . {{args}}
