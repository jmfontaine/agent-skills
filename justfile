set quiet := true

_list:
    just --list

# Run formatters
format:
    uvx rumdl fmt

# Run linter
lint:
    uvx rumdl check

# Run linter and fix issues
lint-fix:
    uvx rumdl check --fix

# Package each skill as a ZIP in dist/ for Claude and ChatGPT
package:
    #!/usr/bin/env bash
    set -euo pipefail
    rm -rf dist
    mkdir dist
    cd skills
    for skill in */; do
        skill="${skill%/}"
        zip -qr "../dist/$skill.zip" "$skill" -x '*.DS_Store' '*/__pycache__/*' '*.pyc'
        echo "dist/$skill.zip"
    done

# Install pre-commit hooks
pre-commit-install:
    uvx prek install

# Update pre-commit hooks to latest versions
pre-commit-update:
    uvx prek autoupdate --freeze

# Run all quality assurance checks, with the hook versions CI uses (tracked files only)
qa:
    uvx prek run --all-files

# Set local dev environment up
setup:
    uvx prek install  # Install pre-commit hooks

# Check spelling against cspell.json, the word list VS Code also uses
spell:
    uvx prek run cspell --all-files
