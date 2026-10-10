#!/usr/bin/env bash
# Collect the mechanical baseline for a Python codebase review: file inventory,
# lint, type check, and tests with coverage. Each step records its exit code and
# keeps going, so one failing tool never hides the others.
#
# Usage: baseline.sh [OUT_DIR]   (run from the repository root)
# Prints OUT_DIR on the last line. Writes inventory.txt, ruff.txt, types.txt,
# tests.txt, and summary.txt there. Never modifies tracked files.
set -uo pipefail

out="${1:-$(mktemp -d "${TMPDIR:-/tmp}/pyreview.XXXXXX")}"
mkdir -p "$out"
summary="$out/summary.txt"
: >"$summary"

has() { command -v "$1" >/dev/null 2>&1; }

# Run project tools through the project's environment when one exists.
if [[ -f uv.lock ]] && has uv; then
	uvmode=1
	uv sync --frozen --all-extras --all-groups >"$out/sync.txt" 2>&1 || uv sync --frozen >>"$out/sync.txt" 2>&1
	run() { uv run --frozen "$@"; }
	pyexe=$(uv run --frozen python -c 'import sys; print(sys.executable)' 2>/dev/null | tail -n 1)
	run_with() { local pkgs=(); while [[ $1 != -- ]]; do pkgs+=(--with "$1"); shift; done; shift; uv run --frozen "${pkgs[@]}" "$@"; }
elif [[ -x .venv/bin/python ]]; then
	run() { .venv/bin/python -m "$@"; }
	pyexe=$PWD/.venv/bin/python
	run_with() { while [[ $1 != -- ]]; do shift; done; shift; .venv/bin/python -m "$@"; }
else
	run() { python3 -m "$@"; }
	pyexe=$(command -v python3)
	run_with() { while [[ $1 != -- ]]; do shift; done; shift; python3 -m "$@"; }
fi

step() { # step NAME FILE CMD...
	local name=$1 file=$2; shift 2
	"$@" >"$out/$file" 2>&1
	local rc=$?
	printf '%-13s exit=%-3s %s (%s lines)\n' "$name" "$rc" "$out/$file" "$(wc -l <"$out/$file" | tr -d ' ')" >>"$summary"
}

# Inventory: Python line counts per top-level directory, for slicing.
inventory() {
	local files
	if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
		files=$(git ls-files -- '*.py' '*.pyi')
	else
		files=$(find . -name '*.py' -not -path '*/.*' -not -path '*/node_modules/*')
	fi
	[[ -z $files ]] && { echo "no Python files"; return 1; }
	echo "$files" | tr '\n' '\0' | xargs -0 wc -l | grep -v ' total$' |
		awk '{n=split($2,p,"/"); d=(n>2)?p[1]"/"p[2]:(n>1?p[1]:"."); s[d]+=$1; t+=$1} END {for (k in s) printf "%8d  %s\n", s[k], k; printf "%8d  TOTAL\n", t}' |
		sort -rn
}
step inventory inventory.txt inventory

# Lint: uvx ruff reads the project's ruff config, so no install is needed.
if has uvx; then
	step ruff ruff.txt uvx ruff check --output-format concise --no-fix .
else
	step ruff ruff.txt run ruff check --output-format concise --no-fix .
fi

# Type check: honour the project's configured checker, else basedpyright.
checker=basedpyright
if [[ -f mypy.ini || -f .mypy.ini ]] || grep -qs '^\[tool\.mypy' pyproject.toml || grep -qs '^\[mypy' setup.cfg; then
	checker=mypy
elif grep -qs '^\[tool\.ty' pyproject.toml || [[ -f ty.toml ]]; then
	checker=ty
elif [[ -f pyrightconfig.json ]] || grep -qs '^\[tool\.pyright' pyproject.toml; then
	checker=pyright
fi
case $checker in
mypy) step mypy types.txt run_with mypy -- mypy . ;;
ty) step ty types.txt uvx ty check ${pyexe:+--python "$pyexe"} ;;
pyright) step pyright types.txt uvx pyright ${pyexe:+--pythonpath "$pyexe"} ;;
*) step basedpyright types.txt uvx basedpyright ${pyexe:+--pythonpath "$pyexe"} ;;
esac

# Tests with coverage; pytest also runs unittest-style suites. Coverage data and
# the pytest cache stay out of the repository.
export COVERAGE_FILE="$out/.coverage"
cov=(--cov --cov-report=term-missing:skip-covered)
# Outside uv, pytest-cov cannot be injected; run without coverage if it is missing.
if [[ -z ${uvmode:-} ]] && ! "$pyexe" -c 'import pytest_cov' 2>/dev/null; then
	cov=()
	echo "coverage: pytest-cov not installed in $pyexe, skipped" >>"$summary"
fi
step pytest tests.txt run_with pytest pytest-cov -- pytest -q -p no:cacheprovider "${cov[@]}"

echo "type checker: $checker" >>"$summary"
cat "$summary"
echo "$out"
