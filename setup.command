#!/bin/bash
cd "$(dirname "$0")"
if command -v python3 &>/dev/null; then
  python3 scripts/setup.py
elif command -v python &>/dev/null; then
  python scripts/setup.py
else
  echo "Python 3.10+ is required. Install from https://python.org"
  exit 1
fi
echo
read -p "Press Enter to close..."
