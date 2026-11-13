#!/usr/bin/env python3
"""Audit internal <link> and <quote> targets against the actual XML corpus.

Report all unresolved targets, but fail CI only for newly broken references
relative to the workflow's base revision. This avoids blocking deployment for
historical incomplete translations while preventing additional regressions.

Resolution follows jewTeX texts/storage.py select_text: author/book directory,
daf or page selection, then nested header type/name selectors.
"""
from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import dataclass
from functools import lru_cache
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET


# Priorities match jewTeX texts/storage.py params_sort_key.
PRIORITY = {
    "dibur_amathil": 1, "j_chapter": 1, "chapter": 3, "parsha": 3,
    "posuk": 5, "mishna": 5, "daf": 3, "siman": 5, "seif": 7,
    "klal": 4, "letter": 10, "siman_katan": 10, "ref": 99,
    "girsa": 999,
}
PRESENTATION = {"author", "book", "daf", "page", "upper"}


@dataclass(frozen=True)
class Finding:
    path: str
    kind: str
    target: tuple[tuple[str, str], ...]
    reason: str

    def key(self) -> tuple:
        # The reason may evolve without changing whether a link is broken.
        return (self.path, self.kind, self.target)

    def description(self) -> str:
        target = " ".join(f'{name}="{value}"' for name, value in self.target)
        return f"{self.path}: <{self.kind} {target}> — {self.reason}"


class Corpus:
    def __init__(self, root: Path):
        self.root = Path(root)

    @lru_cache(maxsize=None)
    def book_roots(self, author: str, book: str):
        # Never let a path traversal in source XML read outside the repository.
        if any(not p or p in {".", ".."} or "/" in p or "\\" in p
               for p in (author, book)):
            return None
        directory = self.root / author / book
        if not (directory / "info.xml").is_file():
            return None
        result = []
        for path in sorted(directory.glob("*.xml")):
            if path.name == "info.xml":
                continue
            try:
                result.append(ET.parse(path).getroot())
            except ET.ParseError:
                # The separate XML schema job reports malformed documents.
                continue
        return result

    def resolve(self, element: ET.Element) -> str | None:
        attrs = element.attrib
        author, book = attrs.get("author"), attrs.get("book")
        if not author or not book:
            return "missing author or book"
        roots = self.book_roots(author, book)
        if roots is None:
            return f"book not found: {author}/{book}"
        if not roots:
            return f"book has no text XML: {author}/{book}"

        page = attrs.get("page")
        daf = attrs.get("daf")
        selected = []
        if page or daf:
            tag, value = ("page", page) if page else ("daf", daf)
            for root in roots:
                selected.extend(node for node in root.iter(tag)
                                if node is not root and node.get("name") == value)
            if not selected:
                return f"{tag} {value} not present"
        else:
            selected = list(roots)

        qualifiers = [(key, value) for key, value in attrs.items()
                      if key not in PRESENTATION]
        qualifiers.sort(key=lambda x: PRIORITY.get(x[0], 999))

        # ElementTree does not expose iterancestors; build parent lookup.
        parents = {}
        for root in roots:
            parents.update({child: parent for parent in root.iter()
                            for child in parent})

        for key, value in qualifiers:
            next_selected = []
            for node in selected:
                if key == "chapter":
                    p = parents.get(node)
                    while p is not None:
                        if p.tag == "header" and p.get("type") == "chapter" and p.get("name") == value:
                            next_selected.append(node)
                            break
                        p = parents.get(p)
                    else:
                        next_selected.extend(
                            h for h in node.iter("header") if h is not node
                            and h.get("type") == key and h.get("name") == value
                        )
                else:
                    next_selected.extend(
                        h for h in node.iter("header") if h is not node
                        and h.get("type") == key and h.get("name") == value
                    )
            selected = next_selected
            if not selected:
                return f"{key} {value} not present in selected text"

        # select_text copies *children* of selected elements into its result.
        # Empty headers/paragraphs cannot produce a useful readable target.
        if not any(any(part.strip() for child in node for part in child.itertext())
                   for node in selected):
            return "selected fragment has no readable text"
        return None


def scan(root: Path) -> list[Finding]:
    corpus = Corpus(root)
    findings = []
    for path in sorted(root.rglob("*.xml")):
        relative = path.relative_to(root).as_posix()
        if len(path.relative_to(root).parts) < 3 or path.name == "info.xml":
            continue
        try:
            doc = ET.parse(path).getroot()
        except ET.ParseError:
            continue  # Existing XML validation handles this.
        for element in doc.iter():
            if element.tag not in {"link", "quote"}:
                continue
            reason = corpus.resolve(element)
            if reason:
                findings.append(Finding(relative, element.tag,
                                        tuple(sorted(element.attrib.items())), reason))
    return findings


def new_regressions(current: list[Finding], before: list[Finding]) -> list[Finding]:
    baseline = Counter(item.key() for item in before)
    result = []
    for finding in current:
        key = finding.key()
        if baseline[key]:
            baseline[key] -= 1
        else:
            result.append(finding)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline", required=True, help="Existing git commit SHA")
    parser.add_argument("--report", type=Path)
    parser.add_argument("--summary", type=Path)
    args = parser.parse_args()

    current = scan(Path("."))
    with tempfile.TemporaryDirectory(prefix="jewtex-link-audit-") as temp:
        previous = Path(temp) / "previous"
        subprocess.run(["git", "worktree", "add", "--detach", "--quiet",
                        str(previous), args.baseline], check=True)
        try:
            before = scan(previous)
        finally:
            subprocess.run(["git", "worktree", "remove", "--force",
                            str(previous)], check=True)

    fresh = new_regressions(current, before)
    print(f"Internal link audit: {len(current)} currently broken, "
          f"{len(before)} in baseline, {len(fresh)} new regressions")
    for finding in fresh[:50]:
        print(f"::error file={finding.path}::{finding.description()}")
    for finding in current[:15]:
        print("UNRESOLVED: " + finding.description())
    if len(fresh) > 50:
        print(f"{len(fresh) - 50} more new regressions in report")

    report = {
        "baseline": args.baseline,
        "unresolved_total": len(current),
        "unresolved_before": len(before),
        "new_regressions": len(fresh),
        "current": [dict(source=f.path, tag=f.kind,
                         attributes=dict(f.target), reason=f.reason) for f in current],
        "new": [dict(source=f.path, tag=f.kind,
                     attributes=dict(f.target), reason=f.reason) for f in fresh],
    }
    if args.report:
        args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    if args.summary:
        with args.summary.open("a", encoding="utf-8") as out:
            out.write("\n## Internal links and citations\n")
            out.write(f"- Existing unresolved targets: **{len(current)}** "
                      f"(baseline: {len(before)})\n")
            out.write(f"- Newly broken targets: **{len(fresh)}** — "
                      + ("CI blocked\n" if fresh else "CI passed\n"))
            for finding in fresh[:25]:
                out.write("- " + finding.description().replace("|", "\\|") + "\n")
    return 1 if fresh else 0


if __name__ == "__main__":
    sys.exit(main())
