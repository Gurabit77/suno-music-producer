#!/usr/bin/env python3
"""Verify all representative artist/band pages have AI-music analysis structure."""

from __future__ import annotations

import re
import sys
from pathlib import Path


VAULT = Path("/path/to/obsidian-vault")
ARTIST_DIR = VAULT / "wiki" / "实体" / "音乐人"
INDEX = ARTIST_DIR / "index.md"
LOG = VAULT / "wiki" / "log.md"

REQUIRED_TERMS = [
    "## 代表作品与逐曲分析",
    "## 音乐语言总览",
    "### 和声",
    "### 旋律",
    "## 人声、咬字、声线或",
    "## 编曲与制作特征",
    "## 可学习的写作手法",
    "## 对 AI音乐 创作的可转译提示词语言",
    "## Suno 实作提醒",
    "## 盲听评审重点",
    "## 可信度与边界",
    "## 相关来源",
]

FORBIDDEN_TEMPLATE_PHRASES = [
    "学习重点不是模仿表面音色",
    "初听顺序：先听最大众传播的一首",
    "作品可从五个层次听",
    "可从五个层次听：鼓/打击乐、低音、和声乐器、旋律 hook、人声制作",
]

REQUIRED_KEY_ARTISTS = [
    "米津玄师",
    "YOASOBI",
    "Ado",
    "King Gnu",
    "周杰伦",
    "BTS",
    "NewJeans",
    "Taylor Swift",
    "Radiohead",
    "五月天",
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
    return "type: entity" in frontmatter and "tags:" in frontmatter and "sources:" in frontmatter


def main() -> int:
    errors: list[str] = []

    if not ARTIST_DIR.exists():
        print(f"missing artist directory: {ARTIST_DIR}", file=sys.stderr)
        return 1

    pages = sorted(p for p in ARTIST_DIR.glob("*.md") if p.name != "index.md")
    if len(pages) < 60:
        errors.append(f"too few artist pages: {len(pages)}")

    index_text = INDEX.read_text(encoding="utf-8") if INDEX.exists() else ""
    for artist in REQUIRED_KEY_ARTISTS:
        if f"[[{artist}]]" not in index_text:
            errors.append(f"artist index missing key artist: {artist}")

    for path in pages:
        text = path.read_text(encoding="utf-8")
        name = path.stem

        if not has_entity_frontmatter(text):
            errors.append(f"{name}: missing entity frontmatter/sources")

        if compact_len(text) < 2700:
            errors.append(f"{name}: page too thin ({compact_len(text)})")

        song_headings = text.count("### 《")
        if song_headings < 3:
            errors.append(f"{name}: fewer than 3 representative song headings")

        missing = [term for term in REQUIRED_TERMS if term not in text]
        if missing:
            errors.append(f"{name}: missing terms: {', '.join(missing)}")

        if "AI prompt 转译" not in text:
            errors.append(f"{name}: missing per-song AI prompt translation")

        if "Exclude" not in text and "no " not in text:
            errors.append(f"{name}: missing negative prompt / exclusion guidance")

        forbidden = [phrase for phrase in FORBIDDEN_TEMPLATE_PHRASES if phrase in text]
        if forbidden:
            errors.append(f"{name}: still has generic template phrases: {', '.join(forbidden)}")

    log_text = LOG.read_text(encoding="utf-8") if LOG.exists() else ""
    if "标杆艺人逐曲分析样板页" not in log_text:
        errors.append("wiki/log.md missing original artist sample batch entry")

    if errors:
        print("Music artist analysis quality gate FAILED:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print("Music artist analysis quality gate passed.")
    print(f"- artist pages: {len(pages)}")
    print(f"- vault: {VAULT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
