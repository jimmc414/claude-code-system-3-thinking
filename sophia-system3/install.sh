#!/bin/bash
set -e

echo "Installing System 3..."

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Create directories
mkdir -p ~/.sophia/{hooks,user_models,episodes,agent_results,logs}
mkdir -p ~/.claude/skills

# Copy hooks
if [[ -d "$SCRIPT_DIR/hooks" ]]; then
    cp "$SCRIPT_DIR/hooks/"*.sh ~/.sophia/hooks/ 2>/dev/null || true
    chmod +x ~/.sophia/hooks/*.sh 2>/dev/null || true
fi

# Copy skills
if [[ -d "$SCRIPT_DIR/skills" ]]; then
    cp "$SCRIPT_DIR/skills/"*.md ~/.claude/skills/ 2>/dev/null || true
fi

# Initialize config
if [[ ! -f ~/.sophia/config.json ]]; then
    cp "$SCRIPT_DIR/templates/config.json" ~/.sophia/config.json
fi

# Initialize self_model
if [[ ! -f ~/.sophia/self_model.json ]]; then
    cp "$SCRIPT_DIR/templates/self_model.json" ~/.sophia/self_model.json
    # Set created_at timestamp
    python3 -c "
import json
from datetime import datetime
with open('$HOME/.sophia/self_model.json', 'r+') as f:
    data = json.load(f)
    data['created_at'] = datetime.now().isoformat()
    data['updated_at'] = datetime.now().isoformat()
    f.seek(0)
    json.dump(data, f, indent=2)
    f.truncate()
" 2>/dev/null || true
fi

# Initialize empty files
if [[ ! -f ~/.sophia/episodes/index.json ]]; then
    echo '{"last_updated":"","total_episodes":0,"entries":[]}' > ~/.sophia/episodes/index.json
fi

if [[ ! -f ~/.sophia/semantic_rules.json ]]; then
    echo '[]' > ~/.sophia/semantic_rules.json
fi

# Update Claude Code hooks configuration
HOOKS_CONFIG="$HOME/.claude/hooks.json"
if [[ -f "$HOOKS_CONFIG" ]]; then
    echo "Hooks config exists at $HOOKS_CONFIG."
    echo "Please manually add System 3 hooks if not already present."
    echo "See: ~/.sophia/hooks/"
else
    cat > "$HOOKS_CONFIG" <<'EOF'
{
  "hooks": {
    "PreToolUse": [
      {"matcher": ".*", "command": "~/.sophia/hooks/guardian_tier1.sh"}
    ],
    "PostToolUse": [
      {"matcher": ".*", "command": "~/.sophia/hooks/log_action.sh"}
    ],
    "Stop": [
      {"command": "~/.sophia/hooks/session_end.sh"}
    ]
  }
}
EOF
fi

echo ""
echo "Installation complete!"
echo ""
echo "Next steps:"
echo "1. Start Claude Code"
echo "2. Run /s3-init to complete setup"
echo "3. Run /s3-status to verify installation"
