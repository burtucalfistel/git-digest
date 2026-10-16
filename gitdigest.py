#!/usr/bin/env python3
"""git-digest: turn a repo's commit history into a human-readable digest.

Summarises the last N days of commits grouped by author, counts changed files,
and prints a markdown report you can paste into a standup note or changelog.

    pip install -e .   (or just run the file)
    git-digest --days 7
    git-digest --days 30 --since-tag v0.2 --author alice
"""
from __future__ import annotations
import argparse
import subprocess
import sys
from collections import defaultdict
from datetime import datetime, timedelta, timezone

GIT = "git"


def _git(*args: str, cwd: str = ".") -> str:
    res = subprocess.run([GIT, *args], cwd=cwd, capture_output=True, text=True)
    if res.returncode != 0:
        raise SystemExit(f"git {' '.join(args)} failed: {res.stderr.strip()}")
    return res.stdout


def repo_root() -> str:
    return _git("rev-parse", "--show-toplevel").strip()


def collect(days: int, since_tag: str | None, author: str | None):
    fmt = "%x1f".join(["%H", "%h", "%an", "%ae", "%aI", "%s"]) + "%x1e"
    revs = f"{since_tag}..HEAD" if since_tag else "HEAD"
    args = ["log", revs, f"--pretty=format:{fmt}", "--no-merges"]
    if author:
        args.append(f"--author={author}")
    raw = _git(*args, cwd=repo_root())
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    commits = []
    for chunk in raw.split("\x1e"):
        chunk = chunk.strip()
        if not chunk:
            continue
        full, short, name, email, date, subject = chunk.split("\x1f")
        ts = datetime.fromisoformat(date)
        if ts < cutoff:
            continue
        files = _git("show", "--name-only", "--pretty=format:", full, cwd=repo_root())
        commits.append({
            "sha": short, "author": name, "email": email,
            "date": ts, "subject": subject,
            "files": [f for f in files.splitlines() if f.strip()],
        })
    return commits


def render(commits, days: int) -> str:
    by_author = defaultdict(list)
    for c in commits:
        by_author[c["author"]].append(c)
    lines = [f"# Git digest — last {days} days", ""]
    if not commits:
        lines.append("_No commits in this window._")
        return "\n".join(lines)
    touched = {f for c in commits for f in c["files"]}
    lines.append(f"**{len(commits)} commits** by **{len(by_author)} authors**, "
                 f"**{len(touched)} files** touched.")
    lines.append("")
    for author in sorted(by_author, key=lambda a: -len(by_author[a])):
        lines.append(f"## {author}")
        for c in sorted(by_author[author], key=lambda c: c["date"]):
            when = c["date"].strftime("%a %d %b")
            lines.append(f"- `{c['sha']}` {when} — {c['subject']}")
        lines.append("")
    return "\n".join(lines)


def main(argv=None):
    p = argparse.ArgumentParser(prog="git-digest", description=__doc__.splitlines()[0])
    p.add_argument("--days", type=int, default=7, help="look-back window (default 7)")
    p.add_argument("--since-tag", help="only commits after this tag")
    p.add_argument("--author", help="filter by author name substring")
    p.add_argument("--out", help="write markdown to file instead of stdout")
    ns = p.parse_args(argv)
    try:
        root = repo_root()
    except SystemExit:
        raise SystemExit("error: not inside a git repository")
    report = render(collect(ns.days, ns.since_tag, ns.author), ns.days)
    if ns.out:
        with open(ns.out, "w") as fh:
            fh.write(report + "\n")
        print(f"wrote {ns.out}")
    else:
        print(report)
    return 0


if __name__ == "__main__":
    sys.exit(main())
