# SPDX-License-Identifier: Apache-2.0
# Copyright (C) 2025, The Spine Docs organization and its contributors.

"""Check that source files have required SPDX headers."""

import argparse
import sys
from pathlib import Path

HEADER_LINES = [
    "# SPDX-License-Identifier: Apache-2.0",
    "# Copyright (C) 2025, The Spine Docs organization and its contributors.",
]


def has_headers(content: str) -> bool:
    """Check if content has required headers in first 5 lines."""
    first_lines = "\n".join(content.split("\n")[:5])
    return all(header in first_lines for header in HEADER_LINES)


def check_file(filepath: Path) -> bool:
    """Check if file has required headers."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        return has_headers(content)
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return False


def main() -> int:
    """Check SPDX headers in files."""
    parser = argparse.ArgumentParser(description="Check SPDX headers in source files")
    parser.add_argument("files", nargs="+", type=Path, help="Files to check")
    args = parser.parse_args()

    missing_headers = []
    for filepath in args.files:
        if not check_file(filepath):
            missing_headers.append(filepath)

    if missing_headers:
        print("❌ Error: The following files are missing required SPDX headers:")
        for f in missing_headers:
            print(f"  - {f}")
        print("\nRequired headers (at top of file):")
        for header in HEADER_LINES:
            print(f"  {header}")
        return 1

    print("✅ All files have required SPDX headers")
    return 0


if __name__ == "__main__":
    sys.exit(main())
