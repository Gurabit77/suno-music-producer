#!/usr/bin/env python3
"""Verify the multilingual pop/rock AI music prompt template suite."""

from __future__ import annotations

import re
import sys
from pathlib import Path


VAULT = Path("/path/to/obsidian-vault")
WIKI = VAULT / "wiki"

PAGES = {
    "template": WIKI / "分析" / "音乐" / "四语种流行摇滚 AI 音乐 Prompt 模板套件.md",
    "analysis_index": WIKI / "分析" / "音乐" / "index.md",
    "map": WIKI / "地图" / "音乐知识地图.md",
    "root_index": WIKI / "index.md",
    "pop_compare": WIKI / "分析" / "音乐" / "四语种流行音乐对比.md",
    "rock_compare": WIKI / "分析" / "音乐" / "四语种摇滚音乐对比.md",
    "suno_workflow": WIKI / "分析" / "音乐" / "Suno 真人感歌曲生成工作流.md",
    "log": WIKI / "log.md",
}

GUARDS = [
    VAULT / "CLAUDE.md",
    VAULT / "CODEX.md",
    WIKI / "系统" / "自动记录价值闸门.md",
    WIKI / "系统" / "知识新增工作流.md",
    WIKI / "index.md",
]

TEMPLATE_HEADINGS = [
    "## 1. 日本流行模板",
    "## 2. 华语流行模板",
    "## 3. 韩语流行模板",
    "## 4. 英语流行模板",
    "## 5. 日本摇滚模板",
    "## 6. 华语摇滚模板",
    "## 7. 韩语摇滚模板",
    "## 8. 英语摇滚模板",
]

REQUIRED_TERMS = [
    "Style of Music",
    "Lyrics tags",
    "Exclude",
    "盲听重点",
    "Sliders 起点",
    "Prompt 包最小交付格式",
    "AI 音乐盲听评审与版本归档工作流",
    "Suno 真人感歌曲生成工作流",
    "Style Influence",
    "Weirdness",
    "Audio Influence",
    "版权边界",
    "日语音节密度",
    "中文声调",
    "韩英 hook",
    "英语口语重音",
]

STYLE_KEYWORDS = [
    "Japanese pop",
    "Mandarin pop ballad",
    "K-pop",
    "English pop",
    "Japanese rock",
    "Mandarin indie rock",
    "Korean pop-rock band",
    "English alternative rock",
]


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def compact_len(text: str) -> int:
    return len(re.sub(r"\s+", "", text))


def under_vault(path: Path) -> bool:
    resolved = path.resolve()
    vault = VAULT.resolve()
    return vault in [resolved, *resolved.parents]


def has_frontmatter_type(text: str, expected: str) -> bool:
    if not text.startswith("---\n"):
        return False
    frontmatter = text.split("---", 2)[1]
    return f"type: {expected}" in frontmatter


def main() -> int:
    errors: list[str] = []

    for path in GUARDS:
        if not path.exists():
            errors.append(f"missing guard file: {path}")

    for name, path in PAGES.items():
        if not under_vault(path):
            errors.append(f"path outside vault ({name}): {path}")
        if not path.exists():
            errors.append(f"missing page ({name}): {path}")

    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1

    template = read(PAGES["template"])
    if not has_frontmatter_type(template, "analysis"):
        errors.append("template page must have type: analysis")

    if compact_len(template) < 7000:
        errors.append("template page is too thin for eight executable templates")

    missing_headings = [heading for heading in TEMPLATE_HEADINGS if heading not in template]
    if missing_headings:
        errors.append("missing template headings: " + ", ".join(missing_headings))

    missing_terms = [term for term in REQUIRED_TERMS if term not in template]
    if missing_terms:
        errors.append("missing required terms: " + ", ".join(missing_terms))

    missing_styles = [term for term in STYLE_KEYWORDS if term not in template]
    if missing_styles:
        errors.append("missing style prompt anchors: " + ", ".join(missing_styles))

    # Each template should carry all operational sections.
    blocks = re.split(r"\n## \d+\. ", template)
    template_blocks = blocks[1:9]
    if len(template_blocks) != 8:
        errors.append(f"expected 8 template blocks, found {len(template_blocks)}")
    else:
        for idx, block in enumerate(template_blocks, start=1):
            for section in ["### Style of Music", "### Lyrics tags", "### Exclude", "### 盲听重点"]:
                if section not in block:
                    errors.append(f"template {idx} missing {section}")

    link = "[[四语种流行摇滚 AI 音乐 Prompt 模板套件]]"
    for key in ["analysis_index", "map", "pop_compare", "rock_compare", "suno_workflow"]:
        if link not in read(PAGES[key]):
            errors.append(f"{PAGES[key]} missing template backlink")

    root_text = read(PAGES["root_index"])
    if "四语种流行摇滚 AI 音乐 Prompt 模板套件" not in root_text:
        errors.append("wiki/index.md missing template suite entry")

    log = read(PAGES["log"])
    if "四语种流行摇滚 AI 音乐 Prompt 模板套件" not in log:
        errors.append("wiki/log.md missing template suite entry")

    if errors:
        print("Multilingual prompt template verification failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print("Multilingual pop/rock AI music prompt template verification passed.")
    print(f"template: {PAGES['template']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
