#!/usr/bin/env bash
set -euo pipefail

usage() {
  printf '%s\n' \
    'Usage: export_logs.sh --project PROJECT_ID --filter QUERY --output FILE [--freshness DURATION] [--limit COUNT]' \
    'Exports matching Cloud Logging entries as a JSON array.'
}

project=''
filter=''
output=''
freshness='30d'
limit=''

while [[ $# -gt 0 ]]; do
  case "$1" in
    --project) project="$2"; shift 2 ;;
    --filter) filter="$2"; shift 2 ;;
    --output) output="$2"; shift 2 ;;
    --freshness) freshness="$2"; shift 2 ;;
    --limit) limit="$2"; shift 2 ;;
    --help|-h) usage; exit 0 ;;
    *) usage >&2; exit 2 ;;
  esac
done

if [[ -z "$project" || -z "$filter" || -z "$output" ]]; then
  usage >&2
  exit 2
fi

if ! command -v gcloud >/dev/null 2>&1; then
  printf '%s\n' 'gcloud is required but was not found on PATH.' >&2
  exit 127
fi

output_dir="$(dirname "$output")"
mkdir -p "$output_dir"

command=(gcloud logging read "$filter" --project="$project" --freshness="$freshness" --order=desc --format=json)
if [[ -n "$limit" ]]; then
  command+=(--limit="$limit")
fi

"${command[@]}" > "$output"
python3 -c 'import json, pathlib, sys; entries=json.loads(pathlib.Path(sys.argv[1]).read_text()); print(f"Exported {len(entries)} entries to {sys.argv[1]}")' "$output"
