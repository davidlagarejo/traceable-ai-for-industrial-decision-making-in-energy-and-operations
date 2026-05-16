#!/bin/bash
# ZLab Dashboard launcher — always runs the LIVE dashboard.py from the repo.
# Updated 2026-05-16 for V10 P3 (industry corpus + regulatory + evidence wire).

DASHBOARD="/Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/runtime-orchestrator/dashboard.py"
PORT=7474
LOG="$HOME/.zlab_dashboard.log"

# Kill any existing process on this port (in case a previous launch left
# a stale process — we want to ALWAYS run the freshest dashboard.py).
EXISTING_PID=$(lsof -ti :$PORT 2>/dev/null)
if [ -n "$EXISTING_PID" ]; then
    echo "$(date -u +%FT%TZ) — killing existing PID $EXISTING_PID on :$PORT" >> "$LOG"
    kill "$EXISTING_PID" 2>/dev/null
    sleep 2
    # If still alive, force
    if kill -0 "$EXISTING_PID" 2>/dev/null; then
        kill -9 "$EXISTING_PID" 2>/dev/null
        sleep 1
    fi
fi

# Sanity check the dashboard.py exists
if [ ! -f "$DASHBOARD" ]; then
    osascript -e 'display alert "ZLab Dashboard" message "dashboard.py not found at expected path. Check /Volumes/ZLab_Run mount."'
    exit 1
fi

# Start fresh
echo "$(date -u +%FT%TZ) — starting dashboard $DASHBOARD --port $PORT" >> "$LOG"
nohup python3 "$DASHBOARD" --port $PORT --open >> "$LOG" 2>&1 &
NEW_PID=$!
echo "$(date -u +%FT%TZ) — launched PID $NEW_PID" >> "$LOG"

# Give the server a couple seconds to bind, then open the browser if --open
# didn't already (defensive).
sleep 2
if ! lsof -ti :$PORT >/dev/null 2>&1; then
    osascript -e 'display alert "ZLab Dashboard" message "Server failed to start. Check ~/.zlab_dashboard.log"'
    exit 1
fi
