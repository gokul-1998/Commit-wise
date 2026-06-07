from __future__ import annotations

from dataclasses import dataclass

from gai.prompts.review_prompt import build_explain_prompt


@dataclass
class Suggestion:
    severity: str
    file: str
    message: str
    fix: str


@dataclass
class ReviewResult:
    security: bool
    performance: bool
    maintainability: bool
    tests: bool
    suggestions: list[Suggestion]
    score: float


def _suggest_test_file(file_path: str) -> str:
    stem = file_path.rsplit(".", 1)[0].replace("/", "_")
    return f"tests/test_{stem}.py"


def _is_source_file(file_path: str) -> bool:
    lower = file_path.lower()
    if lower.endswith("dockerfile") or lower.endswith("docker-compose.yml"):
        return False
    if lower.endswith(".dockerignore") or lower.endswith(".env") or lower.endswith(".env.example"):
        return False
    if lower.endswith((".md", ".txt", ".yml", ".yaml", ".json", ".lock")):
        return False
    if lower.endswith((".py", ".js", ".ts", ".tsx", ".jsx", ".go", ".java", ".rs", ".c", ".cpp", ".cs", ".php", ".sh", ".bash")):
        return True
    return False


def _is_test_file(file_path: str) -> bool:
    lower = file_path.lower()
    return "test" in lower or "/tests/" in lower or lower.startswith("tests/")


def _call_github_models(staged_diff: str, model: str, token: str) -> str:
    try:
        from azure.ai.inference import ChatCompletionsClient
        from azure.ai.inference.models import SystemMessage, UserMessage
        from azure.core.credentials import AzureKeyCredential
    except ImportError as exc:
        raise RuntimeError(
            "GitHub Models support requires azure-ai-inference and azure-core. "
            "Install them with `pip install azure-ai-inference`."
        ) from exc

    client = ChatCompletionsClient(
        endpoint="https://models.github.ai/inference",
        credential=AzureKeyCredential(token),
    )

    response = client.complete(
        messages=[
            SystemMessage(""),
            UserMessage(build_explain_prompt(staged_diff)),
        ],
        model=model,
    )

    return response.choices[0].message.content or ""


def _local_review_staged_changes(staged_files: list[str], staged_diff: str) -> ReviewResult:
    suggestions: list[Suggestion] = []

    source_files = [path for path in staged_files if _is_source_file(path)]
    has_tests = any(_is_test_file(path) for path in staged_files)
    maintainability_ok = True
    security_ok = True
    performance_ok = True

    lowered = staged_diff.lower()
    if "password" in lowered and "hash" not in lowered:
        security_ok = False
        suggestions.append(
            Suggestion(
                severity="high",
                file="(staged diff)",
                message="Potential raw password handling detected.",
                fix="Ensure password values are hashed and never logged or stored in plain text.",
            )
        )

    if "except:" in staged_diff:
        maintainability_ok = False
        suggestions.append(
            Suggestion(
                severity="medium",
                file="(staged diff)",
                message="Bare except detected.",
                fix="Catch explicit exceptions to avoid hiding unexpected failures.",
            )
        )

    if "for " in staged_diff and "append(" in staged_diff and "set(" in staged_diff:
        performance_ok = False
        suggestions.append(
            Suggestion(
                severity="low",
                file="(staged diff)",
                message="Potentially expensive loop pattern found.",
                fix="Consider using set/dict lookups outside loops where possible.",
            )
        )

    if source_files and not has_tests:
        maintainability_ok = False
        for file_path in source_files[:3]:
            suggestions.append(
                Suggestion(
                    severity="medium",
                    file=file_path,
                    message="No test updates detected for this staged change.",
                    fix=f"Add or update tests, e.g. {_suggest_test_file(file_path)}.",
                )
            )

    if not source_files and not has_tests:
        suggestions.append(
            Suggestion(
                severity="low",
                file="(staged files)",
                message="No source files were changed, so test coverage may not be required.",
                fix="Review configuration, documentation, or deployment updates rather than adding code tests.",
            )
        )

    score = 10.0
    if not security_ok:
        score -= 2.0
    if not performance_ok:
        score -= 1.0
    if not maintainability_ok:
        score -= 1.5
    if source_files and not has_tests:
        score -= 1.0

    return ReviewResult(
        security=security_ok,
        performance=performance_ok,
        maintainability=maintainability_ok,
        tests=has_tests or not source_files,
        suggestions=suggestions,
        score=max(0.0, round(score, 1)),
    )


def review_staged_changes(
    staged_files: list[str],
    staged_diff: str,
    provider: str = "github",
    model: str = "openai/gpt-5",
    token: str | None = None,
) -> ReviewResult | str:
    if provider == "github" and token:
        return _call_github_models(staged_diff, model, token)

    return _local_review_staged_changes(staged_files, staged_diff)
