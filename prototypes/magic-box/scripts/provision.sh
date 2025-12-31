#!/usr/bin/env bash
# Wrapper to run the full Magic Box setup script.
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"

exec "${SCRIPT_DIR}/setup-complete.sh" "$@"
