"""One-shot Brand Brain setup: venv, install, smoke test, MCP config."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MIN_PYTHON = (3, 10)


def _venv_python() -> Path:
    if sys.platform == "win32":
        return ROOT / ".venv" / "Scripts" / "python.exe"
    return ROOT / ".venv" / "bin" / "python"


def _run(cmd: list[str]) -> None:
    print(f"  $ {' '.join(cmd)}")
    subprocess.check_call(cmd, cwd=ROOT)


def _ensure_executable(path: Path) -> None:
    """Make a script executable on Unix (no-op on Windows)."""
    if sys.platform != "win32" and path.is_file():
        path.chmod(path.stat().st_mode | 0o111)


def _mcp_server_entry(*, use_workspace_folder: bool) -> dict:
    if use_workspace_folder:
        if sys.platform == "win32":
            command = "${workspaceFolder}/.venv/Scripts/python.exe"
        else:
            command = "${workspaceFolder}/.venv/bin/python"
        return {
            "command": command,
            "args": ["-m", "brand_brain.server"],
            "cwd": "${workspaceFolder}",
        }
    py = _venv_python()
    return {
        "command": str(py),
        "args": ["-m", "brand_brain.server"],
        "cwd": str(ROOT),
    }


def _write_mcp_configs() -> None:
    cursor_path = ROOT / ".cursor" / "mcp.json"
    cursor_path.parent.mkdir(exist_ok=True)
    cursor_path.write_text(
        json.dumps(
            {"mcpServers": {"brand-brain": _mcp_server_entry(use_workspace_folder=True)}},
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    generic_path = ROOT / "mcp-config" / "claude_desktop.json"
    generic_path.parent.mkdir(exist_ok=True)
    generic_path.write_text(
        json.dumps(
            {"mcpServers": {"brand-brain": _mcp_server_entry(use_workspace_folder=False)}},
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def main() -> None:
    if sys.version_info < MIN_PYTHON:
        sys.exit(
            f"Python {MIN_PYTHON[0]}.{MIN_PYTHON[1]}+ is required "
            f"(found {sys.version.split()[0]}). Install from https://python.org"
        )

    print("Setting up Brand Brain...\n")

    if not _venv_python().is_file():
        print("1/4  Creating virtual environment")
        _run([sys.executable, "-m", "venv", str(ROOT / ".venv")])
    else:
        print("1/4  Virtual environment already exists")

    py = str(_venv_python())

    print("2/4  Installing dependencies")
    _run([py, "-m", "pip", "install", "-e", ".[dev]"])

    print("3/4  Running smoke tests")
    _run([py, "tests/test_validator.py"])

    print("4/4  Writing MCP config files")
    _write_mcp_configs()

    _ensure_executable(ROOT / "scripts" / "launch_mcp.py")
    _ensure_executable(ROOT / "setup.command")

    print(
        """
Done - Brand Brain is ready.

Config files:
  Cursor:         .cursor/mcp.json
  Claude Desktop: mcp-config/claude_desktop.json  (copy into your Claude config)
  Other clients:  same command/args/cwd as claude_desktop.json

See README.md for connection steps.
"""
    )


if __name__ == "__main__":
    main()
