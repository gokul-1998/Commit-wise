from __future__ import annotations


def build_explain_prompt(staged_diff: str) -> str:
    return """You are a Staff Software Engineer.

Review ONLY the staged changes.

Consider:
1. Bugs
2. Security
3. Performance
4. Readability
5. Architecture consistency
6. Error handling
7. Missing tests
8. Backward compatibility

Provide:
- Severity
- File
- Explanation
- Suggested fix
- Code snippet
- Overall score (/10)

Do not comment on formatting issues already covered by Ruff.

Staged diff:
""" + staged_diff
