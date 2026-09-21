# the PyO3 crate behind `svglab._resvg`
manifest := "src/svglab-resvg/Cargo.toml"

default:
    @just --list

# rebuild the `svglab._resvg` extension module after changing the crate
build *args:
    uv sync --reinstall-package svglab {{args}}

docs *args:
    SOURCE_DATE_EPOCH="$(git log -1 --format=%ct)" uv run properdocs build {{args}}

docs-serve *args:
    uv run properdocs serve {{args}}

format:
    uv run ruff format --diff
    cargo fmt --manifest-path {{manifest}} --check

format-fix:
    uv run ruff format
    cargo fmt --manifest-path {{manifest}}

licensecheck:
    uv run licensecheck
    cargo deny --manifest-path {{manifest}} check

lint:
    uv run ruff check
    cargo clippy --manifest-path {{manifest}} --all-targets -- --deny warnings

lint-fix:
    uv run ruff check --fix
    cargo clippy --manifest-path {{manifest}} --all-targets --fix --allow-dirty --allow-staged

test *args:
    uv run pytest {{args}}

typecheck *args:
    uv run pyright --warnings {{args}}

versioncheck *args:
    uv run vermin . {{args}}
