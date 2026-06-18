"""Launch Brand Brain MCP server using the project venv when present.

MCP clients invoke this with whatever ``python`` is on PATH. Only the stdlib
is required here; the server itself runs inside ``.venv`` when it exists.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _venv_python() -> Path | None:
    if sys.platform == "win32":
        candidate = ROOT / ".venv" / "Scripts" / "python.exe"
    else:
        candidate = ROOT / ".venv" / "bin" / "python"
    return candidate if candidate.is_file() else None


def main() -> None:
    if sys.stdin.isatty():
        sys.exit(
            "This script is for MCP clients, not the terminal.\n"
            "Run setup first:\n"
            "  python scripts/setup.py\n"
            "Or double-click setup.bat (Windows) / setup.command (Mac)."
        )

    py = _venv_python()
    if py is not None:
        args = [str(py), "-m", "brand_brain.server", *sys.argv[1:]]
        if sys.platform == "win32":
            raise SystemExit(subprocess.call(args))
        import os

        os.execv(str(py), args)

    try:
        from brand_brain.server import main as run_server
    except ImportError:
        sys.exit(
            "Brand Brain is not installed. Run setup first:\n"
            "  python scripts/setup.py\n"
            "Or double-click setup.bat (Windows) / setup.command (Mac)."
        )

    run_server()


if __name__ == "__main__":
    main()
