# Commit-wise

Open Source Commit and PR reviewer.

## Install

Install the library from PyPI:

```bash
pip install gai-review
```

Install directly from the source repository:

```bash
pip install .
```

Install from GitHub (replace `OWNER` with the repository owner):

```bash
pip install git+https://github.com/gokul-1998/Commit-wise.git
```
 
To Force Reinstall

```base
pip install --force-reinstall --no-cache-dir git+https://github.com/gokul-1998/Commit-wise.git
```


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
