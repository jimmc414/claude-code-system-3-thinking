#!/bin/bash
# ~/.sophia/hooks/log_action.sh
# Log tool actions to session buffer
# Fire-and-forget: never wait for I/O

set -e

# Read tool result from stdin
INPUT=$(cat)

# Session buffer file (in /tmp for speed)
SESSION_ID="${CLAUDE_SESSION_ID:-$(date +%Y%m%d_%H%M%S)}"
BUFFER_FILE="/tmp/sophia_session_${SESSION_ID}.jsonl"

# Extract relevant data
TOOL_NAME="${CLAUDE_TOOL_NAME:-unknown}"
TIMESTAMP=$(date -Iseconds)
EXIT_CODE="${CLAUDE_TOOL_EXIT_CODE:-0}"

# Create log entry (minimal fields for speed)
LOG_ENTRY=$(cat <<EOF
{"ts":"$TIMESTAMP","tool":"$TOOL_NAME","exit":$EXIT_CODE,"args_hash":"$(echo "$INPUT" | md5sum | cut -d' ' -f1)"}
EOF
)

# Append to buffer (fire-and-forget, no fsync)
echo "$LOG_ENTRY" >> "$BUFFER_FILE" &

# Exit immediately
exit 0
