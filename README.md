# git-digest

Pastebin your week, not your `git log`. `git-digest` walks a repository's recent
history and renders a markdown standup digest grouped by author — commit counts,
subjects, and the set of touched files.

```
$ git-digest --days 7
# Git digest — last 7 days

**9 commits** by **2 authors**, **14 files** touched.

## Alice
- `a1b2c3d` Mon 10 nov — fix off-by-one in rate limiter
- `e4f5a6b` Tue 11 nov — add tests for window expiry
```

## Usage

```
python3 gitdigest.py --days 14            # print to stdout
python3 gitdigest.py --days 30 --out WEEKLY.md
python3 gitdigest.py --since-tag v0.2 --author alice
```

No dependencies beyond the standard library. Requires `git` on PATH.
