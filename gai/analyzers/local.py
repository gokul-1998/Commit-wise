from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

TOOLS = [
    ("Ruff", ["ruff", "check", "."]),
    ("MyPy", ["mypy", "."]),
    ("Pytest", ["pytest", "tests/"]),
    ("Bandit", ["bandit", "-r", "."]),
]


def run_local_analyzers(cwd: Path) -> list[tuple[str, str]]:
    reports: list[tuple[str, str]] = []
    for name, cmd in TOOLS:
        if shutil.which(cmd[0]) is None:
            reports.append((name, "not installed (skipped)"))
            continue

        proc = subprocess.run(cmd, cwd=str(cwd), check=False, capture_output=True, text=True)
        status = "passed" if proc.returncode == 0 else "issues found"
        output = (proc.stdout + "\n" + proc.stderr).strip()
        if output:
            output = output[:1500]
            reports.append((name, f"{status}: {output}"))
        else:
            reports.append((name, status))
    return reports
