#!/usr/bin/env bash
# Canary test of the pre-push gate: in a throw-away repository, a clean commit must pass
# and every kind of sensitive data must be refused. Fake values are built from fragments
# so this file never contains a literal that the scanner would flag.
set -uo pipefail

here=$(cd "$(dirname "$0")/.." && pwd)
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
fail=0

rand() { LC_ALL=C tr -dc 'A-Za-z0-9' </dev/urandom | head -c "$1" || true; }

check() { # name expected(pass|block) file content
  local name=$1 expected=$2 file=$3 content=$4 repo="$tmp/$1"
  mkdir -p "$repo" && cd "$repo" || exit 2
  git init -q -b main && git config user.email t@example.com && git config user.name t
  cp "$here/.gitleaks.toml" .
  git add .gitleaks.toml && git commit -q -m base
  base=$(git rev-parse HEAD)
  mkdir -p "$(dirname "$file")" && printf '%s\n' "$content" >"$file"
  git add "$file" && git commit -q -m change
  head=$(git rev-parse HEAD)
  if echo "refs/heads/x $head refs/heads/x $base" | "$here/scripts/hooks/pre-push" >/dev/null 2>&1; then
    got=pass
  else
    got=block
  fi
  if [ "$got" = "$expected" ]; then
    echo "ok   $name ($got)"
  else
    echo "FAIL $name: expected $expected, got $got"
    fail=1
  fi
}

check clean-doc pass docs/a.md "Use <MODULE_IP> and <SSH_HOST> from experiments/lab.env."
check github-token block a.txt "token = ghp_$(rand 36)"
check private-ip-192 block a.md "module at 192.168"".1.50"
check private-ip-10 block a.md "gateway 10.""0.0.1"
check private-ip-172 block a.md "host 172.""16.4.9"
check homelab-host block a.md "ssh me@bb-""homelab"
check tailnet-name block a.md "host pi.tail1234.ts"".net"
check home-path block a.md "/home/""someone/project/file"
check personal-email block a.md "contact: someone@gm""ail.com"
check wifi-literal block esphome/a.yaml $'wifi:\n  ssid: "MyHome"'
check wifi-secret pass esphome/a.yaml $'wifi:\n  ssid: !secret wifi_ssid'

# A new branch (remote sha all zeros) must also be scanned.
repo="$tmp/newbranch" && mkdir -p "$repo" && cd "$repo" || exit 2
git init -q -b main && git config user.email t@example.com && git config user.name t
cp "$here/.gitleaks.toml" . && echo "ip 192.168"".9.9" >a.md
git add . && git commit -q -m c && head=$(git rev-parse HEAD)
if echo "refs/heads/n $head refs/heads/n 0000000000000000000000000000000000000000" |
  "$here/scripts/hooks/pre-push" >/dev/null 2>&1; then
  echo "FAIL new-branch: expected block, got pass"; fail=1
else
  echo "ok   new-branch (block)"
fi

# Fail closed when gitleaks is missing.
if echo "refs/heads/n $head refs/heads/n 0000000000000000000000000000000000000000" |
  PATH=/nonexistent /bin/bash "$here/scripts/hooks/pre-push" >/dev/null 2>&1; then
  echo "FAIL missing-gitleaks: expected block, got pass"; fail=1
else
  echo "ok   missing-gitleaks (block)"
fi
exit $fail
