---
name: uv
description: Python package management with uv. Use when installing, adding, removing, upgrading, or syncing Python dependencies.
allowed-tools: Bash(uv add:*) Bash(uv remove:*) Bash(uv sync:*)
---

# Python Package Management With uv

- Always use `uv` to manage Python packages. Never edit dependency tables in
  `pyproject.toml` by hand; use `uv add` and `uv remove`
- Use `--group <group>` to target a dependency group (e.g., `dev`, `test`)
- If `uv` is not available, link to
  [installation docs](https://docs.astral.sh/uv/#installation) and stop
