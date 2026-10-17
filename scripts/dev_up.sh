#!/bin/bash
# One-command dev bring-up: FalkorDB + API + seed. Safe to re-run.
cd "$(dirname "$0")/.."
if ! pgrep -f "redis-server.*6379" >/dev/null; then /home/sandbox/falkor/start_db.sh; sleep 2; fi
if ! pgrep -f "uvicorn aftershock" >/dev/null; then nohup python3 -m uvicorn aftershock.api:app --port 8000 > /tmp/api.log 2>&1 & sleep 3; fi
curl -s -X POST localhost:8000/api/reset && echo " - aftershock up on :8000"
