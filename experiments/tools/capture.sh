#!/usr/bin/env bash
# Record the module's SSE event stream into experiments/data/<date>-<slug>.csv.
#
# Usage: capture.sh HOST DURATION_S SLUG [SSH_HOST]
#   HOST        module address, e.g. 192.168.1.123 or espectre-01.local
#   DURATION_S  how long to record, in seconds
#   SLUG        short scenario name, e.g. baseline-empty-house
#   SSH_HOST    optional: run curl on that ssh host (when HOST is on another LAN)
#
# Example: capture.sh 192.168.1.123 600 baseline-empty-house benoit@bb-homelab
set -euo pipefail

if [ "$#" -lt 3 ]; then
  sed -n '2,10p' "$0" >&2
  exit 1
fi

host=$1
duration=$2
slug=$3
ssh_host=${4:-}

tools_dir=$(cd "$(dirname "$0")" && pwd)
data_dir="$tools_dir/../data"
mkdir -p "$data_dir"
out="$data_dir/$(date +%F)-$slug.csv"

curl_cmd="curl -sN --max-time $duration http://$host/events"

echo "timestamp,entity,value" > "$out"
echo "Recording $host for ${duration}s -> $out" >&2
set +e
if [ -n "$ssh_host" ]; then
  # shellcheck disable=SC2029  # client-side expansion is intended: the command is built here
  ssh "$ssh_host" "$curl_cmd" | python3 "$tools_dir/sse_to_csv.py" >> "$out"
else
  $curl_cmd | python3 "$tools_dir/sse_to_csv.py" >> "$out"
fi
stream_status=${PIPESTATUS[0]}
set -e

# curl exits 28 when --max-time elapses: that is the normal end of a run.
# Anything else (ssh refused, host unreachable, HTTP error) is a failed capture.
if [ "$stream_status" -ne 0 ] && [ "$stream_status" -ne 28 ]; then
  echo "Capture failed (exit $stream_status), see messages above" >&2
  exit "$stream_status"
fi

rows=$(( $(wc -l < "$out") - 1 ))
echo "Done: $rows rows in $out" >&2
