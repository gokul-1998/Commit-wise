from __future__ import annotations

import os
from pathlib import Path

CONFIG_DIR = Path.home() / ".gai"
CONFIG_FILE = CONFIG_DIR / "config.toml"


def _toml_dumps(data: dict[str, str]) -> str:
    lines = []
    for key, value in data.items():
        escaped = value.replace('"', '\\"')
        lines.append(f'{key}="{escaped}"')
    return "\n".join(lines) + "\n"


def save_config(config: dict[str, str]) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(_toml_dumps(config), encoding="utf-8")


def load_config() -> dict[str, str]:
    if not CONFIG_FILE.exists():
        return {}

    text = CONFIG_FILE.read_text(encoding="utf-8")
    result: dict[str, str] = {}
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, raw_value = line.partition("=")
        value = raw_value.strip().strip('"')
        result[key.strip()] = value
    return result


def set_token(provider: str, token: str) -> None:
    try:
        import keyring  # type: ignore
    except Exception as exc:  # pragma: no cover - import guard
        raise RuntimeError(
            "keyring is required for secure token storage. Install it with `pip install keyring`."
        ) from exc

    keyring.set_password("gai", provider, token)


def get_token(provider: str) -> str | None:
    try:
        import keyring  # type: ignore
    except Exception:
        return None
    return keyring.get_password("gai", provider)
