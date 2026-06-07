from __future__ import annotations

import argparse
import subprocess
from pathlib import Path

from gai.analyzers.local import run_local_analyzers
from gai.config.settings import get_token, load_config, save_config, set_token
from gai.git.staged import get_repo_root, get_staged_diff, get_staged_files
from gai.hooks.install import install_pre_commit_hook
from gai.prompts.review_prompt import build_explain_prompt
from gai.providers.reviewer import ReviewResult, review_staged_changes

PROVIDERS = ["github", "openai", "anthropic", "gemini", "ollama"]
DEFAULT_PROVIDER_MODELS = {
    "github": "github/copilot",
    "openai": "openai/gpt-5-mini",
    "anthropic": "anthropic/claude-3",
    "gemini": "gemini/1",
    "ollama": "ollama/ollama-small",
}

GITHUB_PAT_URL = (
    "https://github.com/settings/personal-access-tokens/new?"
    "description=Used+to+call+GitHub+Models+APIs+to+easily+run+LLMs%3A+"
    "https%3A%2F%2Fdocs.github.com%2Fgithub-models%2Fquickstart%23step-2-make-an-api-call&"
    "name=GitHub+Models+token&user_models=read"
)


def _status(flag: bool) -> str:
    return "✓" if flag else "⚠"


def _print_review(result: ReviewResult) -> None:
    print("\nReviewing staged changes...\n")
    print(f"{_status(result.security)} Security")
    print(f"{_status(result.performance)} Performance")
    print(f"{_status(result.maintainability)} Maintainability")
    print(f"{_status(result.tests)} Tests")

    print("\nSuggestions:\n")
    if not result.suggestions:
        print("No critical suggestions found.")
    else:
        for idx, suggestion in enumerate(result.suggestions, start=1):
            print(f"{idx}. {suggestion.file} [{suggestion.severity}]")
            print(f"   {suggestion.message}")
            print(f"   Suggested: {suggestion.fix}\n")

    print(f"Overall score: {result.score}/10")


def cmd_init(_: argparse.Namespace) -> int:
    print("Choose provider:\n")
    for idx, provider in enumerate(PROVIDERS, start=1):
        print(f"{idx}. {provider}")

    raw_choice = input("\n> ").strip()
    if raw_choice.isdigit() and 1 <= int(raw_choice) <= len(PROVIDERS):
        provider = PROVIDERS[int(raw_choice) - 1]
    elif raw_choice in PROVIDERS:
        provider = raw_choice
    else:
        print("Invalid provider selection.")
        return 1

    setup_info = _provider_setup_instructions(provider)
    if setup_info:
        print(setup_info)

    token = input(f"Enter {provider} token (stored securely with keyring):\n> ").strip()
    if not token:
        print("Token is required.")
        return 1

    set_token(provider, token)
    save_config({"provider": provider, "model": DEFAULT_PROVIDER_MODELS.get(provider, "openai/gpt-5-mini")})

    print("\nSaved ~/.gai/config.toml (without token).")
    print("Token saved in keyring.")
    return 0


def _provider_setup_instructions(provider: str) -> str | None:
    if provider == "github":
        return (
            "\nGitHub provider requires a Personal Access Token (PAT).\n"
            f"Create one at: {GITHUB_PAT_URL}\n"
            "Select scopes: repo, workflow (and read:org if needed).\n"
            "Recommended model for GitHub provider: github/copilot\n"
        )
    return None


def cmd_review(_: argparse.Namespace) -> int:
    cwd = Path.cwd()
    staged_files = get_staged_files(cwd)
    if not staged_files:
        print("No staged files found. Run `git add` first.")
        return 1

    staged_diff = get_staged_diff(cwd)
    _ = load_config()

    print("Running local analyzers (when available)...")
    analyzer_reports = run_local_analyzers(cwd)
    for name, report in analyzer_reports:
        short = report.splitlines()[0] if report else ""
        print(f"→ {name}: {short}")

    result = review_staged_changes(staged_files, staged_diff)
    _print_review(result)

    proceed = input("\nProceed with commit? [y/N] ").strip().lower()
    if proceed in {"y", "yes"}:
        return 0
    return 2


def cmd_explain(_: argparse.Namespace) -> int:
    cwd = Path.cwd()
    staged_diff = get_staged_diff(cwd)
    if not staged_diff.strip():
        print("No staged diff found. Run `git add` first.")
        return 1

    prompt = build_explain_prompt(staged_diff)
    print(prompt)
    return 0


def cmd_commit(_: argparse.Namespace) -> int:
    review_code = cmd_review(argparse.Namespace())
    if review_code != 0:
        return review_code

    message = input("Commit message (leave empty for auto-generated):\n> ").strip()
    if not message:
        message = "chore: apply reviewed staged changes"

    proc = subprocess.run(["git", "commit", "-m", message], check=False)
    return proc.returncode


def cmd_hooks_install(_: argparse.Namespace) -> int:
    repo_root = get_repo_root(Path.cwd())
    hook_file = install_pre_commit_hook(repo_root)
    print(f"Installed pre-commit hook at {hook_file}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="gai", description="Git AI review helper")
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init", help="Configure provider and token storage")
    init_parser.set_defaults(func=cmd_init)

    review_parser = subparsers.add_parser("review", help="Review staged changes")
    review_parser.set_defaults(func=cmd_review)

    explain_parser = subparsers.add_parser("explain", help="Print prompt for staged changes")
    explain_parser.set_defaults(func=cmd_explain)

    commit_parser = subparsers.add_parser("commit", help="Review then commit staged changes")
    commit_parser.set_defaults(func=cmd_commit)

    hooks_parser = subparsers.add_parser("hooks", help="Manage git hooks")
    hooks_sub = hooks_parser.add_subparsers(dest="hooks_command", required=True)
    install_parser = hooks_sub.add_parser("install", help="Install pre-commit hook")
    install_parser.set_defaults(func=cmd_hooks_install)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)
