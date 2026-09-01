#!/usr/bin/env python3
"""Update the supported-board tables in the repository README files."""

from __future__ import annotations

import sys
from pathlib import Path

import yaml


BEGIN_MARKER = "<!-- BEGIN SUPPORTED_BOARDS -->"
END_MARKER = "<!-- END SUPPORTED_BOARDS -->"
MAX_BOARD_DIRECTORY_DEPTH = 3
TABLE_HEADERS = {
    "cn": [
        "开发板名称",
        "芯片",
        "音频",
        "SD 卡",
        "LCD",
        "LCD 触摸",
        "摄像头",
        "按键",
        "LED 灯带",
        "旋钮",
    ],
    "en": [
        "Board",
        "Chip",
        "Audio",
        "SD Card",
        "LCD",
        "LCD Touch",
        "Camera",
        "Buttons",
        "LED Strip",
        "Knob",
    ],
}


def _format_chip(chip: str) -> str:
    normalized = chip.lower().replace("-", "")
    if normalized == "esp32":
        return "ESP32"
    if normalized.startswith("esp32") and len(normalized) > len("esp32"):
        return f"ESP32-{normalized[len('esp32'):].upper()}"
    return chip.upper()


def _discover_boards(repo_root: Path) -> list[tuple[str, str]]:
    boards = []
    for info_path in sorted(repo_root.rglob("board_info.yaml")):
        board_dir = info_path.parent.relative_to(repo_root)
        if (
            len(board_dir.parts) > MAX_BOARD_DIRECTORY_DEPTH
            or any(part.startswith(".") for part in board_dir.parts)
        ):
            continue
        with info_path.open(encoding="utf-8") as file:
            info = yaml.safe_load(file) or {}
        if not isinstance(info, dict):
            raise SystemExit(f"invalid board definition: {info_path}")
        board = str(info.get("board") or info_path.parent.name)
        chip = str(info.get("chip") or "")
        if not chip:
            raise SystemExit(f"{info_path} is missing chip")
        if board != info_path.parent.name:
            raise SystemExit(
                f"board name {board!r} must match directory {info_path.parent.name!r}"
            )
        boards.append((board, _format_chip(chip)))
    if not boards:
        raise SystemExit("no board_info.yaml found; add at least one board directory")
    return boards


def _table_cells(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def _manual_details(
    table: str, column_count: int
) -> tuple[dict[str, list[str]], list[str]]:
    details = {}
    board_order = []
    for line in table.splitlines():
        if not line.lstrip().startswith("|"):
            continue
        cells = _table_cells(line)
        if len(cells) < 2 or all(set(cell) <= {"-", ":", " "} for cell in cells):
            continue
        board = cells[0].strip("`")
        if not board or board.lower() in {"board", "开发板名称"}:
            continue
        details[board] = (cells[2:] + [""] * column_count)[:column_count]
        board_order.append(board)
    return details, board_order


def _render_table(
    boards: list[tuple[str, str]], language: str, existing_details: dict[str, list[str]]
) -> str:
    headers = TABLE_HEADERS[language]
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    blank_details = [""] * (len(headers) - 2)
    for board, chip in boards:
        details = existing_details.get(board, blank_details)
        row = "| " + " | ".join([f"`{board}`", chip, *details]) + " |"
        while " |  |" in row:
            row = row.replace(" |  |", " | |")
        lines.append(row)
    return "\n".join(lines)


def update_readme(readme_path: Path, repo_root: Path, language: str) -> None:
    content = readme_path.read_text(encoding="utf-8")
    start = content.find(BEGIN_MARKER)
    end = content.find(END_MARKER, start + len(BEGIN_MARKER))
    if start == -1 or end == -1:
        raise SystemExit(
            f"{readme_path} must contain {BEGIN_MARKER} and {END_MARKER} markers"
        )
    table_start = start + len(BEGIN_MARKER)
    _, existing_order = _manual_details(
        content[table_start:end], len(TABLE_HEADERS[language]) - 2
    )
    discovered_boards = _discover_boards(repo_root)
    existing_names = set(existing_order)
    new_boards = [
        board_entry
        for board_entry in discovered_boards
        if board_entry[0] not in existing_names
    ]
    if not new_boards:
        return
    new_rows = _render_table(new_boards, language, {}).splitlines()[2:]
    updated = content[:end] + "\n".join(new_rows) + "\n" + content[end:]
    readme_path.write_text(updated, encoding="utf-8")


def main() -> int:
    repo_root = Path(__file__).resolve().parent.parent
    update_readme(repo_root / "README.md", repo_root, "en")
    update_readme(repo_root / "README_CN.md", repo_root, "cn")
    return 0


if __name__ == "__main__":
    sys.exit(main())
