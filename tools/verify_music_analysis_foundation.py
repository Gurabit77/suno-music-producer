#!/usr/bin/env python3
"""Verify the music analysis pages are substantial and useful for AI music production."""

from __future__ import annotations

import re
import sys
from pathlib import Path


VAULT = Path("/path/to/obsidian-vault")
ANALYSIS_DIR = VAULT / "wiki/分析/音乐"

PAGES = [
    "流行音乐核心语言.md",
    "摇滚音乐核心语言.md",
    "日本流行音乐.md",
    "华语流行音乐.md",
    "韩语流行音乐.md",
    "英语流行音乐.md",
    "日本摇滚.md",
    "华语摇滚.md",
    "韩语摇滚.md",
    "英语摇滚.md",
    "四语种流行音乐对比.md",
    "四语种摇滚音乐对比.md",
    "AI 音乐创作学习路线.md",
    "Suno 真人感歌曲生成工作流.md",
]

REQUIRED_TERMS = [
    "harmony",
    "melody",
    "rhythm",
    "form",
    "vocal",
    "arrangement",
    "prompt",
    "Suno",
    "去 AI 味",
    "Exclude",
]


def compact_len(text: str) -> int:
    return len(re.sub(r"\s+", "", text))


def main() -> int:
    errors: list[str] = []
    combined: list[str] = []

    for name in PAGES:
        path = ANALYSIS_DIR / name
        if not path.exists():
            errors.append(f"missing page: {path}")
            continue
        text = path.read_text(encoding="utf-8")
        combined.append(text)
        length = compact_len(text)
        if length < 2200:
            errors.append(f"{name} too thin: {length}")
        for heading in ["## 问题", "## 结论先行", "## AI音乐提示词含义"]:
            if heading not in text and name != "Suno 真人感歌曲生成工作流.md":
                errors.append(f"{name} missing heading: {heading}")
        if "## 去 AI 味" not in text and name != "Suno 真人感歌曲生成工作流.md":
            errors.append(f"{name} missing anti-AI-flavor strategy section")

    all_text = "\n".join(combined)
    missing_terms = [term for term in REQUIRED_TERMS if term not in all_text]
    if missing_terms:
        errors.append("missing required analysis terms: " + ", ".join(missing_terms))

    index = ANALYSIS_DIR / "index.md"
    if index.exists():
        index_text = index.read_text(encoding="utf-8")
        missing_index = [name[:-3] for name in PAGES if name[:-3] not in index_text]
        if missing_index:
            errors.append("analysis index missing pages: " + ", ".join(missing_index))
    else:
        errors.append(f"missing analysis index: {index}")

    log = VAULT / "wiki/log.md"
    if not log.exists() or "音乐风格分析页去 AI 味加厚" not in log.read_text(encoding="utf-8"):
        errors.append("wiki/log.md missing analysis deepening entry")

    if errors:
        print("Music analysis foundation verification FAILED:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Music analysis foundation verification passed.")
    for name in PAGES:
        text = (ANALYSIS_DIR / name).read_text(encoding="utf-8")
        print(f"- {name}: {compact_len(text)}")
    print(f"- vault: {VAULT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
