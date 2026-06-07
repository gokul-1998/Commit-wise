from __future__ import annotations

import os
from pathlib import Path


HOOK_CONTENT = "#!/usr/bin/env bash\nset -euo pipefail\ngai review\n"


def install_pre_commit_hook(repo_root: Path) -> Path:
    hooks_dir = repo_root / ".git" / "hooks"
    hooks_dir.mkdir(parents=True, exist_ok=True)
    hook_file = hooks_dir / "pre-commit"
    hook_file.write_text(HOOK_CONTENT, encoding="utf-8")
    os.chmod(hook_file, 0o755)
    return hook_file
