#!/usr/bin/env bash
# Packs the downloads into files/:  Prompt-<version>-windows.zip, -macos.zip and -linux.tar.gz
#   bash scripts/pack.sh 2.0.1
# Used by the release workflow and the install test. Run `npm run build` first for a fresh catalogue.
set -euo pipefail
V="${1:-dev}"
cd "$(dirname "$0")/.."
rm -rf out files
APP_FILES="prompt.pyw builtin_commands.json uitleg.json synonyms.json registry.json catalog-index.json icon.ico icon.png README.md"

pack() {  # $1 = folder to fill
  mkdir -p "out/$1/app"
  for f in $APP_FILES; do cp "app/$f" "out/$1/app/"; done
  cp -r skills "out/$1/skills"
  cp README.md INSTALL.md LICENSE "out/$1/"
}

# Windows: double-click "Install Prompt.cmd". It pauses at the end so you can read the result.
pack windows/Prompt
cp -r app/host app/install.ps1 app/install.cmd app/make_shortcuts.ps1 out/windows/Prompt/app/
printf '@echo off\r\ncall "%%~dp0app\\install.cmd"\r\necho.\r\npause\r\n' > "out/windows/Prompt/Install Prompt.cmd"

# macOS: right-click "Install Prompt.command" > Open.
pack macos/Prompt
cp app/install.sh app/uninstall.sh out/macos/Prompt/app/
cat > "out/macos/Prompt/Install Prompt.command" <<'EOF'
#!/bin/bash
cd "$(dirname "$0")" && bash app/install.sh
status=$?
echo
read -n 1 -s -r -p "Press any key to close this window." || true
exit $status
EOF
chmod +x out/macos/Prompt/app/*.sh "out/macos/Prompt/Install Prompt.command"

# Linux: ./install.sh
pack linux/prompt
cp app/install.sh app/uninstall.sh out/linux/prompt/app/
printf '#!/bin/bash\ncd "$(dirname "$0")" && exec bash app/install.sh\n' > out/linux/prompt/install.sh
chmod +x out/linux/prompt/app/*.sh out/linux/prompt/install.sh

mkdir -p files
(cd out/windows && zip -qrX "../../files/Prompt-$V-windows.zip" Prompt)
(cd out/macos && zip -qrX "../../files/Prompt-$V-macos.zip" Prompt)
(cd out/linux && tar czf "../../files/Prompt-$V-linux.tar.gz" prompt)
rm -rf out
ls -la files
