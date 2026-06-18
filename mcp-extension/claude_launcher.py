"""Claude Desktop entry point for Brand Brain."""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


def main() -> None:
    root = os.environ.get("BRAND_BRAIN_ROOT", "").strip()
    if not root:
        sys.exit(
            "BRAND_BRAIN_ROOT is not set. Reinstall the extension and choose the project folder."
        )

    root_path = Path(root).resolve()
    if sys.platform == "win32":
        py = root_path / ".venv" / "Scripts" / "python.exe"
    else:
        py = root_path / ".venv" / "bin" / "python"

    if not py.is_file():
        sys.exit(
            f"Brand Brain is not set up in {root_path}.\n"
            "Run setup first: python scripts/setup.py"
        )

    args = [str(py), "-m", "brand_brain.server"]
    if sys.platform == "win32":
        raise SystemExit(subprocess.call(args, cwd=str(root_path)))
    os.execv(str(py), args)


if __name__ == "__main__":
    main()
