from __future__ import annotations

import argparse
import re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSION_FILE = ROOT / "VERSION"
CHANGELOG_FILE = ROOT / "CHANGELOG.md"


def parse_version(value: str) -> tuple[int, int, int]:
    parts = value.strip().split(".")

    while len(parts) < 3:
        parts.append("0")

    try:
        major = int(parts[0])
        minor = int(parts[1])
        patch = int(parts[2])
    except ValueError as exc:
        raise ValueError(f"Invalid VERSION file content: {value}") from exc

    return major, minor, patch


def determine_bump(message: str) -> str:
    normalized = message.strip().lower()
    first_line = normalized.splitlines()[0] if normalized else ""

    if "breaking change" in normalized:
        return "major"

    if re.match(r"^[a-z]+(\([^)]+\))?!:", first_line):
        return "major"

    if first_line.startswith("feat"):
        return "minor"

    return "patch"


def update_changelog(version: str, message: str) -> None:
    today = date.today().isoformat()
    first_line = message.strip().splitlines()[0] if message.strip() else "Automatic release"

    entry = f"## v{version} - {today}\n\n- {first_line}\n\n"

    if CHANGELOG_FILE.exists():
        old_content = CHANGELOG_FILE.read_text(encoding="utf-8")

        if old_content.startswith("# Changelog"):
            parts = old_content.split("\n", 1)
            body = parts[1].lstrip("\n") if len(parts) > 1 else ""
            new_content = f"# Changelog\n\n{entry}{body}"
        else:
            new_content = f"# Changelog\n\n{entry}{old_content.lstrip()}"
    else:
        new_content = f"# Changelog\n\n{entry}"

    CHANGELOG_FILE.write_text(new_content, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Increment application version.")
    parser.add_argument("--message", required=True, help="Commit message used to determine bump type.")
    args = parser.parse_args()

    if VERSION_FILE.exists():
        current = VERSION_FILE.read_text(encoding="utf-8").strip()
    else:
        current = "0.1.0"

    major, minor, patch = parse_version(current)
    bump = determine_bump(args.message)

    if bump == "major":
        major += 1
        minor = 0
        patch = 0
    elif bump == "minor":
        minor += 1
        patch = 0
    else:
        patch += 1

    new_version = f"{major}.{minor}.{patch}"

    VERSION_FILE.write_text(new_version + "\n", encoding="utf-8")
    update_changelog(new_version, args.message)

    print(new_version)


if __name__ == "__main__":
    main()