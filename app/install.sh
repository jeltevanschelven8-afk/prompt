#!/usr/bin/env bash
# Installs Prompt for the current user on macOS or Linux. No root needed.
#   macOS: app in ~/Library/Application Support/Prompt, launcher ~/Applications/Prompt.app
#   Linux: app in ~/.local/share/prompt, menu entry + `prompt-app` command in ~/.local/bin
set -euo pipefail

SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILLS_SRC="$(cd "$SRC/.." && pwd)/skills"
OS="$(uname -s)"

say() { printf '%s\n' "$*"; }
fail() { printf '\n%s\n' "$*" >&2; exit 1; }

# --- Find a Python 3.9+ with Tk 8.6+ ---------------------------------------------------------------
candidates=()
if [ "$OS" = "Darwin" ]; then
  # python.org builds first: Apple's /usr/bin/python3 ships an old Tk that draws badly.
  for v in 3.14 3.13 3.12 3.11 3.10 3.9; do
    candidates+=("/Library/Frameworks/Python.framework/Versions/$v/bin/python3")
  done
  candidates+=("/opt/homebrew/bin/python3" "/usr/local/bin/python3")
fi
candidates+=(python3.14 python3.13 python3.12 python3.11 python3.10 python3.9 python3)

PY=""
for c in "${candidates[@]}"; do
  if command -v "$c" >/dev/null 2>&1 && "$c" - <<'EOF' >/dev/null 2>&1
import sys, tkinter
assert sys.version_info >= (3, 9) and tkinter.TkVersion >= 8.6
EOF
  then PY="$(command -v "$c")"; break; fi
done

if [ -z "$PY" ]; then
  say "Prompt needs Python 3.9 or newer with Tk (tkinter). It was not found."
  say ""
  if [ "$OS" = "Darwin" ]; then
    say "  Install Python from https://www.python.org/downloads/macos/ (includes Tk), or:"
    say "    brew install python python-tk"
  else
    say "  Ubuntu, Debian, Mint:  sudo apt install python3 python3-tk"
    say "  Fedora:                sudo dnf install python3 python3-tkinter"
    say "  openSUSE:              sudo zypper install python3 python3-tk"
    say "  Arch, Manjaro:         sudo pacman -S python tk"
  fi
  fail "Then run this installer again."
fi
say "Python: $PY ($("$PY" -c 'import sys, tkinter; print("%d.%d.%d" % sys.version_info[:3], "Tk", tkinter.TkVersion)'))"

# --- Where to install ------------------------------------------------------------------------------
if [ "$OS" = "Darwin" ]; then
  DEST="$HOME/Library/Application Support/Prompt"
else
  DEST="${XDG_DATA_HOME:-$HOME/.local/share}/prompt"
fi

# Stop a running Prompt so its files can be replaced.
pkill -f "$DEST/prompt.pyw" 2>/dev/null || true

mkdir -p "$DEST"
for f in prompt.pyw builtin_commands.json uitleg.json synonyms.json icon.png README.md; do
  cp "$SRC/$f" "$DEST/"
done
# registry.json says which marketplace to use: keep the user's own copy.
if [ ! -f "$DEST/registry.json" ] || grep -q OWNER "$DEST/registry.json"; then
  cp "$SRC/registry.json" "$DEST/"
fi

# Bundled catalogue, so the marketplace also works offline.
rm -rf "$DEST/catalog"
mkdir -p "$DEST/catalog/data"
cp "$SRC/catalog-index.json" "$DEST/catalog/data/index.json"
cp -R "$SKILLS_SRC" "$DEST/catalog/skills"
say "Catalogue: $(find "$DEST/catalog/skills" -mindepth 1 -maxdepth 1 -type d | wc -l | tr -d ' ') skills"

# --- Launcher ----------------------------------------------------------------------------------------
if [ "$OS" = "Darwin" ]; then
  APP="$HOME/Applications/Prompt.app"
  rm -rf "$APP"
  mkdir -p "$APP/Contents/MacOS" "$APP/Contents/Resources"
  cat > "$APP/Contents/MacOS/Prompt" <<EOF
#!/bin/bash
exec "$PY" "$DEST/prompt.pyw" "\$@"
EOF
  chmod +x "$APP/Contents/MacOS/Prompt"
  ICON_LINE=""
  if command -v sips >/dev/null && command -v iconutil >/dev/null; then
    SET="$(mktemp -d)/Prompt.iconset"; mkdir -p "$SET"
    for s in 16 32 128 256; do
      sips -z $s $s "$DEST/icon.png" --out "$SET/icon_${s}x${s}.png" >/dev/null
      d=$((s * 2)); sips -z $d $d "$DEST/icon.png" --out "$SET/icon_${s}x${s}@2x.png" >/dev/null
    done
    iconutil -c icns "$SET" -o "$APP/Contents/Resources/Prompt.icns" && ICON_LINE="<key>CFBundleIconFile</key><string>Prompt</string>"
  fi
  cat > "$APP/Contents/Info.plist" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>CFBundleName</key><string>Prompt</string>
  <key>CFBundleDisplayName</key><string>Prompt</string>
  <key>CFBundleIdentifier</key><string>nl.prompt.app</string>
  <key>CFBundleExecutable</key><string>Prompt</string>
  <key>CFBundlePackageType</key><string>APPL</string>
  <key>CFBundleVersion</key><string>2.0</string>
  <key>NSHighResolutionCapable</key><true/>
  $ICON_LINE
</dict></plist>
EOF
  say ""
  say "Done. Open Prompt from Launchpad or ~/Applications, or run:  open \"$APP\""
else
  BIN="$HOME/.local/bin"
  APPS="${XDG_DATA_HOME:-$HOME/.local/share}/applications"
  mkdir -p "$BIN" "$APPS"
  cat > "$BIN/prompt-app" <<EOF
#!/bin/sh
exec "$PY" "$DEST/prompt.pyw" "\$@"
EOF
  chmod +x "$BIN/prompt-app"
  cat > "$APPS/prompt.desktop" <<EOF
[Desktop Entry]
Type=Application
Name=Prompt
Comment=All Claude Code commands and skills, plus a skill marketplace
Exec="$BIN/prompt-app"
Icon=$DEST/icon.png
Terminal=false
Categories=Development;Utility;
StartupWMClass=Tk
EOF
  command -v update-desktop-database >/dev/null && update-desktop-database "$APPS" >/dev/null 2>&1 || true
  say ""
  say "Done. Start Prompt from your applications menu, or run:  prompt-app"
  case ":$PATH:" in *":$BIN:"*) ;; *) say "(Add $BIN to your PATH to use the prompt-app command.)";; esac
fi
