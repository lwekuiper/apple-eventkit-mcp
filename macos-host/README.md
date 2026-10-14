# Apple EventKit Host

Claude desktop app sessions spawn MCP servers under the Claude Code helper app, which declares no Reminders or Calendar usage strings, so macOS can never grant it EventKit access. This folder builds a tiny app bundle that does declare them. launchd starts it per connection on a Unix socket, and it runs the unchanged Python server as a child, which inherits the bundle's grants.

## Install

1. Build and sign the bundle into `~/Applications`:

   ```bash
   /Users/laurens/.scripts/apple-eventkit-mcp/macos-host/build.sh
   ```

2. Install and load the LaunchAgent (the build prints these too):

   ```bash
   cp /Users/laurens/.scripts/apple-eventkit-mcp/macos-host/com.lwekuiper.apple-eventkit-host.plist ~/Library/LaunchAgents/
   launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.lwekuiper.apple-eventkit-host.plist
   ```

3. Grant access. Click Allow on both prompts:

   ```bash
   open -g "$HOME/Applications/Apple EventKit Host.app" --args /opt/homebrew/bin/uv --directory /Users/laurens/.scripts/apple-eventkit-mcp run python /Users/laurens/.scripts/apple-eventkit-mcp/scripts/setup_permissions.py
   ```

4. Point Claude at the socket. The `apple-eventkit` entry in `~/.claude.json`:

   ```json
   { "type": "stdio", "command": "/usr/bin/nc", "args": ["-U", "/Users/laurens/Library/Caches/apple-eventkit-mcp.sock"], "env": {} }
   ```

## Rebuilding

The bundle is ad-hoc signed, so macOS ties the grant to this exact build. After any rebuild, repeat step 3; remove the stale Apple EventKit Host entry under System Settings > Privacy & Security > Reminders and Calendars if it lingers. Edits to the Python server need no rebuild and keep the grant. The LaunchAgent needs no reload after a rebuild: launchd starts the binary fresh per connection.

## Troubleshooting

- Check the round trip: `/opt/homebrew/bin/uv --directory /Users/laurens/.scripts/apple-eventkit-mcp run python /Users/laurens/.scripts/apple-eventkit-mcp/macos-host/smoke.py`
- `cannot connect`: the agent is not loaded; `launchctl print gui/$(id -u)/com.lwekuiper.apple-eventkit-host`
- Server errors: `~/Library/Logs/apple-eventkit-mcp.log`
- `not_determined` or `denied` in the smoke output: repeat install step 3.
