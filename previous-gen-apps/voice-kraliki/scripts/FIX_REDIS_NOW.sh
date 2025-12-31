#!/bin/bash

# IMMEDIATE REDIS SECURITY FIX
# Copy and run this entire script to fix Redis

echo "Starting Redis security fix..."
cd /home/adminmatej/github/applications/operator-demo-2026

# Run the guided fix script
bash scripts/guided-redis-fix.sh

echo ""
echo "Done! Check output above for results."
