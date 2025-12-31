#!/bin/bash
# Retry pending Linear issues

KRALIKI_DIR="/home/adminmatej/github/applications/kraliki-lab/kraliki-swarm"
SCRIPT="$KRALIKI_DIR/integrations/linear_pending_retry.py"

# Pass all arguments to the Python script
python3 "$SCRIPT" "$@"
