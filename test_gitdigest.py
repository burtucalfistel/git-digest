"""Tiny sanity tests — run with: python3 -m pytest -q  (or plain python3 below)."""
import subprocess, tempfile, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from gitdigest import collect, render

def _mkrepo(path):
    def git(*a): subprocess.run(["git", *a], cwd=path, check=True,
                                env={**os.environ, "GIT_AUTHOR_DATE": "2026-11-09T10:00:00+01:00",
                                     "GIT_COMMITTER_DATE": "2026-11-09T10:00:00+01:00"})
    git("init", "-q"); git("config", "user.email", "t@example.com"); git("config", "user.name", "Tester")
    open(os.path.join(path, "a.txt"), "w").write("1\n"); git("add", "a.txt"); git("commit", "-m", "first")
    open(os.path.join(path, "a.txt"), "a").write("2\n"); git("add", "a.txt"); git("commit", "-m", "second")

if __name__ == "__main__":
    with tempfile.TemporaryDirectory() as d:
        _mkrepo(d)
        os.chdir(d)
        cs = collect(days=365, since_tag=None, author=None)
        assert len(cs) == 2, cs
        md = render(cs, 365)
        assert "2 commits" in md and "Tester" in md
        print("ok: collect/render")
