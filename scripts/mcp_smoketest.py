import json
import os
import subprocess
import sys
import time


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
WRAPPER = os.path.join(ROOT, "cai_mcp_wrapper.py")


def _write_line(proc: subprocess.Popen[str], msg: dict) -> None:
    proc.stdin.write(json.dumps(msg) + "\n")
    proc.stdin.flush()


def main() -> int:
    if not os.path.exists(WRAPPER):
        print(f"Missing wrapper: {WRAPPER}", file=sys.stderr)
        return 2

    proc = subprocess.Popen(
        [sys.executable, "-u", WRAPPER],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd=ROOT,
        bufsize=1,
    )
    assert proc.stdin is not None
    assert proc.stdout is not None

    try:
        _write_line(
            proc,
            {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {"name": "mcp_smoketest", "version": "0.1"},
                },
            },
        )
        _write_line(proc, {"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}})
        _write_line(proc, {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}})
        _write_line(
            proc,
            {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {"name": "ping", "arguments": {}},
            },
        )

        deadline = time.time() + 30
        responses: dict[int, dict] = {}

        while time.time() < deadline and len(responses) < 3:
            line = proc.stdout.readline()
            if not line:
                break
            line = line.strip()
            if not line:
                continue
            try:
                msg = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(msg, dict) and "id" in msg and isinstance(msg["id"], int):
                responses[msg["id"]] = msg

        if 1 not in responses:
            err = proc.stderr.read()
            print("Did not receive initialize response.", file=sys.stderr)
            if err:
                print(err, file=sys.stderr)
            return 1

        if 2 not in responses:
            print("Did not receive tools/list response.", file=sys.stderr)
            return 1

        tools = [t.get("name") for t in (responses[2].get("result", {}).get("tools") or []) if isinstance(t, dict)]
        missing = [t for t in ("ping", "echo", "cai_text") if t not in tools]
        if missing:
            print(f"Missing expected tools: {missing}. Got: {tools}", file=sys.stderr)
            return 1

        if 3 not in responses:
            print("Did not receive ping tool response.", file=sys.stderr)
            return 1

        ping_text = (
            (responses[3].get("result") or {}).get("content") or [{}]
        )[0].get("text")
        if ping_text != "pong":
            print(f"Unexpected ping response: {responses[3]}", file=sys.stderr)
            return 1

        print("OK: MCP server responded; tools list contains ping/echo/cai_text; ping returned pong.")
        return 0
    finally:
        try:
            proc.stdin.close()
        except Exception:
            pass
        try:
            proc.terminate()
        except Exception:
            pass


if __name__ == "__main__":
    raise SystemExit(main())

