#!/bin/bash
# ~/.sophia/hooks/session_end.sh
# Commit session to episode, update stats

set -e

SOPHIA_DIR="$HOME/.sophia"
SESSION_ID="${CLAUDE_SESSION_ID:-$(date +%Y%m%d_%H%M%S)}"
BUFFER_FILE="/tmp/sophia_session_${SESSION_ID}.jsonl"

# Check if buffer exists and has content
if [[ ! -f "$BUFFER_FILE" ]] || [[ ! -s "$BUFFER_FILE" ]]; then
    # No actions logged, skip episode creation
    exit 0
fi

# Count tool calls
TOOL_COUNT=$(wc -l < "$BUFFER_FILE")

# Skip trivial sessions (<2 tool calls)
if [[ "$TOOL_COUNT" -lt 2 ]]; then
    rm -f "$BUFFER_FILE"
    exit 0
fi

# Generate episode ID
EPISODE_ID="ep_$(date +%Y%m%d_%H%M%S)_$(head -c 4 /dev/urandom | xxd -p)"
TIMESTAMP=$(date -Iseconds)

# Read buffer content
ACTIONS=$(cat "$BUFFER_FILE")

# Create episode file
EPISODE_FILE="$SOPHIA_DIR/episodes/${EPISODE_ID}.json"
mkdir -p "$SOPHIA_DIR/episodes"

cat > "$EPISODE_FILE" <<EOF
{
  "id": "$EPISODE_ID",
  "session_id": "$SESSION_ID",
  "started_at": "$(head -1 "$BUFFER_FILE" | jq -r '.ts // empty' 2>/dev/null || echo "$TIMESTAMP")",
  "ended_at": "$TIMESTAMP",
  "end_trigger": "stop_hook",
  "tool_call_count": $TOOL_COUNT,
  "trivial": false,
  "consolidated": false,
  "actions": [
$(echo "$ACTIONS" | sed 's/^/    /' | paste -sd ',' -)
  ],
  "outcome": "UNKNOWN",
  "heuristics": [],
  "keywords": []
}
EOF

# Update index.json with file locking
INDEX_FILE="$SOPHIA_DIR/episodes/index.json"
LOCK_FILE="${INDEX_FILE}.lock"

# Acquire lock (timeout 5s)
LOCK_ACQUIRED=0
for i in {1..50}; do
    if mkdir "$LOCK_FILE" 2>/dev/null; then
        LOCK_ACQUIRED=1
        break
    fi
    sleep 0.1
done

if [[ "$LOCK_ACQUIRED" -eq 1 ]]; then
    # Initialize index if needed
    if [[ ! -f "$INDEX_FILE" ]]; then
        echo '{"last_updated":"","total_episodes":0,"entries":[]}' > "$INDEX_FILE"
    fi

    # Add entry to index (using jq if available, else simple append)
    if command -v jq &>/dev/null; then
        NEW_ENTRY="{\"id\":\"$EPISODE_ID\",\"timestamp\":\"$TIMESTAMP\",\"tool_call_count\":$TOOL_COUNT,\"trivial\":false,\"consolidated\":false}"
        jq --argjson entry "$NEW_ENTRY" \
           '.entries = [$entry] + .entries | .total_episodes += 1 | .last_updated = now | todate' \
           "$INDEX_FILE" > "${INDEX_FILE}.tmp" && mv "${INDEX_FILE}.tmp" "$INDEX_FILE"
    fi

    # Release lock
    rmdir "$LOCK_FILE"
fi

# Update self_model stats
SELF_MODEL="$SOPHIA_DIR/self_model.json"
if [[ -f "$SELF_MODEL" ]] && command -v jq &>/dev/null; then
    jq '.total_sessions += 1 | .total_episodes += 1 | .last_session = now | todate' \
       "$SELF_MODEL" > "${SELF_MODEL}.tmp" && mv "${SELF_MODEL}.tmp" "$SELF_MODEL"
fi

# Clean up buffer
rm -f "$BUFFER_FILE"

# Optionally trigger reflection (check config)
CONFIG_FILE="$SOPHIA_DIR/config.json"
if [[ -f "$CONFIG_FILE" ]]; then
    TRIGGER=$(jq -r '.reflection_trigger // "manual"' "$CONFIG_FILE")
    if [[ "$TRIGGER" == "on_session_end" ]]; then
        # Spawn reflection in background (would need Claude Code agent invocation)
        echo "Reflection triggered for session $SESSION_ID" >> "$SOPHIA_DIR/logs/reflection_queue.txt"
    fi
fi

exit 0
