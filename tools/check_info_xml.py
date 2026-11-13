#!/usr/bin/env python3
"""Require a tracked info.xml in every corpus directory.

Only explicitly enumerated infrastructure and asset directories are exempt.
The checks operate on git-tracked paths (the files that will be deployed).
"""
from __future__ import annotations

import subprocess
import sys

EXEMPT_SUBTREES = frozenset({
    ".github",
    ".meta",
    "lastov_ishayahu/chronos/illustrations",
    "shneur_zalman_of_liadi/likutei_torah_al_devarim/meta",
    "sholom_dovber_schneersohn/sefer_hamaamarim_5656/meta",
    "sholom_dovber_schneersohn/sefer_hamaamarim_5663/meta",
    "sholom_dovber_schneersohn/sefer_hamaamarim_5680/meta",
    "template/book/illustrations",
})


def is_exempt(directory: str) -> bool:
    return any(
        directory == prefix or directory.startswith(prefix + "/")
        for prefix in EXEMPT_SUBTREES
    )


def missing_info_files(tracked_paths: list[str]) -> list[str]:
    """Return required info.xml paths missing from a set of tracked files."""
    files = set(tracked_paths)
    directories = set()
    for path in files:
        parts = path.split("/")
        for depth in range(1, len(parts)):
            directories.add("/".join(parts[:depth]))

    missing = [
        directory + "/info.xml"
        for directory in sorted(directories)
        if not is_exempt(directory) and directory + "/info.xml" not in files
    ]
    if "info.xml" not in files:
        missing.insert(0, "info.xml")
    return missing


def main() -> int:
    try:
        tracked = subprocess.check_output(
            ["git", "ls-files", "--cached", "-z"],
            stderr=subprocess.PIPE,
        )
    except subprocess.CalledProcessError as exc:
        print("Cannot list tracked files: " + exc.stderr.decode(errors="replace"), file=sys.stderr)
        return 2

    files = [path.decode("utf-8", errors="surrogateescape")
             for path in tracked.split(b"\0") if path]
    missing = missing_info_files(files)
    if missing:
        for path in missing:
            print(f"::error file={path}::Required info.xml is missing")
        print(f"Missing {len(missing)} required info.xml file(s)", file=sys.stderr)
        return 1

    directories = {
        "/".join(path.split("/")[:depth])
        for path in files
        for depth in range(1, len(path.split("/")))
    }
    checked = sum(not is_exempt(directory) for directory in directories)
    print(f"Verified info.xml in {checked} content directories and repository root")
    return 0


if __name__ == "__main__":
    sys.exit(main())
