#!/usr/bin/env bash
# F001 item 5 on Linux (WSL): the configured pre-commit gitleaks hook (language: golang, no system Go)
# blocks a staged fake AWS key; a clean staged change passes. Usage: f001_precommit_wsl.sh <bundle>
set -uo pipefail
BUNDLE="$1"
WORK="$(mktemp -d)"; trap 'rm -rf "$WORK"' EXIT
python3 -m venv "$WORK/venv" && "$WORK/venv/bin/pip" install -q pre-commit==4.3.0
export PATH="$WORK/venv/bin:$PATH" PRE_COMMIT_HOME="$WORK/pre-commit-home"
git clone -q "$BUNDLE" "$WORK/repo" -b autodev/F001; cd "$WORK/repo"
git config user.email t@example.invalid; git config user.name throwaway
echo "pre-commit $(pre-commit --version); system go: $(command -v go || echo none)"

echo; echo "### positive control: clean staged change"
echo "clean line" > clean_note.txt; git add clean_note.txt
pre-commit run gitleaks 2>&1; echo "exit=$? (expect 0)"
git reset -q clean_note.txt; rm clean_note.txt

echo; echo "### negative: staged fake AWS key"
KEY="AKIA$(head -c 400 /dev/urandom | tr -dc 'A-Z2-7' | head -c 16)"
mkdir -p src/tmp; printf 'aws_access_key_id = %s\n' "$KEY" > src/tmp/leak.txt; git add src/tmp/leak.txt
pre-commit run gitleaks 2>&1 | sed "s/$KEY/<FAKE-KEY>/g"; echo "exit=${PIPESTATUS[0]} (expect 1)"

echo; echo "### negative via git commit with the hook installed (other hooks skipped via SKIP)"
pre-commit install 2>&1
SKIP=trailing-whitespace,end-of-file-fixer,check-yaml,check-added-large-files,check-merge-conflict,check-toml,debug-statements,mixed-line-ending,ruff,ruff-format,mypy,bandit,poetry-check,pytest-check \
  git commit -q -m "throwaway: leak" 2>&1 | sed "s/$KEY/<FAKE-KEY>/g"; echo "exit=${PIPESTATUS[0]} (expect 1)"
echo "throwaway commit created: $(git log -1 --format=%s | grep -c throwaway) (expect 0)"
