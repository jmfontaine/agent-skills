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
qa: format-check lint

# Set local dev environment up
setup:
    uvx prek install  # Install pre-commit hooks
