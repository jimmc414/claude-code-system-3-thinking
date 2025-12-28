#!/bin/bash
# ~/.sophia/hooks/guardian_tier1.sh
# Guardian Tier 1: Regex blocklist for dangerous patterns
# Exit 0 = allow, Exit 1 = block

set -e

# Read tool input from stdin
INPUT=$(cat)

# Extract tool name and arguments
TOOL_NAME="${CLAUDE_TOOL_NAME:-unknown}"
TOOL_ARGS="$INPUT"

# Log file for blocked attempts
LOG_FILE="$HOME/.sophia/logs/guardian_blocks.jsonl"

# Dangerous patterns (case-insensitive)
BLOCKLIST=(
    'rm\s+-rf\s+/'
    'rm\s+-rf\s+\*'
    'rm\s+-rf\s+~'
    'DROP\s+TABLE'
    'DROP\s+DATABASE'
    'DELETE\s+FROM\s+\w+\s*;'
    'TRUNCATE\s+TABLE'
    ';\s*--'
    'eval\s*\('
    'exec\s*\('
    '\$\(.*\)'
    '`.*`'
    'chmod\s+777'
    'chmod\s+-R\s+777'
    '>\s*/dev/sd'
    'mkfs\.'
    'dd\s+if=.*of=/dev'
    ':(){:|:&};:'
)

# Check each pattern
for pattern in "${BLOCKLIST[@]}"; do
    if echo "$TOOL_ARGS" | grep -qiE "$pattern"; then
        # Ensure log directory exists
        mkdir -p "$(dirname "$LOG_FILE")"

        # Log the blocked attempt
        TIMESTAMP=$(date -Iseconds)
        echo "{\"timestamp\":\"$TIMESTAMP\",\"tool\":\"$TOOL_NAME\",\"pattern\":\"$pattern\",\"blocked\":true}" >> "$LOG_FILE"

        # Output reason and exit with error
        echo "BLOCKED: Pattern '$pattern' matches dangerous operation"
        exit 1
    fi
done

# All checks passed
exit 0
