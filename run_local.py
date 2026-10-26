"""Start the local workspace using installed runtimes (Python standard library only)."""
import argparse
import json
import os
from pathlib import Path
import shutil
import socket
import subprocess
import sys
import tempfile
import threading
import time
import urllib.request
import webbrowser


ROOT = Path(__file__).resolve().parent
FRONTEND_URL = "http://127.0.0.1:5173"
# Local requests must not be sent through a machine's HTTP proxy.
HTTP = urllib.request.build_opener(urllib.request.ProxyHandler({}))


def hidden_process_flags():
    return subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0


def find_node():
    override_name = "GIBLE_NODE" if "GIBLE_NODE" in os.environ else "PARTNER_NODE"
    override = os.environ.get(override_name)
    candidates = [override] if override else [shutil.which("node")]
    if not override and os.name == "nt":
        for variable in ("ProgramFiles", "ProgramFiles(x86)", "LOCALAPPDATA"):
            base = os.environ.get(variable)
            if base:
                candidates.append(str(Path(base) / "nodejs" / "node.exe"))
    for candidate in candidates:
        if not candidate:
            continue
        try:
            result = subprocess.run(
                [candidate, "--version"], capture_output=True, text=True,
                timeout=10, creationflags=hidden_process_flags(),
            )
            version = result.stdout.strip()
            if result.returncode == 0 and int(version.lstrip("v").split(".")[0]) >= 18:
                return candidate, version
        except (OSError, ValueError, subprocess.TimeoutExpired):
            continue
    source = "{} is invalid. ".format(override_name) if override else "Node.js 18 or newer was not found. "
    raise RuntimeError(source + "Install Node.js from https://nodejs.org/ and restart your terminal, "
                       "or set GIBLE_NODE to the full executable path.")


def is_gible(port):
    path = "/api/profiles" if port == 8765 else "/"
    try:
        with HTTP.open("http://127.0.0.1:{}{}".format(port, path), timeout=1) as response:
            body = response.read(1024 * 1024).decode("utf-8")
            if port == 8765:
                return (response.headers.get("Server", "").startswith(("GibleLocalHTTP/", "PartnerLocalHTTP/"))
                        and isinstance(json.loads(body).get("profiles"), list))
            return ('<title>Gible</title>' in body or '<title>Partner</title>' in body) and '/src/main.js' in body
    except (OSError, ValueError, AttributeError):
        return False


# Keep the old helper name for scripts that imported the local launcher.
is_partner = is_gible


def port_in_use(port):
    try:
        with socket.create_connection(("127.0.0.1", port), timeout=0.5):
            return True
    except OSError:
        return False


def stop_owned(processes):
    for process, log in reversed(processes):
        if process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
        log.close()


def start_server(name, port, command, processes):
    if is_gible(port):
        print("{} is already running at http://127.0.0.1:{} (reused).".format(name, port), flush=True)
        return
    if port_in_use(port):
        raise RuntimeError("Port {} is occupied by another application. Close that application and retry.".format(port))
    log = tempfile.TemporaryFile()
    try:
        environment = os.environ.copy()
        # The browser API and launcher use fixed ports; ignore inherited frontend overrides.
        environment.pop("PARTNER_FRONTEND_PORT", None)
        environment.pop("GIBLE_FRONTEND_PORT", None)
        process = subprocess.Popen(
            command, cwd=str(ROOT), env=environment, stdin=subprocess.DEVNULL,
            stdout=log, stderr=subprocess.STDOUT, creationflags=hidden_process_flags(),
        )
    except OSError:
        log.close()
        raise
    processes.append((process, log))
    deadline = time.monotonic() + 15
    while time.monotonic() < deadline:
        if process.poll() is not None:
            break
        if is_gible(port):
            print("{} ready at http://127.0.0.1:{}".format(name, port), flush=True)
            return
        time.sleep(0.2)
    log.seek(0)
    detail = log.read().decode("utf-8", errors="replace").strip()
    raise RuntimeError("{} failed to start. {}".format(name, detail or "Timed out waiting for the server."))


def wait_for_exit(processes):
    finished = threading.Event()

    def read_enter():
        try:
            input()
        except EOFError:
            pass
        finished.set()

    threading.Thread(target=read_enter, daemon=True).start()
    while not finished.wait(0.3):
        for process, log in processes:
            if process.poll() is not None:
                log.seek(0)
                raise RuntimeError("A server stopped unexpectedly: " + log.read().decode("utf-8", errors="replace"))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="check runtimes and files without starting servers")
    parser.add_argument("--no-browser", action="store_true", help="do not open a browser automatically")
    args = parser.parse_args()
    processes = []
    try:
        if sys.version_info < (3, 10):
            raise RuntimeError("Python 3.10 or newer is required. See https://www.python.org/downloads/")
        for relative in ("backend/server.py", "frontend/server.mjs", "frontend/index.html"):
            if not (ROOT / relative).is_file():
                raise RuntimeError("Missing {}. Keep the launcher inside the complete Gible repository.".format(relative))
        node, version = find_node()
        print("Python {}: {}".format(sys.version.split()[0], sys.executable), flush=True)
        print("Node.js {}: {}".format(version, node), flush=True)
        if args.check:
            print("Environment check passed. Browser access to https://esm.sh is required.")
            return 0
        start_server("Backend", 8765, [sys.executable, str(ROOT / "backend/server.py")], processes)
        start_server("Frontend", 5173, [node, str(ROOT / "frontend/server.mjs")], processes)
        print("Open " + FRONTEND_URL, flush=True)
        print("Keep this window open. Press Enter or Ctrl+C to stop services started here.", flush=True)
        if not args.no_browser:
            try:
                webbrowser.open(FRONTEND_URL)
            except webbrowser.Error:
                print("Could not open a browser automatically. Open the URL above manually.")
        wait_for_exit(processes)
        return 0
    except KeyboardInterrupt:
        return 0
    except (OSError, RuntimeError) as error:
        print("ERROR: {}".format(error), file=sys.stderr, flush=True)
        return 1
    finally:
        stop_owned(processes)


if __name__ == "__main__":
    sys.exit(main())
