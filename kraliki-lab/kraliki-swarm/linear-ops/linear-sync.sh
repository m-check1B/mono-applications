#!/bin/bash
set -euo pipefail

GIN_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
python3 "$GIN_DIR/linear-sync.py" "$@"
