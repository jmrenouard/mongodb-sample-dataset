#!/bin/bash
set -euo pipefail

# Import all sample_* NDJSON collections into MongoDB using mongoimport.
usage() {
    cat <<'EOF'
Usage: ./script.sh [host] [port] [username] [password]

Import all sample_*/*.json collections into matching MongoDB databases.

Arguments:
  host      MongoDB hostname or IP address (default: localhost)
  port      MongoDB TCP port (default: 27017)
  username  Optional admin authentication username
  password  Optional admin authentication password (required if username set)

Options:
  -h, --help  Show this help message and exit
EOF
}

if [ "${1:-}" = "-h" ] || [ "${1:-}" = "--help" ]; then
    usage
    exit 0
fi

if ! command -v mongoimport >/dev/null 2>&1; then
    echo "Error: mongoimport command not found in PATH." >&2
    exit 1
fi

HOST="${1:-localhost}"
PORT="${2:-27017}"

auth_args=()
if [ -n "${3:-}" ] || [ -n "${4:-}" ]; then
    if [ -z "${3:-}" ] || [ -z "${4:-}" ]; then
        echo "Error: both username and password must be provided together." >&2
        exit 1
    fi
    echo "Using password authentication!"
    auth_args=(--authenticationDatabase admin -u "$3" -p "$4")
fi

# Restrict imports strictly to sample_* directories to avoid non-dataset files.
shopt -s nullglob
for directory in sample_*; do
    [ -d "$directory" ] || continue
    echo "$directory"
    for data_file in "$directory"/*.json; do
        [ -f "$data_file" ] || continue
        collection="$(basename "$data_file" .json)"
        mongoimport --drop --host "$HOST" --port "$PORT" --db "$directory" --collection "$collection" --file "$data_file" ${auth_args[@]+"${auth_args[@]}"}
    done
done
