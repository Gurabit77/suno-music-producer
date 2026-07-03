#!/usr/bin/env python3
"""Verify the core music theory concept pages are substantial and AI-music-ready."""

from __future__ import annotations

import re
import sys
from pathlib import Path


VAULT = Path("/path/to/obsidian-vault")
CONCEPT_DIR = VAULT / "wiki/概念/音乐"

CORE_PAGES = [
    "乐理基础总览.md",
    "音程与音阶.md",
    "调式与调性.md",
    "和声功能与级数.md",
    "流行和声进行.md",
    "摇滚和声语言.md",
    "节奏、拍号与律动.md",
    "旋律写作.md",
    "曲式结构.md",
    "配器与编曲基础.md",
    "人声、声部与咬字.md",
    "歌词写作.md",
    "声音设计与录音制作基础.md",
    "AI 音乐提示词如何转译音乐语言.md",
]

REQUIRED_TERMS = [
    "AI 音乐",
    "prompt",
    "Prompt",
    "Suno",
    "去 AI 味",
    "真人感",
    "律动",
    "人声",
    "编曲",
    "制作",
    "验收",
]


def compact_len(text: str) -> int:
    return len(re.sub(r"\s+", "", text))


def main() -> int:
    errors: list[str] = []
    combined: list[str] = []

    for name in CORE_PAGES:
        path = CONCEPT_DIR / name
        if not path.exists():
            errors.append(f"missing page: {path}")
            continue
        text = path.read_text(encoding="utf-8")
        combined.append(text)
        length = compact_len(text)
        if length < 1600:
            errors.append(f"{name} too thin: {length}")
        for heading in ["## 定义", "## 第一性原理", "## 面向 AI 音乐"]:
            if heading not in text:
                errors.append(f"{name} missing heading: {heading}")
        if "[[" not in text:
            errors.append(f"{name} has no wikilinks")

    all_text = "\n".join(combined)
    for term in REQUIRED_TERMS:
        if term not in all_text:
            errors.append(f"missing core term across theory pages: {term}")

    index = CONCEPT_DIR / "index.md"
    if index.exists():
        index_text = index.read_text(encoding="utf-8")
        missing_index = [name[:-3] for name in CORE_PAGES if name[:-3] not in index_text]
        if missing_index:
            errors.append("concept index missing pages: " + ", ".join(missing_index))
    else:
        errors.append(f"missing concept index: {index}")

    log = VAULT / "wiki/log.md"
    if not log.exists() or "音乐核心乐理页去 AI 味加厚" not in log.read_text(encoding="utf-8"):
        errors.append("wiki/log.md missing theory deepening entry")

    if errors:
        print("Music theory foundation verification FAILED:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Music theory foundation verification passed.")
    for name in CORE_PAGES:
        text = (CONCEPT_DIR / name).read_text(encoding="utf-8")
        print(f"- {name}: {compact_len(text)}")
    print(f"- vault: {VAULT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
