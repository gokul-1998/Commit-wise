from __future__ import annotations

from dataclasses import dataclass


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


def review_staged_changes(staged_files: list[str], staged_diff: str) -> ReviewResult:
    suggestions: list[Suggestion] = []

    has_tests = any("test" in path.lower() for path in staged_files)
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

    if not has_tests:
        maintainability_ok = False
        for file_path in staged_files[:3]:
            if "test" in file_path.lower():
                continue
            suggestions.append(
                Suggestion(
                    severity="medium",
                    file=file_path,
                    message="No test updates detected for this staged change.",
                    fix=f"Add or update tests, e.g. {_suggest_test_file(file_path)}.",
                )
            )

    score = 10.0
    if not security_ok:
        score -= 2.0
    if not performance_ok:
        score -= 1.0
    if not maintainability_ok:
        score -= 1.5
    if not has_tests:
        score -= 1.0

    return ReviewResult(
        security=security_ok,
        performance=performance_ok,
        maintainability=maintainability_ok,
        tests=has_tests,
        suggestions=suggestions,
        score=max(0.0, round(score, 1)),
    )
