#!/usr/bin/env bash
# Record manual ground-truth marks into experiments/data/<date>-<slug>.marks.csv.
# Run it next to capture.sh with the same SLUG, then press:
#   m  -> "moving"  (someone is moving in the sensed area from now on)
#   s  -> "still"   (the area is still from now on)
#   q  -> quit
# A mark holds until the next one. A run without marks is treated as still throughout.
#
# Usage: mark.sh SLUG
set -euo pipefail

if [ "$#" -ne 1 ]; then
  sed -n '2,9p' "$0" >&2
  exit 1
fi

slug=$1
# The slug becomes a file name: same restriction as capture.sh.
[[ $slug =~ ^[A-Za-z0-9_-]+$ ]] || { echo "SLUG: letters, digits, - _ only" >&2; exit 2; }
tools_dir=$(cd "$(dirname "$0")" && pwd)
data_dir="$tools_dir/../data"
mkdir -p "$data_dir"
out="$data_dir/$(date +%F)-$slug.marks.csv"

[ -f "$out" ] || echo "timestamp,label" > "$out"
echo "Marks -> $out   [m] moving  [s] still  [q] quit" >&2

while IFS= read -r -s -n1 key; do
  case "$key" in
    m) label=moving ;;
    s) label=still ;;
    q) break ;;
    *) continue ;;
  esac
  stamp=$(date +%Y-%m-%dT%H:%M:%S.%3N%:z)  # GNU date (Linux / the Pi); not macOS
  echo "$stamp,$label" >> "$out"
  echo "$stamp $label" >&2
done
