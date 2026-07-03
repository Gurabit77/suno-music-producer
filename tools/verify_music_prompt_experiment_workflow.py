#!/usr/bin/env python3
"""Verify the AI music prompt experiment matrix and version convergence notes."""

from __future__ import annotations

import re
import sys
from pathlib import Path


VAULT = Path("/path/to/obsidian-vault")
WIKI = VAULT / "wiki"

PAGES = {
    "workflow": WIKI / "分析" / "音乐" / "AI 音乐 Prompt 实验矩阵与版本收敛工作流.md",
    "source": WIKI / "来源" / "外部资料" / "音乐" / "AI 音乐 Prompt 实验矩阵与版本收敛资料组.md",
    "source_index": WIKI / "来源" / "外部资料" / "音乐" / "index.md",
    "analysis_index": WIKI / "分析" / "音乐" / "index.md",
    "map": WIKI / "地图" / "音乐知识地图.md",
    "root_index": WIKI / "index.md",
    "suno_workflow": WIKI / "分析" / "音乐" / "Suno 真人感歌曲生成工作流.md",
    "blind_review": WIKI / "分析" / "音乐" / "AI 音乐盲听评审与版本归档工作流.md",
    "ai_flavor": WIKI / "概念" / "音乐" / "AI 音乐去 AI 味核心控制面.md",
    "framework": WIKI / "分析" / "音乐" / "AI 音乐真人感第一性原理审查框架.md",
    "catalog": WIKI / "分析" / "音乐" / "AI 音乐艺人身份与 Catalog Bible 工作流.md",
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
    "experiment-intent.md",
    "brief-freeze.md",
    "variable-inventory.md",
    "prompt-candidate-set.md",
    "batch-generation-plan.md",
    "slider-ablation-matrix.md",
    "lyrics-context-variant.md",
    "exclude-failure-map.md",
    "persona-model-routing.md",
    "take-ledger.md",
    "blind-review-sampling.md",
    "prompt-diff-and-attribution.md",
    "repair-decision-tree.md",
    "prompt-memory-bank.md",
    "catalog-feedback-link.md",
    "Weirdness",
    "Style Influence",
    "Audio Influence",
    "Exclude",
    "Creative Prompt Boosting",
    "ReMi",
    "Persona",
    "Lyrics box",
    "A/B",
    "alignment",
    "preference",
    "AI flavor",
    "single variable",
]

SOURCE_TERMS = [
    "Suno",
    "Detailed Style Instructions",
    "Better Prompts in Lyrics",
    "Creative Prompt Boosting",
    "Exclude",
    "Creative Sliders",
    "Weirdness",
    "Style Influence",
    "Audio Influence",
    "Personas",
    "ReMi",
    "own lyrics",
    "/path/to/suno-prompt-methodology",
    "suno-prompt-template.md",
    "suno-prompt-review-checklist.md",
    "suno-song-creator-plugin",
    "AI-slop",
    "quality-reviewer",
    "genre-evaluation-matrix",
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

    if compact_len(workflow) < 10500:
        errors.append("workflow page is too thin")
    if compact_len(source) < 6500:
        errors.append("source page is too thin")

    missing_workflow = [term for term in WORKFLOW_TERMS if term not in workflow]
    if missing_workflow:
        errors.append("workflow missing terms: " + ", ".join(missing_workflow))

    missing_source = [term for term in SOURCE_TERMS if term not in source]
    if missing_source:
        errors.append("source missing terms: " + ", ".join(missing_source))

    workflow_link = "[[AI 音乐 Prompt 实验矩阵与版本收敛工作流]]"
    source_link = "[[AI 音乐 Prompt 实验矩阵与版本收敛资料组]]"

    workflow_link_pages = [
        "source_index",
        "analysis_index",
        "map",
        "root_index",
        "suno_workflow",
        "blind_review",
        "ai_flavor",
        "framework",
        "catalog",
    ]
    for key in workflow_link_pages:
        text = read(PAGES[key])
        if workflow_link not in text and "AI 音乐 Prompt 实验矩阵与版本收敛工作流" not in text:
            errors.append(f"{PAGES[key]} missing workflow link")

    source_link_pages = [
        "workflow",
        "source_index",
        "analysis_index",
        "map",
        "suno_workflow",
        "blind_review",
        "ai_flavor",
        "framework",
        "catalog",
    ]
    for key in source_link_pages:
        if source_link not in read(PAGES[key]):
            errors.append(f"{PAGES[key]} missing source link")

    log = read(PAGES["log"])
    if "AI 音乐 Prompt 实验矩阵与版本收敛工作流" not in log:
        errors.append("wiki/log.md missing prompt experiment workflow entry")

    if errors:
        print("AI music prompt experiment workflow verification failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print("AI music prompt experiment workflow verification passed.")
    print(f"workflow: {PAGES['workflow']}")
    print(f"source: {PAGES['source']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
