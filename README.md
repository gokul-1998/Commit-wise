# Commit-wise

Open Source Commit and PR reviewer.

## Install

Install the library from PyPI:

```bash
pip install commitwise-review
```

Install directly from the source repository:

```bash
pip install .
```

Install from GitHub:

```bash
pip install git+https://github.com/gokul-1998/Commit-wise.git
```

To force reinstall:

```bash
pip install --force-reinstall --no-cache-dir git+https://github.com/gokul-1998/Commit-wise.git
```

## Versioning

This project uses Semantic Versioning:

```bash
MAJOR.MINOR.PATCH
```

Example release plan:

- `0.1.0` — initial release
- `0.2.0` — new features
- `0.2.1` — bug fixes and prompt improvements
- `1.0.0` — stable public release

## CLI MVP (`commit-wise`)

This repository now includes a minimal local CLI for staged-change review.

### Commands

```bash
commit-wise init
commit-wise review
commit-wise explain
commit-wise commit
commit-wise hooks install
```

The old `gai` alias is still available:

```bash
gai init
gai review
gai explain
gai commit
gai hooks install
```

### What `commit-wise review` does

- Reads staged files from `git diff --cached --name-only`
- Reads staged diff from `git diff --cached`
- Runs local analyzers when installed (`ruff`, `mypy`, `pytest`, `bandit`)
- Prints actionable review suggestions and score in terminal

### Security

`gai init` stores provider tokens in the system keyring (`keyring` package), not in plain-text config.
