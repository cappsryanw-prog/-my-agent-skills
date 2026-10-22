#!/usr/bin/env python3
"""
Start one or more servers, wait until each is accepting connections, run a
command, then shut every server down (including any child processes they
spawned).

Adapted from anthropics/skills (webapp-testing/scripts/with_server.py),
Apache License 2.0. Changes from the original:
  - Server output goes to log files instead of an undrained pipe, so a chatty
    dev server can no longer block once the pipe buffer fills.
  - Each server runs in its own process group, and shutdown signals the whole
    group, so children of `npm run dev` and similar wrappers don't outlive it.
  - Fails fast, with the tail of the server log, if a server exits before its
    port opens.
  - Adds --host and --log-dir options.

Usage:
    python with_server.py --server "npm run dev" --port 5173 -- python test.py

    python with_server.py \\
      --server "cd backend && python server.py" --port 3000 \\
      --server "cd frontend && npm run dev" --port 5173 \\
      -- python test.py
"""

import argparse
import os
import signal
import socket
import subprocess
import sys
import tempfile
import time

IS_WINDOWS = os.name == "nt"


def wait_for_port(host, port, process, timeout):
    """Return None when the port accepts connections, or an error string."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        if process.poll() is not None:
            return f"server process exited with code {process.returncode} before port {port} opened"
        try:
            with socket.create_connection((host, port), timeout=1):
                return None
        except OSError:
            time.sleep(0.5)
    return f"port {port} did not open within {timeout}s"


def start_server(cmd, log_path):
    log_file = open(log_path, "wb")
    kwargs = {"shell": True, "stdout": log_file, "stderr": subprocess.STDOUT, "stdin": subprocess.DEVNULL}
    if IS_WINDOWS:
        kwargs["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP
    else:
        kwargs["start_new_session"] = True  # new process group we can signal as a unit
    return subprocess.Popen(cmd, **kwargs), log_file


def stop_server(process):
    if process.poll() is not None:
        return
    try:
        if IS_WINDOWS:
            subprocess.run(["taskkill", "/F", "/T", "/PID", str(process.pid)], capture_output=True)
        else:
            os.killpg(process.pid, signal.SIGTERM)
        process.wait(timeout=5)
    except (subprocess.TimeoutExpired, ProcessLookupError, PermissionError):
        try:
            if not IS_WINDOWS:
                os.killpg(process.pid, signal.SIGKILL)
            else:
                process.kill()
            process.wait(timeout=5)
        except (ProcessLookupError, subprocess.TimeoutExpired):
            pass


def tail(path, lines=20):
    try:
        with open(path, "rb") as f:
            return b"\n".join(f.read().splitlines()[-lines:]).decode(errors="replace")
    except OSError:
        return ""


def main():
    parser = argparse.ArgumentParser(description="Run a command while one or more servers are up.")
    parser.add_argument("--server", action="append", dest="servers", required=True,
                        help="Server command (repeatable)")
    parser.add_argument("--port", action="append", dest="ports", type=int, required=True,
                        help="Port for each --server, in the same order")
    parser.add_argument("--host", default="localhost", help="Host to poll for readiness (default: localhost)")
    parser.add_argument("--timeout", type=int, default=30, help="Seconds to wait per server (default: 30)")
    parser.add_argument("--log-dir", default=None, help="Where to write server logs (default: a temp dir)")
    parser.add_argument("command", nargs=argparse.REMAINDER, help="Command to run once servers are ready")
    args = parser.parse_args()

    if args.command and args.command[0] == "--":
        args.command = args.command[1:]
    if not args.command:
        parser.error("no command given after --")
    if len(args.servers) != len(args.ports):
        parser.error("the number of --server and --port arguments must match")

    log_dir = args.log_dir or tempfile.mkdtemp(prefix="with_server_")
    os.makedirs(log_dir, exist_ok=True)

    running = []  # (process, log_file, log_path)
    exit_code = 1
    try:
        for i, (cmd, port) in enumerate(zip(args.servers, args.ports), start=1):
            log_path = os.path.join(log_dir, f"server{i}_port{port}.log")
            print(f"Starting server {i}/{len(args.servers)}: {cmd}  (log: {log_path})", flush=True)
            process, log_file = start_server(cmd, log_path)
            running.append((process, log_file, log_path))

            error = wait_for_port(args.host, port, process, args.timeout)
            if error:
                print(f"Error: {error}\n--- last lines of {log_path} ---\n{tail(log_path)}", file=sys.stderr)
                return 1
            print(f"Server ready on {args.host}:{port}", flush=True)

        print(f"\nAll {len(running)} server(s) ready. Running: {' '.join(args.command)}\n", flush=True)
        exit_code = subprocess.run(args.command).returncode
        return exit_code
    except KeyboardInterrupt:
        return 130
    finally:
        print(f"\nStopping {len(running)} server(s)...", flush=True)
        for process, log_file, _ in reversed(running):
            stop_server(process)
            log_file.close()
        print(f"All servers stopped. Logs kept in {log_dir}", flush=True)


if __name__ == "__main__":
    sys.exit(main())
