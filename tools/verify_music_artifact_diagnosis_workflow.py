#!/usr/bin/env python3
"""Verify the AI music artifact diagnosis and repair routing notes."""

from __future__ import annotations

import re
import sys
from pathlib import Path


VAULT = Path("/path/to/obsidian-vault")
WIKI = VAULT / "wiki"

PAGES = {
    "workflow": WIKI / "分析" / "音乐" / "AI 音乐 AI味伪影诊断与修复路由工作流.md",
    "source": WIKI / "来源" / "外部资料" / "音乐" / "AI 音乐伪影诊断与检测资料组.md",
    "source_index": WIKI / "来源" / "外部资料" / "音乐" / "index.md",
    "analysis_index": WIKI / "分析" / "音乐" / "index.md",
    "map": WIKI / "地图" / "音乐知识地图.md",
    "root_index": WIKI / "index.md",
    "ai_flavor": WIKI / "概念" / "音乐" / "AI 音乐去 AI 味核心控制面.md",
    "suno_workflow": WIKI / "分析" / "音乐" / "Suno 真人感歌曲生成工作流.md",
    "framework": WIKI / "分析" / "音乐" / "AI 音乐真人感第一性原理审查框架.md",
    "blind_review": WIKI / "分析" / "音乐" / "AI 音乐盲听评审与版本归档工作流.md",
    "postproduction": WIKI / "分析" / "音乐" / "AI 音乐编曲密度与混音后期修作工作流.md",
    "daw": WIKI / "分析" / "音乐" / "AI 音乐 DAW 复刻与真人重录工作流.md",
    "prompt_experiment": WIKI / "分析" / "音乐" / "AI 音乐 Prompt 实验矩阵与版本收敛工作流.md",
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
    "artifact-audit-intent.md",
    "blind-first-listen.md",
    "20-second-red-flag-scan.md",
    "full-song-structure-scan.md",
    "stem-solo-diagnosis.md",
    "vocal-artifact-sheet.md",
    "lyric-prosody-sheet.md",
    "groove-transient-sheet.md",
    "arrangement-density-sheet.md",
    "mix-space-dynamics-sheet.md",
    "artifact-severity-score.md",
    "repair-route-map.md",
    "regression-listen.md",
    "artifact-memory-bank.md",
    "tools/route_music_repairs.py",
    "take-selection-decision.md",
    "歌词语义伪影",
    "Prosody 伪影",
    "Topline 伪影",
    "Groove 伪影",
    "Stem 分离伪影",
    "Catalog/权利伪影",
    "0-3",
    "华语",
    "日语",
    "韩语",
    "英语",
]

SOURCE_TERMS = [
    "Fourier",
    "AI Music Arms Race",
    "AI-Generated Music Detection and its Challenges",
    "SONICS",
    "FAD",
    "webMUSHRA",
    "Demucs",
    "Suno",
    "Exclude",
    "Voices",
    "Song Editor",
    "Replace Section",
    "Studio",
    "/path/to/suno-prompt-methodology",
    "suno-prompt-review-checklist.md",
    "realism-descriptors.md",
    "suno-song-creator-plugin",
    "Bilibili",
    "Douyin",
    "YouTube",
    "Reddit",
]

REQUIRED_WORKFLOW_LINKS = [
    "[[AI 音乐歌词叙事与反陈词滥调工作流]]",
    "[[四语种歌词 Prosody 与 AI 音乐咬字审查表]]",
    "[[AI 音乐 Topline Hook 与旋律草稿工作流]]",
    "[[AI 音乐和声与低音方向工作流]]",
    "[[AI 音乐结构动态与段落转场工作流]]",
    "[[AI 音乐乐器演奏真实感与 Groove Humanization 工作流]]",
    "[[AI 音乐声线身份与演唱表演工作流]]",
    "[[AI 音乐盲听评审与版本归档工作流]]",
    "[[AI 音乐编曲密度与混音后期修作工作流]]",
    "[[AI 音乐 DAW 复刻与真人重录工作流]]",
    "[[AI 音乐权利发布与平台披露工作流]]",
    "[[AI 音乐艺人身份与 Catalog Bible 工作流]]",
    "[[AI 音乐 Prompt 实验矩阵与版本收敛工作流]]",
    "[[Suno 真人感歌曲生成工作流]]",
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

    if compact_len(workflow) < 12000:
        errors.append("workflow page is too thin")
    if compact_len(source) < 7000:
        errors.append("source page is too thin")

    missing_workflow_terms = [term for term in WORKFLOW_TERMS if term not in workflow]
    if missing_workflow_terms:
        errors.append("workflow missing terms: " + ", ".join(missing_workflow_terms))

    missing_source_terms = [term for term in SOURCE_TERMS if term not in source]
    if missing_source_terms:
        errors.append("source missing terms: " + ", ".join(missing_source_terms))

    missing_links = [link for link in REQUIRED_WORKFLOW_LINKS if link not in workflow]
    if missing_links:
        errors.append("workflow missing routing links: " + ", ".join(missing_links))

    workflow_name = "AI 音乐 AI味伪影诊断与修复路由工作流"
    source_name = "AI 音乐伪影诊断与检测资料组"

    for key in [
        "source_index",
        "analysis_index",
        "map",
        "root_index",
        "ai_flavor",
        "suno_workflow",
        "framework",
        "blind_review",
        "postproduction",
        "daw",
        "prompt_experiment",
        "log",
    ]:
        if workflow_name not in read(PAGES[key]):
            errors.append(f"{PAGES[key]} missing workflow link/name")

    for key in ["workflow", "source_index", "map", "log"]:
        if source_name not in read(PAGES[key]):
            errors.append(f"{PAGES[key]} missing source link/name")

    if "Fourier Explanation of AI-music Artifacts" not in source:
        errors.append("source missing Fourier artifact paper title")
    if "检测器" not in workflow or "detector" not in workflow:
        errors.append("workflow must distinguish detectors from music readiness")
    if "release-candidate" not in workflow:
        errors.append("workflow missing release-candidate gate")

    if errors:
        print("AI music artifact diagnosis workflow verification failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print("AI music artifact diagnosis workflow verification passed.")
    print(f"workflow: {PAGES['workflow']}")
    print(f"source: {PAGES['source']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
