#!/usr/bin/env bash
# F001 item 6: run the run: blocks of .github/workflows/secret-scan.yml verbatim on Linux (WSL)
# against throwaway commits, with the env vars GitHub would set. Proves script logic only.
# Usage (inside WSL): f001_ci_wsl.sh <bundle>
set -uo pipefail
BUNDLE="$1"
WORK="$(mktemp -d)"; trap 'rm -rf "$WORK"' EXIT
git clone -q "$BUNDLE" "$WORK/repo" -b autodev/F001
cd "$WORK/repo"
git config user.email t@example.invalid; git config user.name throwaway
python3 - "$WORK" <<'PY'
import sys, yaml
work = sys.argv[1]
wf = yaml.safe_load(open(".github/workflows/secret-scan.yml"))
steps = [s for s in wf["jobs"]["gitleaks"]["steps"] if "run" in s]
assert [s["name"] for s in steps] == ["Install gitleaks 8.24.3 (checksum-verified)", "Scan commits and tree"]
open(f"{work}/install.sh", "w").write(steps[0]["run"])
open(f"{work}/scan.sh", "w").write(steps[1]["run"])
PY
echo "### install step (verbatim)"
export RUNNER_TEMP="$WORK/runner-temp"; mkdir -p "$RUNNER_TEMP"
export GITHUB_PATH="$WORK/github_path"; : > "$GITHUB_PATH"
bash -e "$WORK/install.sh"; echo "install exit=$?"
export PATH="$(cat "$GITHUB_PATH"):$PATH"

scan() {  # name expected EVENT BASE HEAD BEFORE AFTER
  local name="$1" expected="$2"
  echo; echo "### scenario: $name (expect exit $expected)"
  EVENT_NAME="$3" BASE_SHA="$4" HEAD_SHA="$5" BEFORE_SHA="$6" AFTER_SHA="$7" \
    bash -e "$WORK/scan.sh" 2>&1 | sed -E 's/AKIA[A-Z2-7]{16}/<FAKE-KEY>/g'
  local rc=${PIPESTATUS[0]}
  echo "exit=$rc -> $([ "$rc" = "$expected" ] && echo OK || echo MISMATCH)"
}
fake_key() { echo "AKIA$(head -c 400 /dev/urandom | tr -dc 'A-Z2-7' | head -c 16)"; }

BASE="$(git rev-parse HEAD)"

git checkout -q -b pr-clean "$BASE"
echo "clean change" > clean_note.txt; git add clean_note.txt; git commit -q -m "throwaway: clean"
scan "pull_request, clean commit" 0 pull_request "$BASE" "$(git rev-parse HEAD)" "" ""

git checkout -q -b pr-leak "$BASE"
mkdir -p src/tmp; printf 'aws_access_key_id = %s\n' "$(fake_key)" > src/tmp/leak.txt
git add src/tmp/leak.txt; git commit -q -m "throwaway: leak"
scan "pull_request, commit adds fake AWS key" 1 pull_request "$BASE" "$(git rev-parse HEAD)" "" ""

git checkout -q -b pr-widen "$BASE"
mkdir -p src/tmp; printf 'aws_access_key_id = %s\n' "$(fake_key)" > src/tmp/leak.txt
sed -i "s#^paths = \[.*#paths = ['''(^|/)tests/fixtures/secrets/''', '''src/tmp/''']#" .gitleaks.toml
grep -n "^paths" .gitleaks.toml
git add -A; git commit -q -m "throwaway: leak plus widened allowlist in the PR head"
scan "pull_request, PR widens its own allowlist and leaks" 1 pull_request "$BASE" "$(git rev-parse HEAD)" "" ""

git checkout -q pr-clean
scan "push, new branch (before is all zeros), clean tree" 0 push "" "" "0000000000000000000000000000000000000000" "$(git rev-parse HEAD)"
scan "push, unreachable before (force-push), clean tree" 0 push "" "" "1111111111111111111111111111111111111111" "$(git rev-parse HEAD)"
scan "push, normal range, clean" 0 push "" "" "$BASE" "$(git rev-parse HEAD)"
git checkout -q pr-leak
scan "push, normal range, leak" 1 push "" "" "$BASE" "$(git rev-parse HEAD)"
