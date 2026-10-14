#!/bin/bash
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
REPO="$(dirname "$HERE")"
APP="$HOME/Applications/Apple EventKit Host.app"
LABEL="com.lwekuiper.apple-eventkit-host"

mkdir -p "$APP/Contents/MacOS"
cp "$HERE/Info.plist" "$APP/Contents/Info.plist"
swiftc -O "$HERE/main.swift" -o "$APP/Contents/MacOS/AppleEventKitHost"
codesign --force --sign - "$APP"
codesign --verify "$APP"

cat <<EOF
Built and signed: $APP

A rebuild changes the signature, so macOS asks for Reminders and Calendar access again.

First install, run these yourself:
  cp "$HERE/$LABEL.plist" ~/Library/LaunchAgents/
  launchctl bootstrap gui/\$(id -u) ~/Library/LaunchAgents/$LABEL.plist

Grant access (after first install and after every rebuild):
  open -g "$APP" --args /opt/homebrew/bin/uv --directory "$REPO" run python "$REPO/scripts/setup_permissions.py"

Check it answers:
  /opt/homebrew/bin/uv --directory "$REPO" run python "$HERE/smoke.py"
EOF
