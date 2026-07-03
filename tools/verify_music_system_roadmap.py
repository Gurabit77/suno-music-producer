#!/usr/bin/env python3
"""Verify the AI music system roadmap page exists and has required content."""

from __future__ import annotations

import sys
from pathlib import Path

VAULT = Path("/path/to/obsidian-vault")
WIKI = VAULT / "wiki"

ROADMAP_PATH = WIKI / "分析" / "音乐" / "AI 音乐生产系统总路线图.md"

REQUIRED_TOOLS = [
    "create_music_song_project.py",
    "audit_music_methodology_transfer.py",
    "audit_music_prompt_specificity_budget.py",
    "audit_music_genre_lane_authenticity.py",
    "compile_music_prompt_package.py",
    "audit_music_generation_evidence.py",
    "review_music_takes.py",
    "route_music_repairs.py",
    "prepare_music_release_candidate.py",
    "prepare_music_catalog_memory.py",
]

REQUIRED_KEYWORDS = [
    "最小路径",
    "长期艺人 catalog",
    "失败路由",
    "去 AI 味",
]


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def main() -> int:
    errors: list[str] = []

    if not ROADMAP_PATH.exists():
        errors.append(f"roadmap page missing: {ROADMAP_PATH}")
    else:
        text = read(ROADMAP_PATH)

        for tool in REQUIRED_TOOLS:
            if tool not in text:
                errors.append(f"roadmap missing tool reference: {tool}")

        for kw in REQUIRED_KEYWORDS:
            if kw not in text:
                errors.append(f"roadmap missing keyword: {kw}")

    index_path = WIKI / "index.md"
    if index_path.exists():
        index_text = read(index_path)
        if "AI 音乐生产系统总路线图" not in index_text:
            errors.append("wiki/index.md missing reference to system roadmap")
    else:
        errors.append("wiki/index.md missing")

    log_path = WIKI / "log.md"
    if log_path.exists():
        log_text = read(log_path)
        if "AI 音乐生产系统总路线图" not in log_text:
            errors.append("wiki/log.md missing reference to system roadmap")
    else:
        errors.append("wiki/log.md missing")

    map_path = WIKI / "地图" / "音乐知识地图.md"
    if map_path.exists():
        map_text = read(map_path)
        if "AI 音乐生产系统总路线图" not in map_text:
            errors.append("音乐知识地图.md missing reference to system roadmap")

    if errors:
        print("System roadmap verification FAILED:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("System roadmap verification passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
