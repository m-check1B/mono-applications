#!/bin/bash
echo "=== PM2 Status ==="
pm2 jlist | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'Processes: {len(d)}, Online: {sum(1 for p in d if p[\"pm2_env\"][\"status\"]==\"online\")}')"

echo -e "\n=== Circuit Breakers ==="
cat /home/adminmatej/github/applications/kraliki-lab/kraliki-swarm/control/circuit-breakers.json | python3 -c "import sys,json; d=json.load(sys.stdin); [print(f'{k}: {v[\"state\"]}') for k,v in d.items()]"

echo -e "\n=== Recent Agent Activity ==="
ls -lt /home/adminmatej/github/applications/kraliki-lab/kraliki-swarm/logs/agents/*.log 2>/dev/null | head -5
