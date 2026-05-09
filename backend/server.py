from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse

from app import bid, simulate, system_notes


BACKEND_DIR = Path(__file__).resolve().parent
PROFILE_ROOT = BACKEND_DIR / "partnership_profiles"
ALLOWED_FILE_SUFFIXES = {".py", ".yaml", ".yml", ".md", ".txt", ".json"}


def run(host: str = "127.0.0.1", port: int = 8765) -> None:
    server = ThreadingHTTPServer((host, port), PartnerRequestHandler)
    print(f"Partner backend listening at http://{host}:{port}")
    server.serve_forever()


class PartnerRequestHandler(BaseHTTPRequestHandler):
    server_version = "PartnerLocalHTTP/0.1"

    def do_OPTIONS(self) -> None:
        self._send_empty(204)

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        try:
            if parsed.path == "/api/profiles":
                self._send_json({"profiles": _profile_summaries()})
                return
            if parsed.path.startswith("/api/profiles/") and parsed.path.endswith("/files"):
                profile_id = _path_part(parsed.path, 2)
                self._send_json({"files": _profile_files(profile_id)})
                return
            if parsed.path.startswith("/api/profiles/") and parsed.path.endswith("/file"):
                profile_id = _path_part(parsed.path, 2)
                query = parse_qs(parsed.query)
                relative_path = query.get("path", [""])[0]
                self._send_json(_read_profile_file(profile_id, relative_path))
                return
            if parsed.path.startswith("/api/profiles/") and parsed.path.endswith("/system-notes"):
                profile_id = _path_part(parsed.path, 2)
                self._send_json(system_notes({"profile": {"id": profile_id}}))
                return
            self._send_json({"error": "not_found", "path": parsed.path}, status=404)
        except Exception as exc:
            self._send_json({"error": exc.__class__.__name__, "message": str(exc)}, status=500)

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        try:
            payload = self._read_json_body()
            if parsed.path == "/api/bid":
                self._send_json(bid(payload))
                return
            if parsed.path == "/api/simulate":
                self._send_json(simulate(payload))
                return
            if parsed.path.startswith("/api/profiles/") and parsed.path.endswith("/file"):
                profile_id = _path_part(parsed.path, 2)
                self._send_json(_write_profile_file(profile_id, payload))
                return
            self._send_json({"error": "not_found", "path": parsed.path}, status=404)
        except Exception as exc:
            self._send_json({"error": exc.__class__.__name__, "message": str(exc)}, status=500)

    def do_DELETE(self) -> None:
        parsed = urlparse(self.path)
        try:
            if parsed.path.startswith("/api/profiles/") and parsed.path.endswith("/file"):
                profile_id = _path_part(parsed.path, 2)
                query = parse_qs(parsed.query)
                relative_path = query.get("path", [""])[0]
                self._send_json(_delete_profile_file(profile_id, relative_path))
                return
            self._send_json({"error": "not_found", "path": parsed.path}, status=404)
        except Exception as exc:
            self._send_json({"error": exc.__class__.__name__, "message": str(exc)}, status=500)

    def _read_json_body(self) -> dict:
        length = int(self.headers.get("Content-Length", "0"))
        if length == 0:
            return {}
        raw = self.rfile.read(length).decode("utf-8")
        return json.loads(raw)

    def _send_empty(self, status: int) -> None:
        self.send_response(status)
        self._send_headers(content_type="text/plain")
        self.end_headers()

    def _send_json(self, value: object, status: int = 200) -> None:
        body = json.dumps(value, indent=2).encode("utf-8")
        self.send_response(status)
        self._send_headers(content_type="application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_headers(self, *, content_type: str) -> None:
        self.send_header("Content-Type", f"{content_type}; charset=utf-8")
        origin = self.headers.get("Origin")
        if origin and (origin.startswith("http://localhost:") or origin.startswith("http://127.0.0.1:")):
            self.send_header("Access-Control-Allow-Origin", origin)
        else:
            self.send_header("Access-Control-Allow-Origin", "http://127.0.0.1:5173")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def log_message(self, format: str, *args) -> None:
        return


def _profile_summaries() -> list[dict]:
    if not PROFILE_ROOT.exists():
        return []
    profiles = []
    for path in sorted(item for item in PROFILE_ROOT.iterdir() if item.is_dir()):
        profiles.append(
            {
                "id": path.name,
                "name": _display_name(path.name),
                "path": str(path.relative_to(BACKEND_DIR)),
            }
        )
    return profiles


def _profile_files(profile_id: str) -> list[dict]:
    profile_path = _profile_path(profile_id)
    files = []
    for path in sorted(item for item in profile_path.rglob("*") if item.is_file()):
        if path.suffix.lower() not in ALLOWED_FILE_SUFFIXES:
            continue
        relative = path.relative_to(profile_path).as_posix()
        files.append(
            {
                "path": relative,
                "name": path.name,
                "kind": _file_kind(relative),
                "size": path.stat().st_size,
            }
        )
    return files


def _read_profile_file(profile_id: str, relative_path: str) -> dict:
    path = _safe_profile_file(profile_id, relative_path)
    return {
        "path": path.relative_to(_profile_path(profile_id)).as_posix(),
        "content": path.read_text(encoding="utf-8"),
    }


def _write_profile_file(profile_id: str, payload: dict) -> dict:
    relative_path = payload.get("path")
    content = payload.get("content")
    if not isinstance(relative_path, str) or not relative_path:
        raise ValueError("File write requires a relative path")
    if not isinstance(content, str):
        raise ValueError("File write requires text content")
    path = _safe_profile_file(profile_id, relative_path, must_exist=False)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return {"ok": True, "path": path.relative_to(_profile_path(profile_id)).as_posix()}


def _delete_profile_file(profile_id: str, relative_path: str) -> dict:
    if not relative_path:
        raise ValueError("Delete requires a relative path")
    if relative_path == "profile.bsl.py":
        raise ValueError("The root profile file cannot be deleted")
    path = _safe_profile_file(profile_id, relative_path)
    path.unlink()
    return {"ok": True, "path": relative_path}


def _safe_profile_file(profile_id: str, relative_path: str, must_exist: bool = True) -> Path:
    profile_path = _profile_path(profile_id)
    clean_relative = Path(unquote(relative_path))
    if clean_relative.is_absolute() or ".." in clean_relative.parts:
        raise ValueError("Profile file path must stay inside the profile directory")
    path = (profile_path / clean_relative).resolve()
    if not path.is_relative_to(profile_path):
        raise ValueError("Profile file path must stay inside the profile directory")
    if path.suffix.lower() not in ALLOWED_FILE_SUFFIXES:
        raise ValueError(f"Unsupported editable file suffix: {path.suffix}")
    if must_exist and not path.exists():
        raise FileNotFoundError(relative_path)
    return path


def _profile_path(profile_id: str) -> Path:
    if not profile_id or "/" in profile_id or "\\" in profile_id or ".." in profile_id:
        raise ValueError(f"Invalid profile id: {profile_id}")
    path = (PROFILE_ROOT / profile_id).resolve()
    root = PROFILE_ROOT.resolve()
    if not path.is_relative_to(root):
        raise ValueError(f"Invalid profile id: {profile_id}")
    if not path.exists():
        raise FileNotFoundError(profile_id)
    return path


def _path_part(path: str, index: int) -> str:
    parts = [part for part in path.split("/") if part]
    if len(parts) <= index:
        raise ValueError(f"Missing path part {index}: {path}")
    return parts[index]


def _display_name(profile_id: str) -> str:
    return profile_id.replace("_", " ").title()


def _file_kind(relative_path: str) -> str:
    if relative_path == "profile.bsl.py":
        return "profile"
    if relative_path.startswith("gadgets/"):
        return "gadget"
    if relative_path.startswith("policies/"):
        return "policy"
    if relative_path.startswith("tests/"):
        return "test"
    return "document"


if __name__ == "__main__":
    run()
