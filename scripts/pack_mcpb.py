"""Pack the Claude Desktop extension (.mcpb) from mcp-extension/."""
from __future__ import annotations

import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EXTENSION_DIR = ROOT / "mcp-extension"
OUTPUT = ROOT / "mcp-config" / "brand-brain.mcpb"


def pack() -> Path:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(OUTPUT, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(EXTENSION_DIR.rglob("*")):
            if path.is_file():
                archive.write(path, path.relative_to(EXTENSION_DIR).as_posix())
    return OUTPUT


if __name__ == "__main__":
    out = pack()
    print(f"Wrote {out}")
