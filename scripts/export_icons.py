from __future__ import annotations

from pathlib import Path

from components.icons import ICONS

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "assets" / "icons"


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    for name, svg in ICONS.items():
        target = OUTPUT_DIR / f"{name}.svg"
        target.write_text(svg.strip() + "\n", encoding="utf-8")
        print(f"Écrit : {target}")


if __name__ == "__main__":
    main()