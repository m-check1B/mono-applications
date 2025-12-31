#!/bin/bash
# Sync Linear issues to local cache
cd /home/adminmatej/github/applications/kraliki-lab/kraliki-swarm
python3 integrations/linear_sync.py --once
echo "Linear sync complete"
