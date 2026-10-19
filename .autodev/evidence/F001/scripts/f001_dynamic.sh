#!/usr/bin/env bash
# F001 dynamic checks (items 2, 3, 4) in a throwaway clone. Usage: f001_dynamic.sh <repo> <scratch> <gitleaks>
set -uo pipefail
REPO="$1"; SCR="$2"; GL="$3"
CFG="$REPO/.gitleaks.toml"
fake_key() { echo "AKIA$(head -c 400 /dev/urandom | tr -dc 'A-Z2-7' | head -c 16)"; }

echo "### item 2: clean export of HEAD ($(git -C "$REPO" rev-parse --short HEAD))"
X="$SCR/export-head"; rm -rf "$X"; mkdir -p "$X"
git -C "$REPO" archive HEAD | tar -x -C "$X"
"$GL" dir "$X" --config "$CFG" --redact --no-banner 2>&1 | sed "s#$SCR#<scratch>#g"; echo "exit=${PIPESTATUS[0]} (expect 0)"

echo; echo "### item 3: branch commits 164e7df..HEAD"
"$GL" git --log-opts="164e7df..HEAD" --config "$CFG" --redact --no-banner "$REPO" 2>&1; echo "exit=${PIPESTATUS[0]} (expect 0)"

echo; echo "### item 4: allowlist behaviour in a throwaway clone"
C="$SCR/clone-allowlist"; rm -rf "$C"; git clone -q "$REPO" "$C"
git -C "$C" config user.email t@example.invalid; git -C "$C" config user.name throwaway
KEY="$(fake_key)"
mkdir -p "$C/tests/fixtures/secrets" "$C/src/tmp"
printf 'aws_access_key_id = %s\n' "$KEY" > "$C/tests/fixtures/secrets/fake_aws.txt"
cp "$C/tests/fixtures/secrets/fake_aws.txt" "$C/src/tmp/leak.txt"
HIGH="$(head -c 400 /dev/urandom | tr -dc 'A-Za-z0-9' | head -c 32)"
printf 'tokenizer_name = "%s"\n' "$HIGH" > "$C/src/tmp/near_allowlist.py"
git -C "$C" add -A; git -C "$C" commit -q -m "throwaway: fake secrets"
for mode in dir git; do
  if [ "$mode" = dir ]; then
    "$GL" dir "$C" --config "$CFG" --redact --no-banner --report-format json --report-path "$SCR/r-$mode.json" >/dev/null 2>&1; rc=$?
  else
    "$GL" git --log-opts="HEAD~1..HEAD" --config "$CFG" --redact --no-banner --report-format json --report-path "$SCR/r-$mode.json" "$C" >/dev/null 2>&1; rc=$?
  fi
  echo "-- mode=$mode exit=$rc (expect 1)"
  python -I - "$SCR/r-$mode.json" <<'PY'
import json, sys
findings = json.load(open(sys.argv[1]))
files = sorted({(f["RuleID"], f["File"].replace("\\", "/").split("clone-allowlist/")[-1]) for f in findings})
for rule, path in files:
    print(f"   finding: {rule} {path}")
fixture = any("tests/fixtures/secrets/" in p for _, p in files)
leak = any(r == "aws-access-token" and p.endswith("src/tmp/leak.txt") for r, p in files)
near = any(p.endswith("src/tmp/near_allowlist.py") for _, p in files)
print(f"   fixture reported: {fixture} (expect False); same key elsewhere reported: {leak} (expect True); "
      f"non-allowlisted tokenizer_name value reported: {near} (expect True)")
sys.exit(0 if (not fixture and leak and near) else 1)
PY
  echo "   check=$?"
done
rm -rf "$C"
