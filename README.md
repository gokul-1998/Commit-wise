# Commit-wise

Open Source Commit and PR reviewer.

## CLI MVP (`gai`)

This repository now includes a minimal local CLI for staged-change review.

### Commands

```bash
gai init
gai review
gai explain
gai commit
gai hooks install
```

### What `gai review` does

- Reads staged files from `git diff --cached --name-only`
- Reads staged diff from `git diff --cached`
- Runs local analyzers when installed (`ruff`, `mypy`, `pytest`, `bandit`)
- Prints actionable review suggestions and score in terminal

### Security

`gai init` stores provider tokens in the system keyring (`keyring` package), not in plain-text config.
