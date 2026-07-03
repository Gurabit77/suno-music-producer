#!/usr/bin/env python3
"""Verify the four-language lyric prosody and diction workflow notes."""

from __future__ import annotations

import re
import sys
from pathlib import Path


VAULT = Path("/path/to/obsidian-vault")
WIKI = VAULT / "wiki"

PAGES = {
    "workflow": WIKI / "分析" / "音乐" / "四语种歌词 Prosody 与 AI 音乐咬字审查表.md",
    "source": WIKI / "来源" / "外部资料" / "音乐" / "歌词 Prosody 与旋律对齐资料组.md",
    "lyrics": WIKI / "概念" / "音乐" / "歌词写作.md",
    "vocal": WIKI / "概念" / "音乐" / "人声、声部与咬字.md",
    "translation": WIKI / "概念" / "音乐" / "AI 音乐提示词如何转译音乐语言.md",
    "template": WIKI / "分析" / "音乐" / "四语种流行摇滚 AI 音乐 Prompt 模板套件.md",
    "framework": WIKI / "分析" / "音乐" / "AI 音乐真人感第一性原理审查框架.md",
    "review": WIKI / "分析" / "音乐" / "AI 音乐盲听评审与版本归档工作流.md",
    "map": WIKI / "地图" / "音乐知识地图.md",
    "concept_index": WIKI / "概念" / "音乐" / "index.md",
    "analysis_index": WIKI / "分析" / "音乐" / "index.md",
    "source_index": WIKI / "来源" / "外部资料" / "音乐" / "index.md",
    "root_index": WIKI / "index.md",
    "log": WIKI / "log.md",
}

GUARDS = [
    VAULT / "CLAUDE.md",
    VAULT / "CODEX.md",
    WIKI / "系统" / "自动记录价值闸门.md",
    WIKI / "系统" / "知识新增工作流.md",
    WIKI / "index.md",
]

WORKFLOW_TERMS = [
    "Prosody",
    "华语歌词审查",
    "日语歌词审查",
    "韩语歌词审查",
    "英语歌词审查",
    "中文声调",
    "日语音节密度",
    "韩英 hook",
    "英语口语重音",
    "natural Mandarin phrasing",
    "title phrase on long vowel",
    "short Korean-English hook",
    "stressed words on strong beats",
    "Lyrics tags",
    "Exclude",
    "盲听问题",
    "最小交付模板",
]

SOURCE_TERMS = [
    "Berklee",
    "Pat Pattison",
    "ReLyMe",
    "tone",
    "rhythm",
    "structure",
    "Tone-melody",
    "声调语言",
    "automatic song translation",
    "待验证",
]


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def compact_len(text: str) -> int:
    return len(re.sub(r"\s+", "", text))


def under_vault(path: Path) -> bool:
    resolved = path.resolve()
    vault = VAULT.resolve()
    return vault in [resolved, *resolved.parents]


def has_type(text: str, expected: str) -> bool:
    if not text.startswith("---\n"):
        return False
    return f"type: {expected}" in text.split("---", 2)[1]


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

    workflow = read(PAGES["workflow"])
    source = read(PAGES["source"])

    if not has_type(workflow, "analysis"):
        errors.append("prosody workflow page must have type: analysis")
    if not has_type(source, "source"):
        errors.append("prosody source page must have type: source")

    if compact_len(workflow) < 5200:
        errors.append("prosody workflow page is too thin")
    if compact_len(source) < 2300:
        errors.append("prosody source page is too thin")

    missing_workflow = [term for term in WORKFLOW_TERMS if term not in workflow]
    if missing_workflow:
        errors.append("workflow missing terms: " + ", ".join(missing_workflow))

    missing_source = [term for term in SOURCE_TERMS if term not in source]
    if missing_source:
        errors.append("source missing terms: " + ", ".join(missing_source))

    workflow_link = "[[四语种歌词 Prosody 与 AI 音乐咬字审查表]]"
    source_link = "[[歌词 Prosody 与旋律对齐资料组]]"
    for key in [
        "lyrics",
        "vocal",
        "translation",
        "template",
        "framework",
        "review",
        "map",
        "concept_index",
        "analysis_index",
    ]:
        if workflow_link not in read(PAGES[key]):
            errors.append(f"{PAGES[key]} missing prosody workflow link")

    for key in ["lyrics", "vocal", "source_index", "map"]:
        if source_link not in read(PAGES[key]):
            errors.append(f"{PAGES[key]} missing prosody source link")

    if "四语种歌词 Prosody 与 AI 音乐咬字审查表" not in read(PAGES["root_index"]):
        errors.append("wiki/index.md missing prosody workflow entry")

    if "四语种歌词 Prosody 与 AI 音乐咬字审查" not in read(PAGES["log"]):
        errors.append("wiki/log.md missing prosody workflow entry")

    if errors:
        print("Prosody workflow verification failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print("Four-language lyric prosody workflow verification passed.")
    print(f"workflow: {PAGES['workflow']}")
    print(f"source: {PAGES['source']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
