#!/bin/bash
# uninstall.sh - Remove System 3 components

echo "Removing System 3..."

# Remove hooks from ~/.sophia/
if [[ -d ~/.sophia/hooks ]]; then
    rm -rf ~/.sophia/hooks/
    echo "Removed hooks"
fi

# Remove skills from ~/.claude/skills/
rm -f ~/.claude/skills/s3-*.md 2>/dev/null
echo "Removed skills"

# Remove from hooks.json if present
HOOKS_CONFIG="$HOME/.claude/hooks.json"
if [[ -f "$HOOKS_CONFIG" ]]; then
    echo ""
    echo "Note: You may want to manually edit $HOOKS_CONFIG"
    echo "to remove System 3 hook entries."
fi

# Ask about data removal
echo ""
read -p "Remove all System 3 data (~/.sophia/)? [y/N] " -n 1 -r
echo

if [[ $REPLY =~ ^[Yy]$ ]]; then
    rm -rf ~/.sophia/
    echo "Removed ~/.sophia/ and all data"
else
    echo "Data preserved at ~/.sophia/"
fi

echo ""
echo "Uninstallation complete."
echo ""
echo "Note: If you installed CLAUDE.md, you may want to remove or restore it manually."
