#!/usr/bin/env bash
# F001 item 5: the configured pre-commit gitleaks hook blocks a fake key; positive control passes.
# Usage: f001_precommit.sh <repo> <scratch>
set -uo pipefail
REPO="$1"; SCR="$2"
export PRE_COMMIT_HOME="$SCR/pre-commit-home"
# Windows: some hook repos (poetry) exceed MAX_PATH; enable long paths for this process only.
export GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=core.longpaths GIT_CONFIG_VALUE_0=true
C="$SCR/clone-precommit"; rm -rf "$C"; git clone -q "$REPO" "$C" 2>/dev/null
cd "$C"
git config user.email t@example.invalid; git config user.name throwaway
git config --unset core.hooksPath 2>/dev/null || true
echo "pre-commit $(pre-commit --version); system go: $(command -v go || echo none)"

echo; echo "### positive control: clean staged change"
echo "clean line" > clean_note.txt; git add clean_note.txt
pre-commit run gitleaks 2>&1; echo "exit=$? (expect 0)"
git reset -q clean_note.txt; rm clean_note.txt

echo; echo "### negative: staged fake AWS key"
KEY="AKIA$(head -c 400 /dev/urandom | tr -dc 'A-Z2-7' | head -c 16)"
mkdir -p src/tmp; printf 'aws_access_key_id = %s\n' "$KEY" > src/tmp/leak.txt; git add src/tmp/leak.txt
pre-commit run gitleaks 2>&1 | sed "s/$KEY/<FAKE-KEY>/g"; echo "exit=${PIPESTATUS[0]} (expect 1)"

echo; echo "### negative via git commit (only the gitleaks hook, other hooks skipped)"
pre-commit install 2>&1
SKIP=trailing-whitespace,end-of-file-fixer,check-yaml,check-added-large-files,check-merge-conflict,check-toml,debug-statements,mixed-line-ending,ruff,ruff-format,mypy,bandit,poetry-check,pytest-check \
  git commit -q -m "throwaway: leak" 2>&1 | sed "s/$KEY/<FAKE-KEY>/g"; echo "exit=${PIPESTATUS[0]} (expect 1)"
echo "commit created: $(git log -1 --format=%s | grep -c throwaway) (expect 0)"
cd "$SCR"; rm -rf "$C"
