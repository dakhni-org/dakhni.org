#!/usr/bin/env bash
# loop.sh — run /next-task repeatedly until PLAN.md has no unchecked items.
#
# Usage:
#   bash loop.sh              # default: up to 5 runs, 60s between each
#   MAX_RUNS=10 bash loop.sh  # override run limit
#   SLEEP=30 bash loop.sh     # shorter sleep between runs
#
# Requirements: `claude` CLI must be on PATH and authenticated.
#
# Each run invokes one /next-task turn (one file changed, built, committed, pushed).
# Stop condition: no `- [ ]` lines remain in PLAN.md, or MAX_RUNS is reached.
#
# Logs are written to .claude/loop.log so you can review what ran.

set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="$REPO_DIR/.claude/loop.log"
MAX_RUNS="${MAX_RUNS:-5}"
SLEEP="${SLEEP:-60}"

mkdir -p "$REPO_DIR/.claude"

echo "" >> "$LOG_FILE"
echo "========================================" >> "$LOG_FILE"
echo "loop.sh started at $(date)" >> "$LOG_FILE"
echo "MAX_RUNS=$MAX_RUNS  SLEEP=${SLEEP}s" >> "$LOG_FILE"
echo "========================================" >> "$LOG_FILE"

run=0

while true; do
  # Stop condition: no unchecked tasks remain
  if ! grep -q '^\- \[ \]' "$REPO_DIR/PLAN.md"; then
    echo ""
    echo "All tasks in PLAN.md are complete. Loop finished."
    echo "Loop finished at $(date) — all tasks complete." >> "$LOG_FILE"
    break
  fi

  # Safety cap
  if [ "$run" -ge "$MAX_RUNS" ]; then
    echo ""
    echo "Reached MAX_RUNS=$MAX_RUNS. Stopping."
    echo "Stopped at MAX_RUNS=$MAX_RUNS at $(date). Check PLAN.md for remaining tasks." >> "$LOG_FILE"
    break
  fi

  run=$((run + 1))

  # Show which task is next
  next_task="$(grep '^\- \[ \]' "$REPO_DIR/PLAN.md" | head -1)"
  echo ""
  echo "--- Run $run / $MAX_RUNS  |  $(date) ---"
  echo "Next: $next_task"
  echo ""
  echo "--- Run $run at $(date) ---" >> "$LOG_FILE"
  echo "Task: $next_task" >> "$LOG_FILE"

  # Run one agent turn
  cd "$REPO_DIR"
  claude --dangerously-skip-permissions -p "/next-task" 2>&1 | tee -a "$LOG_FILE"

  echo ""
  echo "Run $run complete."
  echo "Run $run complete at $(date)." >> "$LOG_FILE"

  # Sleep between runs to respect rate limits (skip sleep after last run)
  if grep -q '^\- \[ \]' "$REPO_DIR/PLAN.md" && [ "$run" -lt "$MAX_RUNS" ]; then
    echo "Sleeping ${SLEEP}s before next run..."
    sleep "$SLEEP"
  fi
done

echo ""
# Print final progress summary
total=$(grep -c '^\- \[' "$REPO_DIR/PLAN.md" || true)
done_count=$(grep -c '^\- \[x\]' "$REPO_DIR/PLAN.md" || true)
remaining=$(grep -c '^\- \[ \]' "$REPO_DIR/PLAN.md" || true)
echo "Summary: $done_count / $total tasks done, $remaining remaining."
echo "Summary: $done_count/$total done, $remaining remaining." >> "$LOG_FILE"
