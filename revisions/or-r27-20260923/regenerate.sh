#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../.."
R=revisions/or-r27-20260923
python "$R/propose.py"
python -S "$R/replay.py"
python -S "$R/make_tables.py"
python -S "$R/query_cache.py" --context-id 0 --rho 1/8 --theta -3 4 5 > "$R/results/query_interface_example.json"
