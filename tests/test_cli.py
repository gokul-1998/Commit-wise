import argparse
import io
import unittest
from unittest.mock import patch

from gai.cli.main import _normalize_provider_model, cmd_init


class CliTests(unittest.TestCase):
    @patch("gai.cli.main.save_config")
    @patch("gai.cli.main.set_token")
    def test_init_github_shows_pat_url_and_default_model(self, mock_set_token, mock_save_config):
        user_inputs = ["1", "ghp_testtoken"]
        with patch("builtins.input", side_effect=user_inputs):
            with patch("sys.stdout", new=io.StringIO()) as fake_out:
                result = cmd_init(argparse.Namespace())

        self.assertEqual(result, 0)
        output = fake_out.getvalue()
        self.assertIn(
            "https://github.com/settings/personal-access-tokens/new?description=Used+to+call+GitHub+Models+APIs+to+easily+run+LLMs%3A+https%3A%2F%2Fdocs.github.com%2Fgithub-models%2Fquickstart%23step-2-make-an-api-call&name=GitHub+Models+token&user_models=read",
            output,
        )
        self.assertIn("openai/gpt-5", output)
        mock_save_config.assert_called_once_with({"provider": "github", "model": "openai/gpt-5"})

    def test_normalize_github_model_alias(self):
        self.assertEqual(
            _normalize_provider_model("github", "github/copilot"),
            "openai/gpt-5",
        )
        self.assertEqual(
            _normalize_provider_model("github", "github/copilot-1"),
            "openai/gpt-5",
        )
        self.assertEqual(
            _normalize_provider_model("github", "openai/gpt-5"),
            "openai/gpt-5",
        )
