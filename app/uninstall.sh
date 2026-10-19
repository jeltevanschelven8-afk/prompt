#!/usr/bin/env bash
# Removes Prompt (the program) on macOS or Linux. Your skills in ~/.claude are NOT touched.
set -euo pipefail
if [ "$(uname -s)" = "Darwin" ]; then
  DEST="$HOME/Library/Application Support/Prompt"
  pkill -f "$DEST/prompt.pyw" 2>/dev/null || true
  rm -rf "$HOME/Applications/Prompt.app" "$DEST"
  rm -f "$HOME/Library/LaunchAgents/nl.prompt.app.plist"
else
  DEST="${XDG_DATA_HOME:-$HOME/.local/share}/prompt"
  pkill -f "$DEST/prompt.pyw" 2>/dev/null || true
  rm -rf "$DEST"
  rm -f "$HOME/.local/bin/prompt-app" "${XDG_DATA_HOME:-$HOME/.local/share}/applications/prompt.desktop" \
        "${XDG_CONFIG_HOME:-$HOME/.config}/autostart/prompt.desktop"
fi
echo "Prompt removed. Your skills in ~/.claude/skills and ~/.claude/skills-uit are still there."
