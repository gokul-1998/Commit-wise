import tempfile
import unittest
from pathlib import Path

from gai.hooks.install import install_pre_commit_hook


class HookTests(unittest.TestCase):
    def test_install_pre_commit_hook(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            temp_root = Path(tmpdir)
            hooks_dir = temp_root / ".git" / "hooks"
            hooks_dir.mkdir(parents=True, exist_ok=True)

            hook_file = install_pre_commit_hook(temp_root)

            self.assertTrue(hook_file.exists())
            content = hook_file.read_text(encoding="utf-8")
            self.assertIn("gai review", content)


if __name__ == "__main__":
    unittest.main()
