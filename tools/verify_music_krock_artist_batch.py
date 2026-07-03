#!/usr/bin/env python3
"""Verify the deepened Korean rock band batch for the music wiki."""

from __future__ import annotations

import re
import sys
from pathlib import Path


VAULT = Path("/path/to/obsidian-vault")
ARTIST_DIR = VAULT / "wiki/实体/音乐人"

KROCK_BATCH = [
    "DAY6.md",
    "FTISLAND.md",
    "CNBLUE.md",
    "JANNABI.md",
    "The Rose.md",
    "N.Flying.md",
    "Xdinary Heroes.md",
    "LUCY.md",
]

REQUIRED_TERMS = [
    "代表作品与逐曲分析",
    "音乐语言总览",
    "和声",
    "旋律",
    "节奏",
    "编曲",
    "制作",
    "AI音乐",
    "Suno 实作提醒",
    "盲听评审重点",
    "可信度与边界",
    "相关来源",
]

GENERIC_PHRASES = [
    "学习重点不是模仿表面音色",
    "初听顺序：先听最大众传播的一首",
    "作品可从五个层次听",
    "可从五个层次听：鼓/打击乐、低音、和声乐器、旋律 hook、人声制作",
    "不要只写",
]


def compact_len(text: str) -> int:
    return len(re.sub(r"\s+", "", text))


def has_entity_frontmatter(text: str) -> bool:
    if not text.startswith("---\n"):
        return False
    end = text.find("\n---", 4)
    if end < 0:
        return False
    frontmatter = text[: end + 4]
    return all(key in frontmatter for key in ["title:", "type: entity", "tags:", "created:", "updated:", "sources:"])


def main() -> int:
    errors: list[str] = []

    for name in KROCK_BATCH:
        path = ARTIST_DIR / name
        if not path.exists():
            errors.append(f"missing page: {path}")
            continue
        text = path.read_text(encoding="utf-8")
        length = compact_len(text)
        markers = text.count("### 《") + text.count("#### 《")
        if not has_entity_frontmatter(text):
            errors.append(f"{name} missing entity frontmatter")
        if length < 2800:
            errors.append(f"{name} too thin: {length}")
        if text.count("《") < 3:
            errors.append(f"{name} has fewer than 3 named works")
        if markers < 3:
            errors.append(f"{name} has fewer than 3 song-analysis headings: {markers}")
        missing = [term for term in REQUIRED_TERMS if term not in text]
        if missing:
            errors.append(f"{name} missing terms: {', '.join(missing)}")
        generic = [phrase for phrase in GENERIC_PHRASES if phrase in text]
        if generic:
            errors.append(f"{name} still has template phrases: {', '.join(generic)}")

    log = VAULT / "wiki/log.md"
    if not log.exists() or "韩语摇滚乐队逐曲分析批次" not in log.read_text(encoding="utf-8"):
        errors.append("wiki/log.md missing Korean rock band batch entry")

    if errors:
        print("Korean rock band batch verification FAILED:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Korean rock band batch verification passed.")
    for name in KROCK_BATCH:
        text = (ARTIST_DIR / name).read_text(encoding="utf-8")
        markers = text.count("### 《") + text.count("#### 《")
        print(f"- {name}: {compact_len(text)} chars, {markers} song-analysis headings")
    print(f"- vault: {VAULT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
