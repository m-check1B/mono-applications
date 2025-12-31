#!/usr/bin/env bash
set -e
pnpm env:validate || true
pnpm status:json || true
echo "✅ Dev environment check executed."

