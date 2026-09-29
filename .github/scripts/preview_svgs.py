#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "defusedxml>=0.7.1",
#   "jinja2>=3.1.0",
#   "markdown-it-py>=3.0.0",
#   "pygithub>=2.5.0",
# ]
# ///
"""Show the SVGs that maintainers post in an issue or PR in a comment."""

import dataclasses
import hashlib
import html
import os
import pathlib
import re
import xml.etree.ElementTree as ET

import defusedxml.ElementTree
import jinja2
import markdown_it
from github import (
    Auth,
    Github,
    InputGitTreeElement,
    UnknownObjectException,
)
from github.GithubObject import NotSet
from github.Issue import Issue
from github.Repository import Repository
from markdown_it.token import Token


MARKER = "<!-- svg-preview -->"
MAX_COMMENT = 65536
NAMES = ("width", "height")
TRUSTED = {"OWNER", "MEMBER", "COLLABORATOR"}
BOT = "github-actions[bot]"
REF = "svg-previews/main"
SVG_ROOT = "{http://www.w3.org/2000/svg}svg"
SVG_TAG = re.compile(r"<(?P<close>/)?svg\b[^>]*?(?P<empty>/)?>")
NAMESPACES = {
    "xmlns": "http://www.w3.org/2000/svg",
    "xmlns:xlink": "http://www.w3.org/1999/xlink",
}
TEMPLATE = jinja2.Environment(
    loader=jinja2.FileSystemLoader(pathlib.Path(__file__).parent),
    autoescape=jinja2.select_autoescape(),
    trim_blocks=True,
    lstrip_blocks=True,
).get_template("preview_svgs.md.j2")


@dataclasses.dataclass(frozen=True)
class Preview:
    """An SVG to show and where in the thread it comes from."""

    link: str
    label: str
    where: str
    source: str
    svg: str
    side: str

    @property
    def filename(self) -> str:
        """Name the file by its content so that repeats are free."""
        return f"{hashlib.sha256(self.svg.encode()).hexdigest()[:16]}.svg"

    @property
    def fence(self) -> str:
        """Return a code fence longer than any backticks in the source."""
        ticks = max(map(len, re.findall("`+", self.source)), default=0)
        return "`" * max(3, ticks + 1)


def extract(code: str) -> list[str]:
    """Return the outermost `svg` elements in a piece of code."""
    found = []
    depth = start = 0
    for tag in SVG_TAG.finditer(code):
        if tag["close"]:
            depth = max(depth - 1, 0)
            if depth == 0:
                found.append(code[start : tag.end()])
        elif tag["empty"]:
            if depth == 0:
                found.append(tag[0])
        else:
            if depth == 0:
                start = tag.start()
            depth += 1
    return found


def add_namespaces(svg: str) -> str:
    """Declare the namespaces that HTML implies for an inline SVG."""
    root = svg[: svg.index(">")]
    declarations = "".join(
        f' {name}="{uri}"'
        for name, uri in NAMESPACES.items()
        if not re.search(rf"\s{name}\s*=", root)
        and (name == "xmlns" or "xlink:" in svg)
    )
    return f"<svg{declarations}{svg[4:]}"


def versions(block: Token) -> list[tuple[str, str]]:
    """Return the code of a block, or both sides of a diff, with a label."""
    if block.info.split()[:1] != ["diff"]:
        return [("", block.content)]
    lines = block.content.splitlines()
    return [
        (
            side,
            "\n".join(
                line[1:] for line in lines if line[:1] in {" ", sign}
            ),
        )
        for side, sign in [("before", "-"), ("after", "+")]
    ]


def find_svgs(text: str) -> list[list[tuple[str, str]]]:
    """Group the SVGs in a text's code blocks, a diff's sides together."""
    tokens = markdown_it.MarkdownIt("commonmark").parse(text)
    blocks = [t for t in tokens if t.type in {"fence", "code_block"}]
    found: list[list[tuple[str, str]]] = []
    for i, block in enumerate(blocks, 1):
        language = block.info.split()[:1]
        block_name = f"code block {i}"
        if language:
            block_name += f" (<code>{html.escape(language[0])}</code>)"
        unique: dict[str, str] = {}
        sides = versions(block)
        for side, code in sides:
            svgs = extract(code)
            for k, svg in enumerate(svgs, 1):
                where = [block_name]
                if side:
                    where.append(side)
                if len(svgs) > 1:
                    where.append(f"SVG {k} of {len(svgs)}")
                unique.setdefault(svg, ", ".join(where))
        items = list(unique.items())
        found += [items] if len(sides) > 1 else [[item] for item in items]
    return found


def parse(svg: str) -> ET.Element | None:
    """Return the root of an SVG that a browser would display."""
    try:
        root = defusedxml.ElementTree.fromstring(
            svg, forbid_entities=False
        )
    except ET.ParseError:
        return None
    return root if root.tag == SVG_ROOT else None


def side(root: ET.Element) -> str:
    """Return the longer side of the SVG, which the preview box fits."""
    box = root.get("viewBox", "").replace(",", " ").split()
    sides = box[2:4] or [root.get(k, "") for k in NAMES]
    try:
        width, height = (float(re.match(r"[\d.]*", s)[0]) for s in sides)
    except ValueError:
        return "width"
    return "height" if height > width else "width"


def publish(repo: Repository, files: dict[str, str]) -> str:
    """Commit the files that the ref lacks and return the commit's SHA."""
    try:
        ref = repo.get_git_ref(REF)
    except UnknownObjectException:
        ref, parents = None, []
    else:
        parents = [repo.get_git_commit(ref.object.sha)]
        existing = {e.path for e in parents[0].tree.tree}
        files = {k: v for k, v in files.items() if k not in existing}

    if not files:
        return parents[0].sha

    tree = repo.create_git_tree(
        [
            InputGitTreeElement(path, "100644", "blob", content=svg)
            for path, svg in files.items()
        ],
        base_tree=parents[0].tree if parents else NotSet,
    )
    commit = repo.create_git_commit("Add SVG previews", tree, parents)
    if ref is None:
        repo.create_git_ref(f"refs/{REF}", commit.sha)
    else:
        ref.edit(commit.sha)
    return commit.sha


def comment(
    raw: str, figures: list[list[Preview]], *, sources: bool
) -> str:
    """Write the preview comment, with the SVGs' code if asked to."""
    return TEMPLATE.render(
        marker=MARKER, raw=raw, figures=figures, sources=sources
    ).strip()


def sync(repo: Repository, issue: Issue) -> None:
    """Sync the preview comment with the thread."""
    comments = list(issue.get_comments())

    own = next(
        (c for c in comments if c.user.login == BOT and MARKER in c.body),
        None,
    )
    groups = [
        [
            Preview(item.html_url, label, where, source, svg, side(root))
            for source, where in group
            for svg in [add_namespaces(source)]
            if (root := parse(svg)) is not None
        ]
        for label, item in [
            ("the description", issue),
            *(("a comment", c) for c in comments),
        ]
        if item.author_association in TRUSTED
        for group in find_svgs(item.body or "")
    ]
    figures = [group for group in groups if group]

    if not figures:
        if own is not None:
            own.delete()
        return

    files = {p.filename: p.svg for figure in figures for p in figure}
    sha = publish(repo, files)
    raw = f"https://raw.githubusercontent.com/{repo.full_name}/{sha}"
    body = comment(raw, figures, sources=True)
    if len(body) > MAX_COMMENT:
        body = comment(raw, figures, sources=False)
    if own is None:
        issue.create_comment(body)
    elif own.body != body:
        own.edit(body)


def main() -> None:
    """Sync one thread, or every thread with a preview if none is given."""
    client = Github(auth=Auth.Token(os.environ["GH_TOKEN"]))
    repo = client.get_repo(os.environ["GITHUB_REPOSITORY"])
    if number := os.environ.get("NUMBER"):
        numbers = {int(number)}
    else:
        numbers = {
            int(c.issue_url.rsplit("/", 1)[1])
            for c in repo.get_issues_comments()
            if c.user.login == BOT and MARKER in c.body
        }
    for n in sorted(numbers):
        sync(repo, repo.get_issue(n))


if __name__ == "__main__":
    main()
