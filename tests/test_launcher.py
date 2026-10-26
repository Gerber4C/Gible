"""Portable launcher checks; run with python -m unittest discover -s tests -v."""
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

import importlib.util


ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("gible_launcher", ROOT / "run_local.py")
launcher = importlib.util.module_from_spec(spec)
spec.loader.exec_module(launcher)


class LauncherTests(unittest.TestCase):
    def run_launcher(self, *args, env=None, root=ROOT):
        return subprocess.run(
            [sys.executable, str(root / "run_local.py"), *args],
            cwd=tempfile.gettempdir(), env=env, capture_output=True,
            text=True, timeout=20,
        )

    @unittest.skipUnless(os.name == "nt", "Windows batch entry point")
    def test_cmd_discovers_installed_runtime(self):
        result = subprocess.run(
            ["cmd.exe", "/d", "/c", str(ROOT / "run_local.cmd"), "--check"],
            cwd=tempfile.gettempdir(), capture_output=True, text=True, timeout=20,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("Environment check passed", result.stdout)

    def test_check_from_another_working_directory(self):
        result = self.run_launcher("--check")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("Environment check passed", result.stdout)

    def test_gible_entrypoints_check_from_another_directory(self):
        result = subprocess.run(
            [sys.executable, str(ROOT / "gible.py"), "--check"],
            cwd=tempfile.gettempdir(), capture_output=True, text=True, timeout=20,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        if os.name == "nt":
            result = subprocess.run(
                ["cmd.exe", "/d", "/c", str(ROOT / "gible.cmd"), "--check"],
                cwd=tempfile.gettempdir(), capture_output=True, text=True, timeout=20,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_gible_node_override_takes_precedence(self):
        env = {**os.environ, "GIBLE_NODE": str(ROOT / "missing node.exe"),
               "PARTNER_NODE": shutil.which("node") or "node"}
        result = self.run_launcher("--check", env=env)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("GIBLE_NODE", result.stdout + result.stderr)

    @unittest.skipUnless(os.name == "nt", "Windows batch entry point")
    def test_gible_python_override_takes_precedence(self):
        env = {**os.environ, "GIBLE_PYTHON": str(ROOT / "missing python.exe"),
               "PARTNER_PYTHON": sys.executable}
        result = subprocess.run(
            ["cmd.exe", "/d", "/c", str(ROOT / "gible.cmd"), "--check"],
            cwd=ROOT, env=env, capture_output=True, text=True, timeout=20,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("GIBLE_PYTHON", result.stdout + result.stderr)

    def test_gible_launcher_recognizes_previous_server_signatures(self):
        class Response:
            def __init__(self, body, server="PartnerLocalHTTP/0.1"):
                self.body = body
                self.headers = {"Server": server}

            def __enter__(self):
                return self

            def __exit__(self, *_):
                return None

            def read(self, *_):
                return self.body

        with patch.object(launcher.HTTP, "open", side_effect=[
            Response(b'{"profiles": []}'),
            Response(b'<title>Partner</title><script src="/src/main.js"></script>'),
            Response(b'{"profiles": []}', "GibleLocalHTTP/0.1"),
            Response(b'<title>Gible</title><script src="/src/main.js"></script>'),
        ]):
            self.assertTrue(launcher.is_gible(8765))
            self.assertTrue(launcher.is_gible(5173))
            self.assertTrue(launcher.is_gible(8765))
            self.assertTrue(launcher.is_gible(5173))

    def test_invalid_node_override_reports_actionable_error(self):
        env = {**os.environ, "PARTNER_NODE": str(ROOT / "missing node.exe")}
        result = self.run_launcher("--check", env=env)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("PARTNER_NODE", result.stdout + result.stderr)

    def test_repository_path_with_spaces(self):
        with tempfile.TemporaryDirectory(prefix="Gible launcher ") as directory:
            root = Path(directory)
            for relative in ("run_local.py", "run_local.cmd", "gible.py", "gible.cmd", "backend/server.py", "frontend/server.mjs", "frontend/index.html"):
                target = root / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(ROOT / relative, target)
            result = self.run_launcher("--check", root=root)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            result = subprocess.run(
                [sys.executable, str(root / "gible.py"), "--check"],
                cwd=tempfile.gettempdir(), capture_output=True, text=True, timeout=20,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            if os.name == "nt":
                result = subprocess.run(
                    ["cmd.exe", "/d", "/c", "gible.cmd", "--check"],
                    cwd=root, capture_output=True, text=True, timeout=20,
                )
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    @unittest.skipUnless(os.name == "nt", "Windows batch entry point")
    def test_invalid_python_override_does_not_silently_fallback(self):
        result = subprocess.run(
            ["cmd.exe", "/d", "/c", "run_local.cmd", "--check"],
            cwd=ROOT, env={**os.environ, "PARTNER_PYTHON": str(ROOT / "missing python.exe")},
            capture_output=True, text=True, timeout=20,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("PARTNER_PYTHON", result.stdout)

    def test_start_reuse_and_stop_only_owned_servers(self):
        if any(launcher.port_in_use(port) for port in (8765, 5173)):
            self.skipTest("Gible ports already in use")
        command = (["cmd.exe", "/d", "/c", "run_local.cmd", "--no-browser"]
                   if os.name == "nt" else [sys.executable, str(ROOT / "run_local.py"), "--no-browser"])
        process = subprocess.Popen(
            command,
            cwd=ROOT, stdin=subprocess.PIPE,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
        )
        try:
            deadline = time.monotonic() + 20
            while time.monotonic() < deadline and process.poll() is None:
                if launcher.is_partner(8765) and launcher.is_partner(5173):
                    break
                time.sleep(0.2)
            self.assertTrue(launcher.is_partner(8765), "Backend did not become ready")
            self.assertTrue(launcher.is_partner(5173), "Frontend did not become ready")
            reused = subprocess.run(
                [sys.executable, str(ROOT / "run_local.py"), "--no-browser"],
                input="\n", capture_output=True, text=True, timeout=20,
            )
            self.assertEqual(reused.returncode, 0, reused.stdout + reused.stderr)
            self.assertEqual(reused.stdout.count("(reused)"), 2)
            self.assertTrue(launcher.is_partner(8765))
            self.assertTrue(launcher.is_partner(5173))
        finally:
            output, _ = process.communicate(input="\n", timeout=20)
        self.assertEqual(process.returncode, 0, output)
        self.assertFalse(launcher.port_in_use(8765))
        self.assertFalse(launcher.port_in_use(5173))

    def test_frontend_port_conflict_cleans_up_started_backend(self):
        import socket
        if any(launcher.port_in_use(port) for port in (8765, 5173)):
            self.skipTest("Gible ports already in use")
        with socket.socket() as occupied:
            occupied.bind(("127.0.0.1", 5173))
            occupied.listen()
            result = self.run_launcher("--no-browser")
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Port 5173 is occupied", result.stderr)
            self.assertFalse(launcher.port_in_use(8765))


if __name__ == "__main__":
    unittest.main()
