#!/usr/bin/env bash
# Record the module's SSE event stream into experiments/data/<date>-<slug>.csv.
#
# Usage: capture.sh HOST DURATION_S SLUG [SSH_HOST]
#   HOST        module address, e.g. <MODULE_IP> or espectre-01.local
#   DURATION_S  how long to record, in seconds
#   SLUG        short scenario name (letters, digits, - _), e.g. baseline-empty-house
#   SSH_HOST    optional: run curl on that ssh host (when HOST is on another LAN)
#
# Example: capture.sh <MODULE_IP> 600 baseline-empty-house <SSH_HOST>
set -euo pipefail

if [ "$#" -lt 3 ]; then
  sed -n '2,10p' "$0" >&2
  exit 1
fi

host=$1
duration=$2
slug=$3
ssh_host=${4:-}

# The host and duration are re-parsed by a remote shell when SSH_HOST is used, and the
# slug becomes a file name: restrict all three to harmless characters.
[[ $host =~ ^[A-Za-z0-9.:-]+$ ]] || { echo "HOST must be a hostname or IP" >&2; exit 2; }
[[ $duration =~ ^[0-9]+$ ]] || { echo "DURATION_S must be an integer" >&2; exit 2; }
[[ $slug =~ ^[A-Za-z0-9_-]+$ ]] || { echo "SLUG: letters, digits, - _ only" >&2; exit 2; }
[[ $ssh_host != -* ]] || { echo "SSH_HOST must not start with -" >&2; exit 2; }

tools_dir=$(cd "$(dirname "$0")" && pwd)
data_dir="$tools_dir/../data"
mkdir -p "$data_dir"
out="$data_dir/$(date +%F)-$slug.csv"
if [ -e "$out" ]; then
  echo "$out already exists: pick another SLUG (a rerun must not erase a capture)" >&2
  exit 1
fi

# -f: an HTTP error is a failure, not an empty capture. --connect-timeout: an unreachable
# host fails fast instead of waiting the whole duration.
curl_cmd="curl -sfN --connect-timeout 5 --max-time $duration http://$host/events"

echo "Recording $host for ${duration}s -> $out" >&2
set +e
if [ -n "$ssh_host" ]; then
  # shellcheck disable=SC2029  # client-side expansion is intended: the command is built here
  ssh -- "$ssh_host" "$curl_cmd" | python3 "$tools_dir/sse_to_csv.py" > "$out"
else
  # unquoted on purpose: $curl_cmd is a command line, split by the shell
  $curl_cmd | python3 "$tools_dir/sse_to_csv.py" > "$out"
fi
statuses=("${PIPESTATUS[@]}")
set -e

# curl exits 28 when --max-time elapses: that is the normal end of a run.
# Anything else (ssh refused, host unreachable, HTTP error, converter crash) is a failure.
if [ "${statuses[0]}" -ne 0 ] && [ "${statuses[0]}" -ne 28 ]; then
  echo "Capture failed (curl/ssh exit ${statuses[0]}), see messages above" >&2
  exit "${statuses[0]}"
fi
if [ "${statuses[1]}" -ne 0 ]; then
  echo "Capture failed (sse_to_csv.py exit ${statuses[1]})" >&2
  exit "${statuses[1]}"
fi

rows=$(( $(wc -l < "$out") - 1 ))
if [ "$rows" -le 0 ]; then
  echo "No data captured from $host (is the module up and the address right?)" >&2
  exit 1
fi
echo "Done: $rows rows in $out" >&2
