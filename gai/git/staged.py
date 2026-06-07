from __future__ import annotations

import subprocess
from pathlib import Path


def _git(args: list[str], cwd: Path | None = None) -> str:
    proc = subprocess.run(
        ["git", *args],
        cwd=str(cwd) if cwd else None,
        check=False,
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or "git command failed")
    return proc.stdout


def get_staged_files(cwd: Path | None = None) -> list[str]:
    out = _git(["diff", "--cached", "--name-only"], cwd=cwd)
    return [line.strip() for line in out.splitlines() if line.strip()]


def get_staged_diff(cwd: Path | None = None) -> str:
    return _git(["diff", "--cached"], cwd=cwd)


def get_repo_root(cwd: Path | None = None) -> Path:
    out = _git(["rev-parse", "--show-toplevel"], cwd=cwd)
    return Path(out.strip())


def read_file(path: str, cwd: Path | None = None) -> str:
    root = get_repo_root(cwd)
    full_path = root / path
    if not full_path.exists():
        return ""
    return full_path.read_text(encoding="utf-8", errors="ignore")
