#!/usr/bin/env python3
"""Verify the AI music harmony and bass-direction workflow notes."""

from __future__ import annotations

import re
import sys
from pathlib import Path


VAULT = Path("/path/to/obsidian-vault")
WIKI = VAULT / "wiki"

PAGES = {
    "workflow": WIKI / "分析" / "音乐" / "AI 音乐和声与低音方向工作流.md",
    "source": WIKI / "来源" / "外部资料" / "音乐" / "AI 音乐和声与低音方向资料组.md",
    "harmony": WIKI / "概念" / "音乐" / "和声功能与级数.md",
    "pop_harmony": WIKI / "概念" / "音乐" / "流行和声进行.md",
    "rock_harmony": WIKI / "概念" / "音乐" / "摇滚和声语言.md",
    "ai_flavor": WIKI / "概念" / "音乐" / "AI 音乐去 AI 味核心控制面.md",
    "suno_workflow": WIKI / "分析" / "音乐" / "Suno 真人感歌曲生成工作流.md",
    "framework": WIKI / "分析" / "音乐" / "AI 音乐真人感第一性原理审查框架.md",
    "topline": WIKI / "分析" / "音乐" / "AI 音乐 Topline Hook 与旋律草稿工作流.md",
    "groove": WIKI / "分析" / "音乐" / "AI 音乐乐器演奏真实感与 Groove Humanization 工作流.md",
    "postproduction": WIKI / "分析" / "音乐" / "AI 音乐编曲密度与混音后期修作工作流.md",
    "templates": WIKI / "分析" / "音乐" / "四语种流行摇滚 AI 音乐 Prompt 模板套件.md",
    "concept_index": WIKI / "概念" / "音乐" / "index.md",
    "analysis_index": WIKI / "分析" / "音乐" / "index.md",
    "source_index": WIKI / "来源" / "外部资料" / "音乐" / "index.md",
    "map": WIKI / "地图" / "音乐知识地图.md",
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
    "harmony-brief.md",
    "key-mode-color",
    "progression-map.md",
    "bassline-map.md",
    "harmonic-rhythm-map.md",
    "cadence-and-bridge-plan.md",
    "harmony-repair-log.md",
    "chord progression",
    "bassline",
    "harmonic rhythm",
    "cadence",
    "bridge turn",
    "chorus arrival",
    "topline/harmony",
    "secondary dominant",
    "modal interchange",
    "pedal",
    "ostinato",
    "Suno",
    "Style of Music",
    "Lyrics tags",
    "Exclude",
    "blind review",
    "Audio Upload",
    "DAW",
    "四语种",
]

SOURCE_TERMS = [
    "local Suno prompt methodology",
    "Berklee",
    "Songwriting: Harmony",
    "power progressions",
    "cadences",
    "modulation",
    "Harmony 2",
    "secondary",
    "modal interchange",
    "Harmony 4",
    "pedal point",
    "ostinato",
    "Ableton",
    "basslines",
    "Detailed Style Instructions",
    "warm basslines",
    "GitHub",
    "HookTheory",
    "harmonic rhythm",
    "section contrast",
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
    frontmatter = text.split("---", 2)[1]
    return f"type: {expected}" in frontmatter


def main() -> int:
    errors: list[str] = []

    for path in GUARDS:
        if not path.exists():
            errors.append(f"missing guard: {path}")

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
        errors.append("workflow page must have type: analysis")
    if not has_type(source, "source"):
        errors.append("source page must have type: source")

    if compact_len(workflow) < 8000:
        errors.append("workflow page is too thin")
    if compact_len(source) < 4500:
        errors.append("source page is too thin")

    missing_workflow = [term for term in WORKFLOW_TERMS if term not in workflow]
    if missing_workflow:
        errors.append("workflow missing terms: " + ", ".join(missing_workflow))

    missing_source = [term for term in SOURCE_TERMS if term not in source]
    if missing_source:
        errors.append("source missing terms: " + ", ".join(missing_source))

    workflow_link = "[[AI 音乐和声与低音方向工作流]]"
    source_link = "[[AI 音乐和声与低音方向资料组]]"

    for key in [
        "harmony",
        "pop_harmony",
        "rock_harmony",
        "ai_flavor",
        "suno_workflow",
        "framework",
        "topline",
        "groove",
        "postproduction",
        "templates",
        "concept_index",
        "analysis_index",
        "map",
    ]:
        if workflow_link not in read(PAGES[key]):
            errors.append(f"{PAGES[key]} missing workflow link")

    root_index = read(PAGES["root_index"])
    if workflow_link not in root_index and "AI 音乐和声与低音方向工作流" not in root_index:
        errors.append(f"{PAGES['root_index']} missing workflow link")

    for key in [
        "workflow",
        "harmony",
        "pop_harmony",
        "rock_harmony",
        "ai_flavor",
        "suno_workflow",
        "framework",
        "topline",
        "groove",
        "postproduction",
        "templates",
        "concept_index",
        "analysis_index",
        "source_index",
        "map",
    ]:
        if source_link not in read(PAGES[key]):
            errors.append(f"{PAGES[key]} missing source link")

    log = read(PAGES["log"])
    if "AI 音乐和声与低音方向工作流" not in log:
        errors.append("wiki/log.md missing harmony/bass workflow entry")

    if errors:
        print("AI music harmony/bass workflow verification failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print("AI music harmony/bass workflow verification passed.")
    print(f"workflow: {PAGES['workflow']}")
    print(f"source: {PAGES['source']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
