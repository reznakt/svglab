#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "defusedxml>=0.7.1",
#   "markdown-it-py>=3.0.0",
#   "pygithub>=2.5.0",
# ]
# ///
"""Show the SVGs that maintainers post in an issue or PR in a comment."""

import hashlib
import os
import xml.etree.ElementTree as ET

import defusedxml.ElementTree
import markdown_it
from github import (
    Auth,
    Github,
    InputGitTreeElement,
    UnknownObjectException,
)
from github.GithubObject import NotSet
from github.Repository import Repository


MARKER = "<!-- svg-preview -->"
TRUSTED = {"OWNER", "MEMBER", "COLLABORATOR"}
BOT = "github-actions[bot]"
REF = "svg-previews/main"
SVG_ROOT = "{http://www.w3.org/2000/svg}svg"


def find_svgs(text: str) -> list[str]:
    """Return the code blocks that contain an SVG."""
    tokens = markdown_it.MarkdownIt("commonmark").parse(text)
    return [
        t.content
        for t in tokens
        if t.type in {"fence", "code_block"} and "<svg" in t.content
    ]


def check(svg: str) -> str | None:
    """Return why a browser would not display the SVG, if it would not."""
    try:
        root = defusedxml.ElementTree.fromstring(
            svg, forbid_entities=False
        )
    except ET.ParseError as e:
        return f"not well-formed XML: {e}"
    if root.tag != SVG_ROOT:
        return "the root is not an `svg` element in the SVG namespace"
    return None


def filename(svg: str) -> str:
    """Name the file by its content so that repeats are free."""
    return f"{hashlib.sha256(svg.encode()).hexdigest()[:16]}.svg"


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


def main() -> None:
    """Sync the preview comment with the thread."""
    client = Github(auth=Auth.Token(os.environ["GH_TOKEN"]))
    repo = client.get_repo(os.environ["GITHUB_REPOSITORY"])
    issue = repo.get_issue(int(os.environ["NUMBER"]))
    comments = list(issue.get_comments())

    own = next(
        (c for c in comments if c.user.login == BOT and MARKER in c.body),
        None,
    )
    found = [
        (label, item.html_url, svg)
        for label, item in [
            ("the description", issue),
            *((f"@{c.user.login}", c) for c in comments),
        ]
        if item.author_association in TRUSTED
        for svg in find_svgs(item.body or "")
    ]

    if not found:
        if own is not None:
            own.delete()
        return

    previews = [(label, url, svg, check(svg)) for label, url, svg in found]
    files = {
        filename(svg): svg for *_, svg, error in previews if not error
    }
    sha = publish(repo, files) if files else None

    raw = f"https://raw.githubusercontent.com/{repo.full_name}/{sha}"
    lines = [MARKER, "### SVG previews"]
    for label, url, svg, error in previews:
        lines.append(f"From [{label}]({url}):")
        if error:
            lines.append(f"> [!WARNING]\n> Cannot show: {error}")
        else:
            lines.append(f'<img src="{raw}/{filename(svg)}">')

    body = "\n\n".join(lines)
    if own is None:
        issue.create_comment(body)
    elif own.body != body:
        own.edit(body)


if __name__ == "__main__":
    main()
