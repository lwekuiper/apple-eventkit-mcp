"""Round-trip the MCP server through the host socket and print what comes back."""

import json
import socket
import sys

SOCKET = "/Users/laurens/Library/Caches/apple-eventkit-mcp.sock"


def main() -> int:
    conn = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    conn.settimeout(60)
    try:
        conn.connect(SOCKET)
    except OSError as exc:
        print(f"cannot connect to {SOCKET}: {exc}", file=sys.stderr)
        return 1
    stream = conn.makefile("rw")

    def send(msg: dict) -> None:
        stream.write(json.dumps(msg) + "\n")
        stream.flush()

    def receive(want_id: int) -> dict:
        while True:
            line = stream.readline()
            if not line:
                raise SystemExit("server closed the connection")
            try:
                msg = json.loads(line)
            except json.JSONDecodeError:
                raise SystemExit(f"non-JSON line on the MCP stream: {line!r}") from None
            if msg.get("id") == want_id:
                return msg

    send({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {
        "protocolVersion": "2025-06-18", "capabilities": {},
        "clientInfo": {"name": "smoke", "version": "1"}}})
    print("server:", receive(1)["result"]["serverInfo"])
    send({"jsonrpc": "2.0", "method": "notifications/initialized"})
    for call_id, tool in enumerate(("eventkit_check_permissions", "reminders_list_lists"), start=2):
        send({"jsonrpc": "2.0", "id": call_id, "method": "tools/call",
              "params": {"name": tool, "arguments": {}}})
        print(f"{tool}:", receive(call_id)["result"]["content"][0]["text"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
