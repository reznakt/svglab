# the PyO3 crate behind `svglab._resvg`
manifest := "src/svglab-resvg/Cargo.toml"

# the hand-written TOML files; the lockfiles are left to their tools
toml := "pyproject.toml .rumdl.toml src/svglab-resvg/Cargo.toml src/svglab-resvg/deny.toml"

default:
    @just --list

# rebuild the `svglab._resvg` extension module after changing the crate
build *args:
    uv sync --reinstall-package svglab {{ args }}

depcheck:
    uv run deptry src tests
    cargo machete src/svglab-resvg

docs *args:
    SOURCE_DATE_EPOCH="$(git log -1 --format=%ct)" uv run properdocs build {{ args }}

docs-serve *args:
    uv run properdocs serve {{ args }}

format:
    uv run ruff format --diff
    cargo fmt --manifest-path {{ manifest }} --check
    tombi format --check {{ toml }}
    nixfmt --check flake.nix
    yamlfmt -lint .
    just --fmt --unstable --check

format-fix:
    uv run ruff format
    cargo fmt --manifest-path {{ manifest }}
    tombi format {{ toml }}
    nixfmt flake.nix
    yamlfmt .
    just --fmt --unstable

licensecheck:
    uv run licensecheck
    cargo deny --manifest-path {{ manifest }} check

lint:
    uv run ruff check
    cargo clippy --manifest-path {{ manifest }} --all-targets -- --deny warnings
    tombi lint {{ toml }}
    statix check flake.nix
    deadnix --fail flake.nix
    rumdl check .
    typos
    editorconfig-checker

lint-fix:
    uv run ruff check --fix
    cargo clippy --manifest-path {{ manifest }} --all-targets --fix --allow-dirty --allow-staged
    tombi lint {{ toml }}
    statix fix flake.nix
    deadnix --edit flake.nix
    rumdl check --fix .
    typos
    editorconfig-checker

# scan the git history, or with `--pre-commit --staged` just the index, for secrets
secretcheck *args:
    gitleaks git --redact --no-banner --verbose {{ args }}

test *args:
    uv run pytest {{ args }}

typecheck *args:
    uv run pyright --warnings {{ args }}

versioncheck *args:
    uv run vermin . {{ args }}

# lint the GitHub Actions workflows and audit them for security issues
workflowcheck:
    actionlint
    zizmor .github
