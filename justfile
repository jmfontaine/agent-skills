set quiet := true

_list:
    just --list

# Run formatters
format:
    uvx rumdl fmt

# Check formatting without modifying files
format-check:
    uvx rumdl fmt --check

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

# Run pre-commit on all files
pre-commit:
    uvx prek run --all-files

# Install pre-commit hooks
pre-commit-install:
    uvx prek install

# Update pre-commit hooks to latest versions
pre-commit-update:
    uvx prek autoupdate --freeze

# Run all quality assurance checks
qa: format-check lint terms

# Set local dev environment up
setup:
    uvx prek install  # Install pre-commit hooks

# Check that skills do not use retired workflow terms
terms:
    uvx prek run banned-terms --all-files
