#!/usr/bin/env python3
"""Verify the AI music prompt compilation and preflight workflow notes."""

from __future__ import annotations

import re
import sys
from pathlib import Path


VAULT = Path("/path/to/obsidian-vault")
WIKI = VAULT / "wiki"

PAGES = {
    "workflow": WIKI / "分析" / "音乐" / "AI 音乐 Prompt 编译与生成前预检工作流.md",
    "source": WIKI / "来源" / "外部资料" / "音乐" / "AI 音乐 Prompt 编译器与生成前预检资料组.md",
    "source_index": WIKI / "来源" / "外部资料" / "音乐" / "index.md",
    "analysis_index": WIKI / "分析" / "音乐" / "index.md",
    "map": WIKI / "地图" / "音乐知识地图.md",
    "root_index": WIKI / "index.md",
    "suno": WIKI / "分析" / "音乐" / "Suno 真人感歌曲生成工作流.md",
    "prompt_experiment": WIKI / "分析" / "音乐" / "AI 音乐 Prompt 实验矩阵与版本收敛工作流.md",
    "templates": WIKI / "分析" / "音乐" / "四语种流行摇滚 AI 音乐 Prompt 模板套件.md",
    "translation": WIKI / "概念" / "音乐" / "AI 音乐提示词如何转译音乐语言.md",
    "single_gate": WIKI / "分析" / "音乐" / "AI 音乐单曲制作总控与阶段闸门工作流.md",
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
    "prompt-compile-brief.md",
    "source-and-rights-routing.md",
    "field-responsibility-map.md",
    "style-field-map.md",
    "lyrics-context-map.md",
    "exclude-negative-aesthetic.md",
    "slider-intent-map.md",
    "persona-voice-model-routing.md",
    "boost-remi-candidate-log.md",
    "constraint-conflict-check.md",
    "field-length-and-specificity-budget.md",
    "prompt-preflight-review.md",
    "experiment-handoff.md",
    "prompt-memory-update.md",
    "Style of Music",
    "Lyrics box",
    "Exclude",
    "Weirdness",
    "Style Influence",
    "Audio Influence",
    "Persona",
    "Voice",
    "Custom Model",
    "Prompt Boost",
    "ReMi",
    "compile approved",
    "rights",
    "catalog",
]

SOURCE_TERMS = [
    "/path/to/suno-prompt-methodology",
    "suno-prompt-template.md",
    "suno-prompt-review-checklist.md",
    "Suno",
    "Custom Mode",
    "own lyrics",
    "Detailed Style Instructions",
    "Better Prompts in Lyrics",
    "Creative Sliders",
    "Weirdness",
    "Style Influence",
    "Audio Influence",
    "Exclude",
    "Creative Prompt Boosting",
    "ReMi",
    "Personas",
    "suno-song-creator-plugin",
    "AI-slop",
    "style-mesh",
    "quality review",
]

REQUIRED_WORKFLOW_LINKS = [
    "[[Suno 真人感歌曲生成工作流]]",
    "[[AI 音乐提示词如何转译音乐语言]]",
    "[[AI 音乐 Prompt 实验矩阵与版本收敛工作流]]",
    "[[AI 音乐参考曲风格 DNA 与合法转译工作流]]",
    "[[四语种流行摇滚 AI 音乐 Prompt 模板套件]]",
    "[[AI 音乐歌词叙事与反陈词滥调工作流]]",
    "[[AI 音乐 Topline Hook 与旋律草稿工作流]]",
    "[[AI 音乐声线身份与演唱表演工作流]]",
    "[[AI 音乐单曲制作总控与阶段闸门工作流]]",
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
        if name != "log" and not under_vault(path):
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

    if compact_len(workflow) < 8500:
        errors.append("workflow page is too thin")
    if compact_len(source) < 4200:
        errors.append("source page is too thin")

    missing_workflow = [term for term in WORKFLOW_TERMS if term not in workflow]
    if missing_workflow:
        errors.append("workflow missing terms: " + ", ".join(missing_workflow))

    missing_source = [term for term in SOURCE_TERMS if term not in source]
    if missing_source:
        errors.append("source missing terms: " + ", ".join(missing_source))

    missing_links = [link for link in REQUIRED_WORKFLOW_LINKS if link not in workflow]
    if missing_links:
        errors.append("workflow missing links: " + ", ".join(missing_links))

    workflow_name = "AI 音乐 Prompt 编译与生成前预检工作流"
    source_name = "AI 音乐 Prompt 编译器与生成前预检资料组"

    for key in [
        "source_index",
        "analysis_index",
        "map",
        "root_index",
        "suno",
        "prompt_experiment",
        "templates",
        "translation",
        "single_gate",
        "log",
    ]:
        if workflow_name not in read(PAGES[key]):
            errors.append(f"{PAGES[key]} missing workflow link/name")

    for key in ["workflow", "source_index", "map", "log"]:
        if source_name not in read(PAGES[key]):
            errors.append(f"{PAGES[key]} missing source link/name")

    single_gate = read(PAGES["single_gate"])
    if "prompt-compile-gate.md" not in single_gate or "prompt-preflight-review.md" not in single_gate:
        errors.append("single production gate missing prompt compile gate integration")

    suno = read(PAGES["suno"])
    if "Prompt 编译与生成前预检" not in suno or "prompt-preflight-review.md" not in suno:
        errors.append("Suno workflow missing prompt compile/preflight integration")

    if errors:
        print("AI music prompt compile preflight workflow verification failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print("AI music prompt compile preflight workflow verification passed.")
    print(f"workflow: {PAGES['workflow']}")
    print(f"source: {PAGES['source']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
