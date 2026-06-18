#!/bin/bash
cd "$(dirname "$0")"

pick_python() {
  for cmd in python3.14 python3.13 python3.12 python3.11 python3 python; do
    if command -v "$cmd" >/dev/null 2>&1 && "$cmd" -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 10) else 1)' 2>/dev/null; then
      echo "$cmd"
      return 0
    fi
  done
  return 1
}

PY="$(pick_python)" || {
  echo "Python 3.10+ is required. Install from https://python.org"
  exit 1
}

"$PY" scripts/setup.py
echo
read -p "Press Enter to close..."
